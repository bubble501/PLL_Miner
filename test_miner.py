#!/usr/bin/env python3
"""
Test script for POL Miner

Verifies that the miner setup is correct without actually mining.
"""

import json
import sys
from web3 import Web3
from miner import POLMiner


def test_connection(config: dict) -> bool:
    """Test RPC connection"""
    print("Testing RPC connection...")
    try:
        w3 = Web3(Web3.HTTPProvider(config['rpc_url']))
        if not w3.is_connected():
            print("  ❌ Failed to connect to RPC")
            return False
        
        chain_id = w3.eth.chain_id
        block_number = w3.eth.block_number
        print(f"  ✅ Connected to chain {chain_id}, block {block_number}")
        return True
    except Exception as e:
        print(f"  ❌ Connection error: {e}")
        return False


def test_account(config: dict) -> bool:
    """Test account loading"""
    print("\nTesting account...")
    try:
        from eth_account import Account
        account = Account.from_key(config['private_key'])
        print(f"  ✅ Account loaded: {account.address}")
        
        # Check ETH balance
        w3 = Web3(Web3.HTTPProvider(config['rpc_url']))
        balance = w3.eth.get_balance(account.address)
        balance_eth = balance / 1e18
        print(f"  ETH Balance: {balance_eth:.6f}")
        
        if balance_eth < 0.001:
            print("  ⚠️  Low ETH balance - you may not have enough for gas")
        
        return True
    except Exception as e:
        print(f"  ❌ Account error: {e}")
        return False


def test_contracts(config: dict) -> bool:
    """Test contract connectivity"""
    print("\nTesting contracts...")
    
    try:
        w3 = Web3(Web3.HTTPProvider(config['rpc_url']))
        
        # Test POL Chain
        print("  Testing POL Chain contract...")
        code = w3.eth.get_code(Web3.to_checksum_address(config['pol_chain_address']))
        if code == b'' or code == b'0x':
            print(f"    ❌ No contract at {config['pol_chain_address']}")
            return False
        print(f"    ✅ Contract found at {config['pol_chain_address']}")
        
        # Test POL Token
        print("  Testing POL Token contract...")
        code = w3.eth.get_code(Web3.to_checksum_address(config['pol_token_address']))
        if code == b'' or code == b'0x':
            print(f"    ❌ No contract at {config['pol_token_address']}")
            return False
        print(f"    ✅ Contract found at {config['pol_token_address']}")
        
        # Test USDC
        print("  Testing USDC contract...")
        code = w3.eth.get_code(Web3.to_checksum_address(config['usdc_address']))
        if code == b'' or code == b'0x':
            print(f"    ❌ No contract at {config['usdc_address']}")
            return False
        print(f"    ✅ Contract found at {config['usdc_address']}")
        
        return True
    except Exception as e:
        print(f"  ❌ Contract error: {e}")
        return False


def test_balances(config: dict) -> bool:
    """Test token balances"""
    print("\nTesting balances...")
    
    try:
        miner = POLMiner(config)
        
        # ETH
        eth_balance = miner.w3.eth.get_balance(miner.account.address)
        print(f"  ETH: {eth_balance / 1e18:.6f}")
        
        # USDC
        usdc_balance = miner.usdc.functions.balanceOf(miner.account.address).call()
        print(f"  USDC: {usdc_balance / 1e6:.6f}")
        
        # POL
        pol_balance = miner.pol_token.functions.balanceOf(miner.payout_address).call()
        print(f"  POL: {pol_balance / 1e18:.2f}")
        
        return True
    except Exception as e:
        print(f"  ❌ Balance error: {e}")
        return False


def test_subscription(config: dict) -> bool:
    """Test subscription status"""
    print("\nTesting subscription...")
    
    try:
        miner = POLMiner(config)
        is_subscribed, time_remaining = miner.check_subscription()
        
        if is_subscribed:
            hours = time_remaining / 3600
            print(f"  ✅ Agent is subscribed")
            print(f"  Time remaining: {hours:.2f} hours")
        else:
            print(f"  ⚠️  Agent is not subscribed")
            print(f"  You'll need to subscribe before mining")
        
        return True
    except Exception as e:
        print(f"  ❌ Subscription error: {e}")
        return False


def test_mining_state(config: dict) -> bool:
    """Test mining state retrieval"""
    print("\nTesting mining state...")
    
    try:
        miner = POLMiner(config)
        state = miner.get_mining_state()
        
        print(f"  Height: {state['height']}")
        print(f"  Target: {state['target']}")
        print(f"  Difficulty: ~{2**256 / state['target']:.2e}")
        
        return True
    except Exception as e:
        print(f"  ❌ Mining state error: {e}")
        return False


def main():
    if len(sys.argv) < 2:
        print("Usage: python3 test_miner.py <config.json>")
        sys.exit(1)
    
    config_file = sys.argv[1]
    
    print("="*60)
    print("POL Miner Test Suite")
    print("="*60)
    
    # Load config
    print(f"\nLoading config from {config_file}...")
    try:
        with open(config_file, 'r') as f:
            config = json.load(f)
        print("  ✅ Config loaded")
    except Exception as e:
        print(f"  ❌ Failed to load config: {e}")
        sys.exit(1)
    
    # Run tests
    tests = [
        ("RPC Connection", lambda: test_connection(config)),
        ("Account", lambda: test_account(config)),
        ("Contracts", lambda: test_contracts(config)),
        ("Balances", lambda: test_balances(config)),
        ("Subscription", lambda: test_subscription(config)),
        ("Mining State", lambda: test_mining_state(config)),
    ]
    
    results = []
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            print(f"\n❌ Test '{name}' crashed: {e}")
            results.append((name, False))
    
    # Summary
    print("\n" + "="*60)
    print("Test Results")
    print("="*60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {status} - {name}")
    
    print(f"\nPassed: {passed}/{total}")
    
    if passed == total:
        print("\n🎉 All tests passed! You're ready to mine!")
        sys.exit(0)
    else:
        print("\n⚠️  Some tests failed. Please fix the issues before mining.")
        sys.exit(1)


if __name__ == '__main__':
    main()
