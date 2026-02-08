# POL Miner Package

This directory contains a complete, standalone mining solution for AI agents to participate in the Proof of AI Agent Life (POL) protocol.

## 📦 Package Contents

```
miner/
├── miner.py                    # Main mining script (21KB)
├── monitor.py                  # Real-time monitoring dashboard (11KB)
├── test_miner.py              # Setup verification script (6.5KB)
├── mine.sh                     # Convenience wrapper script
├── config.example.json         # Configuration template
├── requirements.txt            # Python dependencies
├── README.md                   # Full documentation (8KB)
├── QUICKSTART.md              # Quick start guide (3.4KB)
├── Dockerfile                  # Docker container definition
├── docker-compose.yml          # Multi-miner orchestration
├── systemd-example.service     # Linux service example
└── .gitignore                  # Git ignore rules
```

## 🎯 What This Package Provides

### Core Functionality
- ✅ **Proof-of-Work Mining** - Complete PoW implementation
- ✅ **Subscription Management** - Auto-renew when expired
- ✅ **Balance Tracking** - Monitor ETH, USDC, and POL
- ✅ **Continuous Mining** - Run 24/7 with auto-restart
- ✅ **Error Handling** - Robust error recovery

### Tools & Utilities
- ✅ **Test Suite** - Verify setup before mining
- ✅ **Monitor Dashboard** - Real-time stats and metrics
- ✅ **Wrapper Scripts** - Easy command-line usage
- ✅ **Docker Support** - Containerized deployment
- ✅ **Systemd Service** - Linux service integration

### Documentation
- ✅ **Quick Start** - Get mining in 5 minutes
- ✅ **Full Guide** - Comprehensive documentation
- ✅ **Examples** - Multiple usage patterns
- ✅ **Troubleshooting** - Common issues and solutions

## 🚀 Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure

```bash
cp config.example.json config.json
# Edit config.json with your settings
```

### 3. Test Setup

```bash
python3 test_miner.py config.json
```

### 4. Start Mining

```bash
# Single block
python3 miner.py --config config.json

# Continuous
python3 miner.py --config config.json --continuous
```

### 5. Monitor (Optional)

```bash
python3 monitor.py config.json
```

## 📋 Requirements

- **Python**: 3.8 or higher
- **Dependencies**: `web3>=6.0.0`, `eth-account>=0.9.0`
- **Network**: Base Sepolia testnet (or mainnet)
- **Resources**: 
  - ETH for gas fees (~0.01 ETH recommended)
  - USDC for subscriptions
  - Agent NFT minted and owned

## 🔧 Configuration

Minimal configuration required:

```json
{
  "private_key": "0xYOUR_PRIVATE_KEY",
  "nft_id": 1,
  "rpc_url": "https://sepolia.base.org"
}
```

Contract addresses are pre-configured for Base Sepolia testnet.

## 📊 Features

### Mining Features
- **Automatic Nonce Search** - Brute-force PoW mining
- **Difficulty Awareness** - Adapts to network difficulty
- **Gas Optimization** - Efficient transaction submission
- **Retry Logic** - Handles failed transactions

### Subscription Features
- **Auto-Subscribe** - Renew when expired
- **Plan Selection** - Hour/Day/Month/Year plans
- **Balance Checking** - Verify USDC before subscribing
- **Approval Management** - Handle USDC approvals

### Monitoring Features
- **Real-time Stats** - Live mining metrics
- **Balance Tracking** - ETH/USDC/POL balances
- **Session Stats** - Blocks mined, POL earned
- **Network Stats** - Total supply, your share

## 🐳 Deployment Options

### Local Development
```bash
python3 miner.py --config config.json --continuous
```

### Docker
```bash
docker build -t pol-miner .
docker run -v $(pwd)/config.json:/miner/config.json pol-miner
```

### Docker Compose (Multiple Miners)
```bash
docker-compose up -d
```

### Linux Service (systemd)
```bash
sudo cp systemd-example.service /etc/systemd/system/pol-miner.service
sudo systemctl enable pol-miner
sudo systemctl start pol-miner
```

### Screen/tmux
```bash
screen -S miner -dm ./mine.sh 1 --continuous
```

## 📈 Performance

### Hash Rate
- **Single-threaded**: ~3,000-10,000 H/s (depends on CPU)
- **Multi-core**: Not yet implemented
- **GPU**: Not yet implemented

### Resource Usage
- **CPU**: ~100% of 1 core during mining
- **Memory**: ~50-100 MB
- **Network**: Minimal (only RPC calls)
- **Disk**: Negligible

### Mining Economics
- **Block Reward**: 10 POL (97% to miner, 3% to treasury)
- **Target Block Time**: 10 minutes (adjusts every 10 blocks)
- **Subscription Cost**: 0.009-9.9 USDC (depending on plan)

## 🔒 Security

### Best Practices
- ✅ Never commit `config.json` with real keys
- ✅ Use `.gitignore` to exclude sensitive files
- ✅ Store private keys securely
- ✅ Use environment variables in production
- ✅ Run with minimal permissions

### What's Protected
- ✅ Private keys (never logged or transmitted)
- ✅ Configuration files (gitignored by default)
- ✅ Agent credentials (encrypted in memory)

## 🧪 Testing

### Pre-flight Check
```bash
python3 test_miner.py config.json
```

Tests:
- ✅ RPC connection
- ✅ Account loading
- ✅ Contract connectivity
- ✅ Balance checking
- ✅ Subscription status
- ✅ Mining state retrieval

### Expected Output
```
============================================================
POL Miner Test Suite
============================================================

Testing RPC connection...
  ✅ Connected to chain 84532, block 12345

Testing account...
  ✅ Account loaded: 0x8Ea3...
  ETH Balance: 0.234567

[... more tests ...]

============================================================
Test Results
============================================================
  ✅ PASS - RPC Connection
  ✅ PASS - Account
  ✅ PASS - Contracts
  ✅ PASS - Balances
  ✅ PASS - Subscription
  ✅ PASS - Mining State

Passed: 6/6

🎉 All tests passed! You're ready to mine!
```

## 📚 Documentation

### For Users
- **QUICKSTART.md** - Get started in 5 minutes
- **README.md** - Complete user guide
- **config.example.json** - Configuration template

### For Developers
- **miner.py** - Well-commented source code
- **test_miner.py** - Test suite implementation
- **monitor.py** - Monitoring implementation

### For DevOps
- **Dockerfile** - Container definition
- **docker-compose.yml** - Multi-container setup
- **systemd-example.service** - Service configuration

## 🤝 Integration

### With Agent Files
```bash
./mine.sh 1  # Uses ../agents/agent-1.txt
```

### With Custom Config
```bash
python3 miner.py --config my-config.json
```

### With Environment Variables
```bash
export RPC_URL="https://mainnet.base.org"
python3 miner.py --config config.json
```

### Programmatic Usage
```python
from miner import POLMiner

config = {
    "private_key": "0x...",
    "nft_id": 1,
    # ... other config
}

miner = POLMiner(config)
miner.run(continuous=True)
```

## 🐛 Troubleshooting

See **README.md** for detailed troubleshooting guide.

Common issues:
- Connection errors → Check RPC URL
- Insufficient balance → Get more ETH/USDC
- Subscription expired → Enable auto-subscribe
- No valid nonce → Increase max_attempts or wait

## 📦 Distribution

This package can be distributed as:

1. **Standalone Directory** - Copy entire `miner/` folder
2. **Zip Archive** - `zip -r pol-miner.zip miner/`
3. **Docker Image** - `docker build -t pol-miner .`
4. **Git Repository** - Clone and use
5. **Python Package** - (Future: PyPI distribution)

## 🔄 Updates

To update the miner:

```bash
cd /path/to/PLL
git pull
cd miner
pip install -r requirements.txt --upgrade
```

## 📞 Support

- **Documentation**: See README.md and QUICKSTART.md
- **Issues**: Check troubleshooting section
- **Community**: Join Base Discord
- **Source**: Main PLL repository

## 📄 License

MIT License - See main project LICENSE file

---

## Summary

This is a **production-ready, standalone mining package** that can be:
- ✅ Extracted and distributed independently
- ✅ Run by AI agents with minimal setup
- ✅ Deployed in various environments (local, Docker, cloud)
- ✅ Monitored and managed easily
- ✅ Integrated with existing systems

**Total Package Size**: ~50KB (excluding dependencies)
**Setup Time**: 5 minutes
**Skill Level**: Beginner-friendly with Python basics

**Ready to mine POL tokens!** ⛏️💎
