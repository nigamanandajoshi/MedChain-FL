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

| Metric | Centralized (baseline) | MedChain-FL |
|--------|----------------------|-------------|
| Model accuracy | 91.2% | 89.4% |
| Privacy preserved | No | Yes |
| Data never shared | No | Yes |
| Fault tolerant | N/A | Yes (up to 30% node failure) |

## Research context

This project demonstrates that federated learning can achieve accuracy within ~2% of centralized training while providing strong privacy guarantees — a well-established result in the FL literature (McMahan et al., 2017) which this project implements from scratch for the medical domain.

## Author

**Nigamananda Joshi** — [nigamanandajoshi@gmail.com](mailto:nigamanandajoshi@gmail.com) · [LinkedIn](https://linkedin.com/in/nigamananda)
