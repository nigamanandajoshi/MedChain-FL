#!/usr/bin/env bash
# start_blockchain.sh

echo "Starting local Hardhat Ethereum node..."
cd blockchain_eth

# Start node in the background
npx hardhat node > hardhat_node.log 2>&1 &
NODE_PID=$!

echo "Waiting for node to initialize..."
sleep 5

echo "Deploying MedChain smart contracts..."
npx hardhat ignition deploy ignition/modules/MedChain.js --network localhost > deploy_output.log

echo "Deployment complete."
echo "Hardhat Node PID: $NODE_PID"
echo "Keep this node running while executing Python scripts."
