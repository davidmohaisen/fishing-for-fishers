# Research implementation (independent reconstruction)

This is a **new, independent implementation based on the methodology in** *Fishing for Phishers: Learning-Based Phishing Detection in Ethereum Transactions* (ACM DLT 2026, DOI: 10.1145/3786202). It is **not the authors' original experimental code**, and has **not been verified to reproduce the paper's reported metrics**.

## Implemented

- Directed transaction graph (Ethereum addresses as nodes, transactions as edges)
- All 16 implicit features enumerated in Table 2, including sending/receiving activity, gas usage, hour statistics, inter-transaction intervals, transaction duration, and weekend ratios
- A separate explicit-feature experiment using aggregated transaction attributes
- Min-max normalization (fit on training nodes only)
- Two-layer PyTorch Geometric GCN, ReLU, dropout, weighted cross-entropy
- Stratified 80/20 node split, accuracy, precision, recall and F1

## Important deviations and unresolved details

1. **Labels:** The paper describes transaction labels and node classification but does not provide the exact transaction-to-node label conversion. This reconstruction labels a node positive when *any incident transaction* is positive. This can over-label benign counterparties. **For scientifically valid replication, replace this with verified address-level ground truth.**
2. **Explicit features:** Transaction-level fields are aggregated to node means to fit the node classifier. The exact paper transformation is not specified.
3. **Graph:** Both training and test nodes remain in the same graph (transductive evaluation). This is not a strictly inductive test on previously unseen addresses.
4. **Splits and hyperparameters:** The 80/20 proportion is reported, but the exact random split, hidden size, learning rate, epochs, dropout, and optimizer settings were not established from the supplied preprint. Defaults here are *implementation choices*, not claimed paper settings.
5. **Data scale:** Reading the complete CSV and constructing the graph in memory may require tens of gigabytes of RAM. Begin with a representative sample; full-scale execution needs a high-memory machine or a chunked/distributed preprocessing pipeline.
6. **Temporal leakage:** Features are computed from all available transaction history. Do not claim prospective detection without implementing time-windowed feature computation and temporal evaluation.
7. **Precision:** Wei amounts are parsed as Python integers before converting to ETH for aggregate numerical features. If the input CSV has already lost precision during export, this cannot restore it.
8. **Label prevalence:** The paper reports 671,865 phishing and 2,687,460 benign transactions (20% phishing) but also mentions 7.63% elsewhere. Validate the actual archive and document the discrepancy.

## Install and run

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r implementation/requirements.txt
python implementation/train_gcn.py --csv /path/to/transactions.csv --features implicit
python implementation/train_gcn.py --csv /path/to/transactions.csv --features explicit
```

A ZIP archive containing one CSV may also be supplied directly to pandas.

**Do not describe the output as an exact reproduction of the ACM paper until the original labels, experimental partitions, and configurations are confirmed.**
