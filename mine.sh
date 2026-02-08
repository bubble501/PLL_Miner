#!/bin/bash

# Simple wrapper script for mining with agent files
# Usage: ./mine.sh <agent_num> [--continuous]

if [ -z "$1" ]; then
    echo "Usage: ./mine.sh <agent_num> [--continuous]"
    echo "Example: ./mine.sh 1"
    echo "Example: ./mine.sh 2 --continuous"
    exit 1
fi

AGENT_NUM=$1
CONTINUOUS_FLAG=""

if [ "$2" == "--continuous" ]; then
    CONTINUOUS_FLAG="--continuous"
fi

# Load environment variables
if [ -f ../.env ]; then
    source ../.env
else
    echo "Error: ../.env file not found"
    exit 1
fi

# Check if agent file exists
AGENT_FILE="../agents/agent-$AGENT_NUM.txt"
if [ ! -f "$AGENT_FILE" ]; then
    echo "Error: Agent file not found: $AGENT_FILE"
    exit 1
fi

# Default contract addresses (Base Sepolia testnet)
POL_CHAIN="${POL_CHAIN_ADDRESS:-0xAcA4dC2B2f2aBE1de0e9ac2E4408c76c9a86d019}"
POL_TOKEN="${POL_TOKEN_ADDRESS:-0xC04c1Cf7cd72cc85541337B8980d94473b3F8A65}"
USDC="${MOCK_USDC_ADDRESS:-0x23af5625F8f37Bd553E5c3f852F7Be6452aE1E59}"
REGISTRY="${MOCK_ERC721_ADDRESS:-0x408D7B0C9D4C94D46a71Ab2D3bFA80246c255986}"
RPC="${BASE_SEPOLIA_RPC:-https://sepolia.base.org}"

# For simplicity, assume NFT ID = agent number + 10
# Adjust this logic based on your setup
NFT_ID=$((AGENT_NUM + 10))

echo "╔═══════════════════════════════════════════════════════════════╗"
echo "║          Starting POL Miner for Agent #$AGENT_NUM                      ║"
echo "╚═══════════════════════════════════════════════════════════════╝"
echo ""
echo "Agent File: $AGENT_FILE"
echo "NFT ID: $NFT_ID"
echo "RPC: $RPC"
echo ""

# Run the miner
python3 miner.py \
    --agent-file "$AGENT_FILE" \
    --nft-id "$NFT_ID" \
    --rpc-url "$RPC" \
    --pol-chain "$POL_CHAIN" \
    --pol-token "$POL_TOKEN" \
    --usdc "$USDC" \
    --registry "$REGISTRY" \
    $CONTINUOUS_FLAG
