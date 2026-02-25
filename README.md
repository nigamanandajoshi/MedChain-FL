# MedChain-FL: Federated Learning for Thalassemia Detection

## Overview
MedChain-FL is a privacy-preserving federated learning system for thalassemia detection using Complete Blood Count (CBC) data and blood smear images. The system leverages blockchain for secure model aggregation and Azure ML for scalable deployment.

## Features
- **Federated Learning**: Train models across multiple hospitals without sharing raw patient data
- **Blockchain Integration**: Secure and transparent model aggregation using blockchain ledger
- **Hybrid Models**: Combine CBC data and blood smear images for accurate diagnosis
- **Azure ML Pipeline**: Scalable deployment using Azure Machine Learning
- **REST API**: Easy integration with existing hospital systems
- **Interactive Dashboard**: Monitor training progress and model performance

## Project Structure
- `config/`: Configuration files for Azure, logging, and application settings
- `data/`: Hospital-specific datasets (Italy, Pakistan, USA)
- `data_generation/`: Synthetic data generation for testing
- `models/`: Machine learning model definitions
- `data_loaders/`: PyTorch data loaders for different data types
- `training/`: Local training utilities
- `federated/`: Federated learning orchestration and aggregation
- `blockchain/`: Blockchain ledger and smart contracts
- `azure_ml/`: Azure ML pipeline components
- `api/`: REST API server
- `dashboard/`: React-based monitoring dashboard
- `scripts/`: Utility scripts for training and evaluation
- `tests/`: Unit and integration tests
- `notebooks/`: Jupyter notebooks for exploration and visualization
- `docs/`: Documentation
- `deployment/`: Docker and Kubernetes deployment files

## Quick Start

### Installation
```bash
# Create conda environment
conda env create -f environment.yml
conda activate medchain-fl

# Or use pip
pip install -r requirements.txt
pip install -e .
```

### Generate Demo Data
```bash
python scripts/generate_demo_data.py
```

### 1. Setup Ethereum Blockchain (Local Devnet)
Before running the simulation, start the local Hardhat node and deploy the Smart Contracts:
```bash
./start_blockchain.sh
```
*(Keep this terminal open)*

### 2. Generate Demo Patient Data
In a new terminal:
```bash
python generate_data_standalone.py
```

### 3. Run Ethereum-Backed FL Simulation
Execute the full federated learning loop with smart contract governance and on-chain logging:
```bash
python run_fl_standalone.py
```

### (Optional) Run Azure FL Pipeline
```bash
python scripts/run_azure_fl.py
```

### Start API Server
```bash
cd api
python app.py
```

### Start Dashboard
```bash
cd dashboard
npm install
npm start
```

## Documentation
- [Architecture](docs/architecture.md)
- [Setup Guide](docs/setup_guide.md)
- [API Documentation](docs/api_documentation.md)
- [Deployment Guide](docs/deployment.md)

## License
MIT License

## Contributors
Developed for privacy-preserving medical diagnostics research.
