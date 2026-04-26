![Python](https://img.shields.io/badge/python-3.8+-blue)
![PyTorch](https://img.shields.io/badge/PyTorch-2.0+-orange)
![License](https://img.shields.io/badge/license-MIT-green)
# MedChain-FL — Privacy-Preserving Federated Learning for Medical Data

A distributed machine learning system that enables **collaborative model training across isolated medical institutions** without any raw patient data ever leaving its source node.

## The problem it solves

Hospitals and medical research institutions hold valuable patient data, but legal, ethical, and privacy constraints prevent them from pooling this data for joint ML training. MedChain-FL solves this by training locally on each node and sharing only model gradients — never the underlying data.

## Architecture

```
Node A (Hospital A)     Node B (Hospital B)     Node C (Research Lab)
   Local training  ──┐     Local training  ──┤     Local training  ──┐
   (raw data stays)  │     (raw data stays)  │     (raw data stays)  │
                     ▼                       ▼                       ▼
              ┌─────────────────────────────────────────────┐
              │            Aggregator (FedAvg)              │
              │   Weighted average of gradients only        │
              │   Fault-tolerant: continues if node fails   │
              └─────────────────────────────────────────────┘
                           │
                     Global model update
                     broadcast to all nodes
```

## Key technical components

- **Federated Averaging (FedAvg)** — Aggregates model updates using weighted averaging based on each node's dataset size
- **Fault-tolerant node communication** — Aggregator continues training rounds even when a subset of nodes fail or disconnect mid-round
- **Distributed coordination** — Nodes operate asynchronously; the aggregator synchronizes at configurable round boundaries
- **Privacy guarantee** — Raw data never leaves the originating node; only gradient tensors are transmitted

## Tech stack

`Python · PyTorch · Distributed Systems · gRPC / sockets`

## Repository structure
```
MedChain-FL/
├── aggregator.py     # Central coordinator — FedAvg logic
├── client.py         # Node — local training + gradient sending
├── model.py          # Shared model architecture
├── data/             # Sample data for each simulated node
└── requirements.txt
```
## Getting started

```bash
git clone https://github.com/nigamanandajoshi/MedChain-FL
cd MedChain-FL
pip install -r requirements.txt

# Start the aggregator
python aggregator.py --rounds 10 --min-nodes 2

# Start client nodes (in separate terminals or machines)
python client.py --node-id 0 --data-path data/hospital_a/
python client.py --node-id 1 --data-path data/hospital_b/
```

## Results

Benchmarking in progress. The system demonstrates that 
federated training completes successfully across distributed 
nodes with fault-tolerant aggregation. Formal accuracy 
benchmarks against centralized baselines coming soon.
## Research context

This project implements the Federated Averaging (FedAvg) 
algorithm (McMahan et al., 2017) from scratch for the medical 
domain. FL has been shown in literature to achieve accuracy 
within 1–3% of centralized training while providing strong 
privacy guarantees — demonstrating that collaborative ML is 
possible without centralising sensitive data.

This project demonstrates that architecture in a fault-tolerant 
distributed setting, where the aggregator continues training 
rounds even under partial node failure.

> McMahan, B., Moore, E., Ramage, D., Hampson, S., & Agüera y Arcas, B. (2017).
> Communication-Efficient Learning of Deep Networks from Decentralized Data.
> *AISTATS 2017.* https://arxiv.org/abs/1602.05629

## Author

**Nigamananda Joshi** — [nigamanandajoshi@gmail.com](mailto:nigamanandajoshi@gmail.com) · [LinkedIn](https://linkedin.com/in/nigamananda)

## License
MIT License

## Citation
If you use this project in your research:
Nigamananda Joshi. MedChain-FL: Privacy-Preserving
Federated Learning for Medical Data (2024).
github.com/nigamanandajoshi/MedChain-FL
