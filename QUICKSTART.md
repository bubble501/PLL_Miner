# Quick Start Guide for POL Miner

Get mining POL tokens in 5 minutes!

## Prerequisites

1. Python 3.8+ installed
2. An agent file or private key
3. Agent NFT minted and subscribed (or USDC to subscribe)
4. Some ETH for gas fees

## 🚀 3-Step Setup

### Step 1: Install Dependencies

```bash
cd miner
pip install -r requirements.txt
```

### Step 2: Create Config

**Option A: Use Agent File** (Easiest)

```bash
# Just use the wrapper script with your agent number
./mine.sh 1
```

**Option B: Create Config File**

```bash
# Copy the example
cp config.example.json config.json

# Edit with your settings
nano config.json  # or vim, code, etc.
```

Fill in these values:

```json
{
  "private_key": "0xYOUR_PRIVATE_KEY",
  "nft_id": 1,
  "rpc_url": "https://sepolia.base.org"
}
```

The contract addresses are pre-filled for Base Sepolia testnet.

### Step 3: Start Mining!

**Mine one block:**

```bash
python3 miner.py --config config.json
```

**Mine continuously:**

```bash
python3 miner.py --config config.json --continuous
```

**Or use the wrapper:**

```bash
./mine.sh 1              # Mine one block with agent-1
./mine.sh 1 --continuous # Mine continuously with agent-1
```

## ✅ Success!

You should see output like:

```
============================================================
🚀 POL Miner Starting
============================================================

🔑 Loaded account: 0x8Ea3...
✅ Miner initialized for Agent NFT #1
💰 Payout address: 0x8Ea3...

💰 Balances:
   ETH: 0.234567
   USDC: 100.000000
   POL: 0.00

✅ Agent is subscribed
   Time remaining: 23.45 hours

⛏️  Mining block 1...
   ✅ Found valid nonce: 12345
   ✅ Block mined successfully!

🎉 Mining Success!
   New height: 1
   POL balance: 9.70 POL
```

## 🆘 Troubleshooting

### "No module named 'web3'"

```bash
pip install web3 eth-account
```

### "Insufficient USDC balance"

You need USDC to subscribe for mining access:

```bash
# From main project directory
cd ..
./deploy-helper.sh mint-usdc
```

### "Agent not subscribed"

The miner will auto-subscribe if you have USDC. Or manually subscribe:

```bash
cd ..
./deploy-helper.sh subscribe 1 86400  # Subscribe agent #1 for 1 day
```

### "No valid nonce found"

This is normal if difficulty is high or other miners found the block first. The miner will try again automatically in continuous mode.

## 📚 Next Steps

- Read the full [README.md](README.md) for advanced usage
- Configure subscription plans in `config.json`
- Run multiple miners for different agents
- Monitor your POL balance on [Basescan](https://sepolia.basescan.org/)

## 🎯 Pro Tips

1. **Continuous Mode**: Use `--continuous` to keep mining 24/7
2. **Multiple Agents**: Run separate miners for each agent you own
3. **Monitor Logs**: Use `tee` to save output: `./mine.sh 1 --continuous | tee mining.log`
4. **Background Mining**: Use `screen` or `tmux` to keep mining when you disconnect
5. **Auto-restart**: Use `systemd` or `pm2` for production deployments

## 💡 Example: Run 3 Miners

```bash
# Terminal 1
./mine.sh 1 --continuous

# Terminal 2
./mine.sh 2 --continuous

# Terminal 3
./mine.sh 3 --continuous
```

Or use `screen`:

```bash
screen -S miner1 -dm ./mine.sh 1 --continuous
screen -S miner2 -dm ./mine.sh 2 --continuous
screen -S miner3 -dm ./mine.sh 3 --continuous

# List running miners
screen -ls

# Attach to a miner
screen -r miner1
```

---

**Happy Mining!** ⛏️💎

For detailed documentation, see [README.md](README.md)
