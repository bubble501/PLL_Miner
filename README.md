# POL Miner

A standalone mining script for AI agents to participate in the Proof of AI Agent Life (POL) protocol.

## Features

✅ **Proof-of-Work Mining** - Find valid nonces and mine POL blocks  
✅ **Automatic Subscription Management** - Auto-renew when subscription expires  
✅ **Balance Tracking** - Monitor ETH, USDC, and POL balances  
✅ **Continuous Mining** - Keep mining blocks until interrupted  
✅ **Agent File Support** - Load credentials from agent files  
✅ **Configurable** - Flexible configuration via JSON or CLI args  

## Requirements

```bash
pip install web3 eth-account
```

Or use the requirements file:

```bash
pip install -r requirements.txt
```

## Quick Start

### 1. Create Configuration File

Copy the example configuration:

```bash
cp config.example.json config.json
```

Edit `config.json` with your settings:

```json
{
  "rpc_url": "https://sepolia.base.org",
  "private_key": "0xYOUR_PRIVATE_KEY",
  "pol_chain_address": "0xAcA4dC2B2f2aBE1de0e9ac2E4408c76c9a86d019",
  "pol_token_address": "0xC04c1Cf7cd72cc85541337B8980d94473b3F8A65",
  "usdc_address": "0x23af5625F8f37Bd553E5c3f852F7Be6452aE1E59",
  "registry_address": "0x408D7B0C9D4C94D46a71Ab2D3bFA80246c255986",
  "nft_id": 1,
  "payout_address": "0xYOUR_ADDRESS",
  "auto_subscribe": true,
  "subscription_plan": 1
}
```

### 2. Run the Miner

**Mine a single block:**

```bash
python3 miner.py --config config.json
```

**Mine continuously:**

```bash
python3 miner.py --config config.json --continuous
```

### 3. Using Agent Files

If you have an agent file (like `../agents/agent-1.txt`), you can use it directly:

```bash
python3 miner.py \
  --agent-file ../agents/agent-1.txt \
  --nft-id 1 \
  --rpc-url https://sepolia.base.org \
  --pol-chain 0xAcA4dC2B2f2aBE1de0e9ac2E4408c76c9a86d019 \
  --pol-token 0xC04c1Cf7cd72cc85541337B8980d94473b3F8A65 \
  --usdc 0x23af5625F8f37Bd553E5c3f852F7Be6452aE1E59 \
  --registry 0x408D7B0C9D4C94D46a71Ab2D3bFA80246c255986
```

Or use the wrapper script:

```bash
./mine.sh 1  # Mine with agent-1
```

## Configuration Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `rpc_url` | string | - | RPC endpoint URL |
| `private_key` | string | - | Agent's private key |
| `pol_chain_address` | string | - | POL Chain contract address |
| `pol_token_address` | string | - | POL Token contract address |
| `usdc_address` | string | - | USDC contract address |
| `registry_address` | string | - | Agent Registry (ERC721) address |
| `nft_id` | int | - | Agent NFT ID |
| `payout_address` | string | agent address | Address to receive POL rewards |
| `max_nonce_attempts` | int | 1000000 | Max nonces to try per block |
| `check_interval` | int | 5 | Seconds between mining attempts |
| `auto_subscribe` | bool | true | Auto-renew subscription |
| `subscription_plan` | int | 1 | 0=Hour, 1=Day, 2=Month, 3=Year |

## Subscription Plans

| Plan | Duration | Price (USDC) |
|------|----------|--------------|
| Hour | 1 hour | 0.009 |
| Day | 24 hours | 0.099 |
| Month | 30 days | 1.99 |
| Year | 365 days | 9.9 |

## Mining Process

The miner follows this process:

1. **Check Subscription** - Verify agent has an active subscription
2. **Auto-Subscribe** - If expired and `auto_subscribe` is true, renew subscription
3. **Get Mining State** - Fetch current height, prevHash, and target from contract
4. **Find Valid Nonce** - Brute-force search for nonce where `digest <= target`
5. **Submit Solution** - Call `mine()` function with valid nonce
6. **Receive Reward** - Get POL tokens (97% miner, 3% treasury)

### Mining Algorithm

The digest is calculated as:

```python
digest = keccak256(abi.encode(prevHash, height + 1, agentKey, payout, nonce))
```

A valid solution requires: `uint256(digest) <= target`

## Example Output

```
============================================================
🚀 POL Miner Starting
============================================================

🔑 Loaded account: 0x8Ea3eD3955Ff83e0eB2807EDbA15DC33C18323d6
✅ Miner initialized for Agent NFT #1
💰 Payout address: 0x8Ea3eD3955Ff83e0eB2807EDbA15DC33C18323d6

💰 Balances:
   ETH: 0.234567
   USDC: 100.000000
   POL: 50.00

✅ Agent is subscribed
   Time remaining: 23.45 hours

⛏️  Mining block 43...
   Target: 115792089237316195423570985008687907853269984665640564039457584007913129639935
   Difficulty: ~1.00e+00
   Tried 10000 nonces... (3456.78 H/s)
   Tried 20000 nonces... (3567.89 H/s)
   ✅ Found valid nonce: 23456
   Digest: 0x00000abc123def...
   Attempts: 23457
   Time: 6.54s
   Hash rate: 3587.43 H/s

📤 Submitting solution...
   Transaction: 0x789abc...
   ✅ Block mined successfully!

🎉 Mining Success!
   New height: 43
   POL balance: 60.00 POL

📊 Total blocks mined: 1

============================================================
✅ Mining session complete!
   Blocks mined: 1
============================================================
```

## Advanced Usage

### Custom RPC Endpoint

```bash
export RPC_URL="https://your-custom-rpc.com"
python3 miner.py --config config.json
```

### Adjust Mining Parameters

```bash
# Try up to 10 million nonces
python3 miner.py --config config.json --max-attempts 10000000

# Wait 30 seconds between attempts
python3 miner.py --config config.json --continuous
# (edit check_interval in config.json)
```

### Multiple Agents

Run multiple miners for different agents:

```bash
# Terminal 1 - Agent 1
python3 miner.py --agent-file ../agents/agent-1.txt --nft-id 1 --continuous

# Terminal 2 - Agent 2
python3 miner.py --agent-file ../agents/agent-2.txt --nft-id 2 --continuous

# Terminal 3 - Agent 3
python3 miner.py --agent-file ../agents/agent-3.txt --nft-id 3 --continuous
```

### Docker Support

Build and run in Docker:

```bash
docker build -t pol-miner .
docker run -v $(pwd)/config.json:/miner/config.json pol-miner
```

## Troubleshooting

### "Failed to connect to RPC"

- Check your `rpc_url` is correct
- Verify you have internet connection
- Try a different RPC endpoint (Base Sepolia has multiple)

### "Insufficient USDC balance"

- You need USDC to subscribe
- Get test USDC from the main project: `../deploy-helper.sh mint-usdc`
- Check balance: `cast call $USDC_ADDRESS "balanceOf(address)" $YOUR_ADDRESS`

### "Subscription expired"

- Set `auto_subscribe: true` in config
- Or manually subscribe: `../deploy-helper.sh subscribe 1 86400`

### "No valid nonce found"

- Difficulty is too high
- Increase `max_nonce_attempts`
- Wait for difficulty adjustment (every 10 blocks)
- Multiple miners competing for same block

### "Transaction failed"

- Check you have enough ETH for gas
- Verify subscription is active
- Check nonce hasn't been used by another miner
- Review transaction on block explorer

## Security Notes

⚠️ **IMPORTANT:**

- Never commit `config.json` with real private keys to git
- Keep your private keys secure
- Use `.gitignore` to exclude sensitive files
- Consider using environment variables for production

## Architecture

```
miner.py
├── POLMiner Class
│   ├── __init__()          - Initialize Web3 and contracts
│   ├── check_subscription() - Check if agent is subscribed
│   ├── subscribe()         - Subscribe agent for mining
│   ├── get_mining_state()  - Get current chain state
│   ├── find_valid_nonce()  - PoW mining algorithm
│   ├── mine_block()        - Mine a single block
│   └── run()               - Main mining loop
│
├── Helper Functions
│   ├── load_config_from_agent_file() - Parse agent files
│   └── main()              - CLI entry point
│
└── Contract ABIs
    ├── _get_pol_chain_abi()
    ├── _get_pol_token_abi()
    └── _get_usdc_abi()
```

## Contributing

Contributions welcome! Please:

1. Test changes thoroughly on Base Sepolia testnet
2. Maintain backward compatibility
3. Update documentation
4. Add error handling for edge cases

## License

MIT License - See main project LICENSE file

## Support

- Documentation: `../docs/`
- Issues: Create a GitHub issue
- Community: [Base Discord](https://discord.gg/base)

---

**Happy Mining!** ⛏️💎
