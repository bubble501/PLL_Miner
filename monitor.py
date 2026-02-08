#!/usr/bin/env python3
"""
POL Miner Monitor

Real-time monitoring dashboard for mining operations.
Shows current stats, balances, and recent blocks.
"""

import json
import sys
import time
from datetime import datetime
from web3 import Web3
from eth_account import Account


def clear_screen():
    """Clear terminal screen"""
    print('\033[2J\033[H', end='')


def format_time(seconds: int) -> str:
    """Format seconds into human-readable time"""
    if seconds < 60:
        return f"{seconds}s"
    elif seconds < 3600:
        return f"{seconds // 60}m {seconds % 60}s"
    elif seconds < 86400:
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        return f"{hours}h {minutes}m"
    else:
        days = seconds // 86400
        hours = (seconds % 86400) // 3600
        return f"{days}d {hours}h"


def monitor(config: dict, refresh_interval: int = 10):
    """Monitor mining operations"""
    
    # Initialize Web3
    w3 = Web3(Web3.HTTPProvider(config['rpc_url']))
    account = Account.from_key(config['private_key'])
    
    # Load contracts
    pol_chain = w3.eth.contract(
        address=Web3.to_checksum_address(config['pol_chain_address']),
        abi=[
            {"inputs": [{"internalType": "address", "name": "identityRegistry", "type": "address"}, {"internalType": "uint256", "name": "agentId", "type": "uint256"}], "name": "agentKey", "outputs": [{"internalType": "bytes32", "name": "", "type": "bytes32"}], "stateMutability": "pure", "type": "function"},
            {"inputs": [{"internalType": "bytes32", "name": "", "type": "bytes32"}], "name": "paidUntil", "outputs": [{"internalType": "uint256", "name": "", "type": "uint256"}], "stateMutability": "view", "type": "function"},
            {"inputs": [], "name": "height", "outputs": [{"internalType": "uint256", "name": "", "type": "uint256"}], "stateMutability": "view", "type": "function"},
            {"inputs": [], "name": "target", "outputs": [{"internalType": "uint256", "name": "", "type": "uint256"}], "stateMutability": "view", "type": "function"},
        ]
    )
    
    pol_token = w3.eth.contract(
        address=Web3.to_checksum_address(config['pol_token_address']),
        abi=[
            {"inputs": [{"internalType": "address", "name": "account", "type": "address"}], "name": "balanceOf", "outputs": [{"internalType": "uint256", "name": "", "type": "uint256"}], "stateMutability": "view", "type": "function"},
            {"inputs": [], "name": "totalSupply", "outputs": [{"internalType": "uint256", "name": "", "type": "uint256"}], "stateMutability": "view", "type": "function"},
        ]
    )
    
    usdc = w3.eth.contract(
        address=Web3.to_checksum_address(config['usdc_address']),
        abi=[
            {"inputs": [{"internalType": "address", "name": "account", "type": "address"}], "name": "balanceOf", "outputs": [{"internalType": "uint256", "name": "", "type": "uint256"}], "stateMutability": "view", "type": "function"}
        ]
    )
    
    agent_key = pol_chain.functions.agentKey(
        Web3.to_checksum_address(config['registry_address']),
        config['nft_id']
    ).call()
    
    # Track initial state
    start_time = time.time()
    initial_height = pol_chain.functions.height().call()
    initial_pol = pol_token.functions.balanceOf(account.address).call()
    
    print("Starting POL Miner Monitor...")
    print("Press Ctrl+C to exit\n")
    time.sleep(2)
    
    try:
        while True:
            clear_screen()
            
            # Get current state
            current_time = int(time.time())
            eth_balance = w3.eth.get_balance(account.address)
            usdc_balance = usdc.functions.balanceOf(account.address).call()
            pol_balance = pol_token.functions.balanceOf(account.address).call()
            pol_supply = pol_token.functions.totalSupply().call()
            
            height = pol_chain.functions.height().call()
            target = pol_chain.functions.target().call()
            difficulty = 2**256 / target if target > 0 else float('inf')
            
            paid_until = pol_chain.functions.paidUntil(agent_key).call()
            is_subscribed = paid_until > current_time
            time_remaining = paid_until - current_time if is_subscribed else 0
            
            # Calculate stats
            uptime = int(time.time() - start_time)
            blocks_mined = height - initial_height
            pol_earned = (pol_balance - initial_pol) / 1e18
            
            # Display dashboard
            print("╔═══════════════════════════════════════════════════════════════╗")
            print("║              POL Miner Monitoring Dashboard                   ║")
            print("╚═══════════════════════════════════════════════════════════════╝")
            print()
            
            # Header
            print(f"  Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"  Uptime: {format_time(uptime)}")
            print(f"  Agent: #{config['nft_id']} @ {account.address[:10]}...{account.address[-8:]}")
            print()
            
            # Subscription Status
            print("┌─────────────────────────────────────────────────────────────┐")
            print("│ Subscription Status                                         │")
            print("├─────────────────────────────────────────────────────────────┤")
            if is_subscribed:
                print(f"│ Status:         ✅ ACTIVE                                    │")
                print(f"│ Time Remaining: {format_time(time_remaining):45s} │")
            else:
                print(f"│ Status:         ❌ EXPIRED                                   │")
                print(f"│ Time Remaining: 0s                                          │")
            print("└─────────────────────────────────────────────────────────────┘")
            print()
            
            # Balances
            print("┌─────────────────────────────────────────────────────────────┐")
            print("│ Balances                                                    │")
            print("├─────────────────────────────────────────────────────────────┤")
            print(f"│ ETH:  {eth_balance / 1e18:50.6f} │")
            print(f"│ USDC: {usdc_balance / 1e6:50.6f} │")
            print(f"│ POL:  {pol_balance / 1e18:50.2f} │")
            print("└─────────────────────────────────────────────────────────────┘")
            print()
            
            # Mining Stats
            print("┌─────────────────────────────────────────────────────────────┐")
            print("│ Mining Statistics                                           │")
            print("├─────────────────────────────────────────────────────────────┤")
            print(f"│ Current Height: {height:44d} │")
            print(f"│ Difficulty:     {difficulty:44.2e} │")
            print(f"│ Target:         {target:44d} │")
            print("└─────────────────────────────────────────────────────────────┘")
            print()
            
            # Session Stats
            print("┌─────────────────────────────────────────────────────────────┐")
            print("│ Session Statistics                                          │")
            print("├─────────────────────────────────────────────────────────────┤")
            print(f"│ Blocks Mined:   {blocks_mined:44d} │")
            print(f"│ POL Earned:     {pol_earned:44.2f} │")
            if uptime > 0:
                blocks_per_hour = (blocks_mined / uptime) * 3600
                pol_per_hour = (pol_earned / uptime) * 3600
                print(f"│ Blocks/Hour:    {blocks_per_hour:44.2f} │")
                print(f"│ POL/Hour:       {pol_per_hour:44.2f} │")
            print("└─────────────────────────────────────────────────────────────┘")
            print()
            
            # Network Stats
            print("┌─────────────────────────────────────────────────────────────┐")
            print("│ Network Statistics                                          │")
            print("├─────────────────────────────────────────────────────────────┤")
            print(f"│ Total POL Supply: {pol_supply / 1e18:42.2f} │")
            print(f"│ Your Share:       {(pol_balance / pol_supply * 100) if pol_supply > 0 else 0:42.4f}% │")
            print("└─────────────────────────────────────────────────────────────┘")
            print()
            
            # Footer
            print(f"  Refreshing in {refresh_interval}s... (Press Ctrl+C to exit)")
            
            time.sleep(refresh_interval)
            
    except KeyboardInterrupt:
        print("\n\nMonitor stopped by user")


def main():
    if len(sys.argv) < 2:
        print("Usage: python3 monitor.py <config.json> [refresh_interval]")
        print("\nExample:")
        print("  python3 monitor.py config.json")
        print("  python3 monitor.py config.json 5")
        sys.exit(1)
    
    config_file = sys.argv[1]
    refresh_interval = int(sys.argv[2]) if len(sys.argv) > 2 else 10
    
    # Load config
    try:
        with open(config_file, 'r') as f:
            config = json.load(f)
    except Exception as e:
        print(f"Error loading config: {e}")
        sys.exit(1)
    
    monitor(config, refresh_interval)


if __name__ == '__main__':
    main()
