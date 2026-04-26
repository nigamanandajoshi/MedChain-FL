# Contributing to MedChain-FL

MedChain-FL is an open-source privacy-preserving federated 
learning system for distributed medical data. Contributions 
that improve correctness, performance, or extend functionality 
are welcome.

---

## Setup

```bash
git clone https://github.com/nigamanandajoshi/MedChain-FL
cd MedChain-FL
pip install -r requirements.txt
```

## Running locally

```bash
# Terminal 1 — start the aggregator
python aggregator.py --rounds 10 --min-nodes 2

# Terminal 2 — start node 0
python client.py --node-id 0 --data-path data/hospital_a/

# Terminal 3 — start node 1
python client.py --node-id 1 --data-path data/hospital_b/
```

---

## Project structure
MedChain-FL/
├── aggregator.py     # Central coordinator — FedAvg logic
├── client.py         # Node — local training + gradient sending
├── model.py          # Shared model architecture
├── data/             # Sample data for each simulated node
└── requirements.txt

---

## Areas open for contribution

| Area | Difficulty | Description |
|------|-----------|-------------|
| Differential privacy | Medium | Add noise to gradients before transmission (DP-SGD) |
| Secure aggregation | Hard | Encrypt gradients so aggregator can't read individual updates |
| Async aggregation | Medium | Remove round synchronisation — nodes update independently |
| More datasets | Easy | Add support for CIFAR-10, ChestX-ray14 as FL benchmarks |
| Benchmarking suite | Medium | Automated accuracy vs centralized baseline comparison |
| gRPC transport | Medium | Replace socket communication with gRPC for production use |
| Docker setup | Easy | Containerise each node for reproducible multi-node testing |

---

## Contribution workflow

1. Fork the repository
2. Create a branch: `git checkout -b feature/your-feature-name`
3. Make your changes
4. Test: run a full federated training loop and verify aggregation completes
5. Open a Pull Request with a clear description of what changed and why

## Code style

- Follow PEP 8
- Type hints on all function signatures
- Docstrings on all classes and public functions
- No hardcoded paths — use argparse or config files

---

## Questions

Open an issue with the `question` label or reach out at
nigamanandajoshi@gmail.com
