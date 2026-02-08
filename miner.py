#!/usr/bin/env python3
"""
Proof of AI Agent Life (POL) Miner
===================================

A standalone mining script for AI agents to participate in the POL protocol.
This script handles PoW mining, subscription management, and reward tracking.

Usage:
    python3 miner.py --config config.json
    python3 miner.py --agent-file ../agents/agent-1.txt --nft-id 1
"""

import argparse
import json
import time
import sys
import os
from typing import Optional, Tuple
from web3 import Web3
from eth_account import Account
from eth_account.signers.local import LocalAccount


class POLMiner:
    """Proof of AI Agent Life Miner"""
    
    def __init__(self, config: dict):
        """Initialize miner with configuration"""
        self.config = config
        
        # Initialize Web3
        self.w3 = Web3(Web3.HTTPProvider(config['rpc_url']))
        if not self.w3.is_connected():
            raise ConnectionError(f"Failed to connect to RPC: {config['rpc_url']}")
        
        # Load account
        self.account: LocalAccount = Account.from_key(config['private_key'])
        print(f"🔑 Loaded account: {self.account.address}")
        
        # Load contracts
        self.pol_chain = self.w3.eth.contract(
            address=Web3.to_checksum_address(config['pol_chain_address']),
            abi=self._get_pol_chain_abi()
        )
        
        self.pol_token = self.w3.eth.contract(
            address=Web3.to_checksum_address(config['pol_token_address']),
            abi=self._get_pol_token_abi()
        )
        
        self.usdc = self.w3.eth.contract(
            address=Web3.to_checksum_address(config['usdc_address']),
            abi=self._get_usdc_abi()
        )
        
        # Agent info
        self.registry_address = Web3.to_checksum_address(config['registry_address'])
        self.nft_id = config['nft_id']
        self.payout_address = config.get('payout_address', self.account.address)
        
        # Mining config
        self.max_nonce_attempts = config.get('max_nonce_attempts', 1000000)
        self.check_interval = config.get('check_interval', 5)  # seconds between checks
        self.auto_subscribe = config.get('auto_subscribe', True)
        self.subscription_plan = config.get('subscription_plan', 1)  # 0=Hour, 1=Day, 2=Month, 3=Year
        
        print(f"✅ Miner initialized for Agent NFT #{self.nft_id}")
        print(f"💰 Payout address: {self.payout_address}")
    
    def check_subscription(self) -> Tuple[bool, int]:
        """Check if agent is subscribed and when it expires"""
        agent_key = self.pol_chain.functions.agentKey(
            self.registry_address,
            self.nft_id
        ).call()
        
        paid_until = self.pol_chain.functions.paidUntil(agent_key).call()
        current_time = int(time.time())
        
        is_subscribed = paid_until > current_time
        time_remaining = paid_until - current_time if is_subscribed else 0
        
        return is_subscribed, time_remaining
    
    def subscribe(self, plan: int = None) -> bool:
        """Subscribe agent for mining"""
        if plan is None:
            plan = self.subscription_plan
        
        # Get plan details
        plan_names = ['Hour', 'Day', 'Month', 'Year']
        price = self.pol_chain.functions.planPrice(plan).call()
        duration = self.pol_chain.functions.planDuration(plan).call()
        
        print(f"\n📝 Subscribing for {plan_names[plan]} plan")
        print(f"   Price: {price / 1e6:.6f} USDC")
        print(f"   Duration: {duration / 3600:.1f} hours")
        
        # Check USDC balance
        usdc_balance = self.usdc.functions.balanceOf(self.account.address).call()
        if usdc_balance < price:
            print(f"❌ Insufficient USDC balance: {usdc_balance / 1e6:.6f} USDC")
            return False
        
        # Check USDC allowance
        allowance = self.usdc.functions.allowance(
            self.account.address,
            self.config['pol_chain_address']
        ).call()
        
        if allowance < price:
            print(f"   Approving USDC spending...")
            approve_tx = self.usdc.functions.approve(
                self.config['pol_chain_address'],
                2**256 - 1  # Approve max
            ).build_transaction({
                'from': self.account.address,
                'nonce': self.w3.eth.get_transaction_count(self.account.address),
                'gas': 100000,
                'gasPrice': self.w3.eth.gas_price
            })
            
            signed_tx = self.account.sign_transaction(approve_tx)
            tx_hash = self.w3.eth.send_raw_transaction(signed_tx.raw_transaction)
            print(f"   Waiting for approval tx: {tx_hash.hex()}")
            self.w3.eth.wait_for_transaction_receipt(tx_hash)
            print(f"   ✅ Approved")
        
        # Subscribe
        subscribe_tx = self.pol_chain.functions.subscribe(
            self.registry_address,
            self.nft_id,
            plan
        ).build_transaction({
            'from': self.account.address,
            'nonce': self.w3.eth.get_transaction_count(self.account.address),
            'gas': 300000,
            'gasPrice': self.w3.eth.gas_price
        })
        
        signed_tx = self.account.sign_transaction(subscribe_tx)
        tx_hash = self.w3.eth.send_raw_transaction(signed_tx.raw_transaction)
        print(f"   Waiting for subscription tx: {tx_hash.hex()}")
        receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
        
        if receipt['status'] == 1:
            print(f"   ✅ Subscribed successfully!")
            return True
        else:
            print(f"   ❌ Subscription failed")
            return False
    
    def get_mining_state(self) -> dict:
        """Get current mining state from contract"""
        height = self.pol_chain.functions.height().call()
        prev_hash = self.pol_chain.functions.prevHash().call()
        target = self.pol_chain.functions.target().call()
        
        return {
            'height': height,
            'prev_hash': prev_hash.hex() if isinstance(prev_hash, bytes) else prev_hash,
            'target': target
        }
    
    def find_valid_nonce(self, prev_hash: bytes, height: int, target: int) -> Optional[int]:
        """Find a valid nonce for the current block"""
        agent_key_bytes = self.pol_chain.functions.agentKey(
            self.registry_address,
            self.nft_id
        ).call()
        
        payout_address = Web3.to_checksum_address(self.payout_address)
        
        print(f"⛏️  Mining block {height + 1}...")
        print(f"   Target: {target}")
        print(f"   Difficulty: ~{2**256 / target:.2e}")
        
        start_time = time.time()
        
        for nonce in range(self.max_nonce_attempts):
            # Calculate digest same way as contract
            # keccak256(abi.encode(prevHash, nextHeight, key, payout, nonce))
            encoded = self.w3.codec.encode(
                ['bytes32', 'uint256', 'bytes32', 'address', 'uint256'],
                [prev_hash, height + 1, agent_key_bytes, payout_address, nonce]
            )
            digest = self.w3.keccak(encoded)
            digest_int = int.from_bytes(digest, byteorder='big')
            
            if digest_int <= target:
                elapsed = time.time() - start_time
                hash_rate = nonce / elapsed if elapsed > 0 else 0
                print(f"   ✅ Found valid nonce: {nonce}")
                print(f"   Digest: {digest.hex()}")
                print(f"   Attempts: {nonce + 1}")
                print(f"   Time: {elapsed:.2f}s")
                print(f"   Hash rate: {hash_rate:.2f} H/s")
                return nonce
            
            # Progress indicator
            if nonce % 10000 == 0 and nonce > 0:
                elapsed = time.time() - start_time
                hash_rate = nonce / elapsed if elapsed > 0 else 0
                print(f"   Tried {nonce} nonces... ({hash_rate:.2f} H/s)")
        
        print(f"   ❌ No valid nonce found in {self.max_nonce_attempts} attempts")
        return None
    
    def mine_block(self) -> bool:
        """Mine a single block"""
        # Get current state
        state = self.get_mining_state()
        prev_hash_bytes = bytes.fromhex(state['prev_hash'].replace('0x', ''))
        
        # Find valid nonce
        nonce = self.find_valid_nonce(
            prev_hash_bytes,
            state['height'],
            state['target']
        )
        
        if nonce is None:
            return False
        
        # Submit solution
        print(f"\n📤 Submitting solution...")
        
        try:
            mine_tx = self.pol_chain.functions.mine(
                self.registry_address,
                self.nft_id,
                Web3.to_checksum_address(self.payout_address),
                nonce,
                0,  # deadline (0 for no signature)
                b''  # empty signature (using owner tx)
            ).build_transaction({
                'from': self.account.address,
                'nonce': self.w3.eth.get_transaction_count(self.account.address),
                'gas': 500000,
                'gasPrice': self.w3.eth.gas_price
            })
            
            signed_tx = self.account.sign_transaction(mine_tx)
            tx_hash = self.w3.eth.send_raw_transaction(signed_tx.raw_transaction)
            print(f"   Transaction: {tx_hash.hex()}")
            
            receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
            
            if receipt['status'] == 1:
                print(f"   ✅ Block mined successfully!")
                
                # Get reward info from events
                new_height = self.pol_chain.functions.height().call()
                pol_balance = self.pol_token.functions.balanceOf(self.payout_address).call()
                
                print(f"\n🎉 Mining Success!")
                print(f"   New height: {new_height}")
                print(f"   POL balance: {pol_balance / 1e18:.2f} POL")
                
                return True
            else:
                print(f"   ❌ Transaction failed")
                return False
                
        except Exception as e:
            print(f"   ❌ Error submitting transaction: {e}")
            return False
    
    def run(self, continuous: bool = False):
        """Run the miner"""
        print("\n" + "="*60)
        print("🚀 POL Miner Starting")
        print("="*60)
        
        # Check balances
        eth_balance = self.w3.eth.get_balance(self.account.address)
        usdc_balance = self.usdc.functions.balanceOf(self.account.address).call()
        pol_balance = self.pol_token.functions.balanceOf(self.payout_address).call()
        
        print(f"\n💰 Balances:")
        print(f"   ETH: {eth_balance / 1e18:.6f}")
        print(f"   USDC: {usdc_balance / 1e6:.6f}")
        print(f"   POL: {pol_balance / 1e18:.2f}")
        
        # Check subscription
        is_subscribed, time_remaining = self.check_subscription()
        
        if is_subscribed:
            print(f"\n✅ Agent is subscribed")
            print(f"   Time remaining: {time_remaining / 3600:.2f} hours")
        else:
            print(f"\n⚠️  Agent is not subscribed")
            if self.auto_subscribe:
                if not self.subscribe():
                    print("❌ Failed to subscribe. Exiting.")
                    return
            else:
                print("❌ Auto-subscribe disabled. Please subscribe manually.")
                return
        
        # Mining loop
        blocks_mined = 0
        
        while True:
            try:
                # Check subscription status
                is_subscribed, time_remaining = self.check_subscription()
                
                if not is_subscribed:
                    print(f"\n⚠️  Subscription expired!")
                    if self.auto_subscribe:
                        print("Renewing subscription...")
                        if not self.subscribe():
                            print("❌ Failed to renew subscription. Exiting.")
                            break
                    else:
                        print("❌ Auto-subscribe disabled. Exiting.")
                        break
                
                # Mine block
                success = self.mine_block()
                
                if success:
                    blocks_mined += 1
                    print(f"\n📊 Total blocks mined: {blocks_mined}")
                
                # Exit if not continuous mode
                if not continuous:
                    break
                
                # Wait before next attempt
                print(f"\n⏳ Waiting {self.check_interval} seconds...")
                time.sleep(self.check_interval)
                
            except KeyboardInterrupt:
                print("\n\n🛑 Mining stopped by user")
                break
            except Exception as e:
                print(f"\n❌ Error: {e}")
                if not continuous:
                    break
                print(f"   Retrying in {self.check_interval} seconds...")
                time.sleep(self.check_interval)
        
        print(f"\n" + "="*60)
        print(f"✅ Mining session complete!")
        print(f"   Blocks mined: {blocks_mined}")
        print("="*60)
    
    @staticmethod
    def _get_pol_chain_abi() -> list:
        """Get POL Chain contract ABI (minimal)"""
        return [
            {"inputs": [{"internalType": "address", "name": "identityRegistry", "type": "address"}, {"internalType": "uint256", "name": "agentId", "type": "uint256"}], "name": "agentKey", "outputs": [{"internalType": "bytes32", "name": "", "type": "bytes32"}], "stateMutability": "pure", "type": "function"},
            {"inputs": [{"internalType": "bytes32", "name": "", "type": "bytes32"}], "name": "paidUntil", "outputs": [{"internalType": "uint256", "name": "", "type": "uint256"}], "stateMutability": "view", "type": "function"},
            {"inputs": [{"internalType": "enum ProofOfAIAgentLifeChain.Plan", "name": "plan", "type": "uint8"}], "name": "planPrice", "outputs": [{"internalType": "uint256", "name": "", "type": "uint256"}], "stateMutability": "pure", "type": "function"},
            {"inputs": [{"internalType": "enum ProofOfAIAgentLifeChain.Plan", "name": "plan", "type": "uint8"}], "name": "planDuration", "outputs": [{"internalType": "uint256", "name": "", "type": "uint256"}], "stateMutability": "pure", "type": "function"},
            {"inputs": [{"internalType": "address", "name": "identityRegistry", "type": "address"}, {"internalType": "uint256", "name": "agentId", "type": "uint256"}, {"internalType": "enum ProofOfAIAgentLifeChain.Plan", "name": "plan", "type": "uint8"}], "name": "subscribe", "outputs": [], "stateMutability": "nonpayable", "type": "function"},
            {"inputs": [], "name": "height", "outputs": [{"internalType": "uint256", "name": "", "type": "uint256"}], "stateMutability": "view", "type": "function"},
            {"inputs": [], "name": "prevHash", "outputs": [{"internalType": "bytes32", "name": "", "type": "bytes32"}], "stateMutability": "view", "type": "function"},
            {"inputs": [], "name": "target", "outputs": [{"internalType": "uint256", "name": "", "type": "uint256"}], "stateMutability": "view", "type": "function"},
            {"inputs": [{"internalType": "address", "name": "identityRegistry", "type": "address"}, {"internalType": "uint256", "name": "agentId", "type": "uint256"}, {"internalType": "address", "name": "payout", "type": "address"}, {"internalType": "uint256", "name": "nonce", "type": "uint256"}, {"internalType": "uint256", "name": "deadline", "type": "uint256"}, {"internalType": "bytes", "name": "signature", "type": "bytes"}], "name": "mine", "outputs": [{"internalType": "bytes32", "name": "digest", "type": "bytes32"}], "stateMutability": "nonpayable", "type": "function"}
        ]
    
    @staticmethod
    def _get_pol_token_abi() -> list:
        """Get POL Token contract ABI (minimal)"""
        return [
            {"inputs": [{"internalType": "address", "name": "account", "type": "address"}], "name": "balanceOf", "outputs": [{"internalType": "uint256", "name": "", "type": "uint256"}], "stateMutability": "view", "type": "function"}
        ]
    
    @staticmethod
    def _get_usdc_abi() -> list:
        """Get USDC contract ABI (minimal)"""
        return [
            {"inputs": [{"internalType": "address", "name": "account", "type": "address"}], "name": "balanceOf", "outputs": [{"internalType": "uint256", "name": "", "type": "uint256"}], "stateMutability": "view", "type": "function"},
            {"inputs": [{"internalType": "address", "name": "owner", "type": "address"}, {"internalType": "address", "name": "spender", "type": "address"}], "name": "allowance", "outputs": [{"internalType": "uint256", "name": "", "type": "uint256"}], "stateMutability": "view", "type": "function"},
            {"inputs": [{"internalType": "address", "name": "spender", "type": "address"}, {"internalType": "uint256", "name": "amount", "type": "uint256"}], "name": "approve", "outputs": [{"internalType": "bool", "name": "", "type": "bool"}], "stateMutability": "nonpayable", "type": "function"}
        ]


def load_config_from_agent_file(agent_file: str, nft_id: int, rpc_url: str, 
                                pol_chain: str, pol_token: str, usdc: str, registry: str) -> dict:
    """Load configuration from agent file"""
    with open(agent_file, 'r') as f:
        content = f.read()
    
    # Parse agent file
    address = None
    private_key = None
    
    for line in content.split('\n'):
        if 'Address:' in line:
            address = line.split('Address:')[1].strip()
        elif 'Private key:' in line:
            private_key = line.split('Private key:')[1].strip()
    
    if not address or not private_key:
        raise ValueError("Could not parse agent file")
    
    return {
        'rpc_url': rpc_url,
        'private_key': private_key,
        'pol_chain_address': pol_chain,
        'pol_token_address': pol_token,
        'usdc_address': usdc,
        'registry_address': registry,
        'nft_id': nft_id,
        'payout_address': address,
        'max_nonce_attempts': 1000000,
        'check_interval': 5,
        'auto_subscribe': True,
        'subscription_plan': 1  # Day
    }


def main():
    parser = argparse.ArgumentParser(
        description='Proof of AI Agent Life Miner',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Mine with config file
  python3 miner.py --config config.json

  # Mine with agent file
  python3 miner.py --agent-file ../agents/agent-1.txt --nft-id 1 \\
      --rpc-url $BASE_SEPOLIA_RPC \\
      --pol-chain 0xAcA4dC2B2f2aBE1de0e9ac2E4408c76c9a86d019 \\
      --pol-token 0xC04c1Cf7cd72cc85541337B8980d94473b3F8A65 \\
      --usdc 0x23af5625F8f37Bd553E5c3f852F7Be6452aE1E59 \\
      --registry 0x408D7B0C9D4C94D46a71Ab2D3bFA80246c255986

  # Mine continuously
  python3 miner.py --config config.json --continuous
        """
    )
    
    parser.add_argument('--config', help='Path to config JSON file')
    parser.add_argument('--agent-file', help='Path to agent file (alternative to config)')
    parser.add_argument('--nft-id', type=int, help='Agent NFT ID')
    parser.add_argument('--rpc-url', help='RPC URL')
    parser.add_argument('--pol-chain', help='POL Chain contract address')
    parser.add_argument('--pol-token', help='POL Token contract address')
    parser.add_argument('--usdc', help='USDC contract address')
    parser.add_argument('--registry', help='Agent Registry contract address')
    parser.add_argument('--continuous', action='store_true', help='Mine continuously')
    parser.add_argument('--max-attempts', type=int, default=1000000, help='Max nonce attempts per block')
    
    args = parser.parse_args()
    
    # Load configuration
    if args.config:
        with open(args.config, 'r') as f:
            config = json.load(f)
    elif args.agent_file:
        if not all([args.nft_id, args.rpc_url, args.pol_chain, args.pol_token, args.usdc, args.registry]):
            print("Error: When using --agent-file, you must provide all contract addresses")
            sys.exit(1)
        config = load_config_from_agent_file(
            args.agent_file, args.nft_id, args.rpc_url,
            args.pol_chain, args.pol_token, args.usdc, args.registry
        )
    else:
        print("Error: Must provide either --config or --agent-file")
        parser.print_help()
        sys.exit(1)
    
    # Override max attempts if specified
    if args.max_attempts:
        config['max_nonce_attempts'] = args.max_attempts
    
    # Create and run miner
    try:
        miner = POLMiner(config)
        miner.run(continuous=args.continuous)
    except KeyboardInterrupt:
        print("\n🛑 Interrupted by user")
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
