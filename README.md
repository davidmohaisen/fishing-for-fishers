# Fishing for Phishers

**Learning-Based Phishing Detection in Ethereum Transactions**

Companion repository for the peer-reviewed article:

> Ahod Alghuried, Abdulaziz Alghamdi, Ali Alkinoon, Soohyeon Choi, Khalid Alquonus, Manar Mohaisen, and David Mohaisen. **Fishing for Phishers: Learning-Based Phishing Detection in Ethereum Transactions.** *Distributed Ledger Technologies: Research and Practice*, 6(1), Article 2, pp. 1–23, 2026. https://doi.org/10.1145/3786202

## Overview

The paper investigates phishing detection on Ethereum by comparing **explicit transaction attributes** with **implicit address-level behavioral and graph-derived features**, using graph convolutional networks (GCNs). It describes transaction collection through Etherscan and labels informed by a publicly available collection of known phishing addresses.

## Dataset

The paper reports **3,359,325 transactions**: **671,865 labeled phishing** and **2,687,460 labeled benign**, with **7,915 known phishing addresses** in the source collection. These are *reported paper figures*, not counts independently verified from the released archive.

**Dataset on Zenodo:** [ADD DATASET DOI LINK AFTER PUBLICATION](https://zenodo.org/)

**Download:** Obtain the full compressed CSV from the Zenodo record. The large dataset is deliberately not tracked in Git.

The transaction CSV has 24 columns; see [dataset/schema.json](dataset/schema.json) and [dataset/README.md](dataset/README.md). Labels in the shared CSV example are `0` (benign) and `1` (phishing). These labels describe transactions; the paper's GCN classification is at the address/node level. The exact transaction-to-node label mapping and splits should be documented with the experimental artifacts before claiming end-to-end reproduction.

## Quick start

Requires Python 3.9+; utilities use only the standard library.

```bash
# Check the archive or extracted CSV against the documented schema
python scripts/validate.py /path/to/fishing-for-phishers-ethereum-transactions-v1.0.csv.zip

# Preview the first 10 data rows without extracting the entire ZIP
python scripts/preview.py /path/to/fishing-for-phishers-ethereum-transactions-v1.0.csv.zip --rows 10
```

For a full count and label distribution (which may take time for a multi-GB CSV):

```bash
python scripts/validate.py /path/to/dataset.csv.zip --full
```

The lightweight validation scripts do not modify the dataset. An **independent, paper-inspired GCN implementation** is available in [implementation/](implementation/README.md); it is not the original authors' code or a verified reproduction.

## Repository structure

```text
fishing-for-phishers/
├── README.md
├── CITATION.cff
├── .gitignore
├── dataset/
│   ├── README.md
│   └── schema.json
├── implementation/
│   ├── train_gcn.py
│   ├── requirements.txt
│   └── README.md
├── scripts/
│   ├── preview.py
│   └── validate.py
└── experiments/
    └── README.md
```

## Provenance

- Ethereum transaction records: [Etherscan](https://etherscan.io/), as described in Section 3.1 of the paper.
- Source collection of known phishing addresses: [YNclusk/scamsonethereum](https://github.com/YNclusk/scamsonethereum).
- The paper describes verification using transaction histories and Etherscan community reports.

**Interpretation caution:** A `0` label means no known phishing association under the paper's labeling procedure; it is not a guarantee that an address or transaction is free from malicious activity. Refer to the paper for the methodology and limitations.

## Reproducibility status

This repository provides dataset metadata, lightweight validation tools, and an **independent research implementation** of the GCN approach described in the paper. It does **not** include the original authors' experimental code, verified node labels, original train/test splits, or trained model checkpoints. See [implementation/README.md](implementation/README.md) for methodological assumptions and limitations.

## License and reuse

A dataset license should be stated on the Zenodo record after verifying redistribution rights for any third-party material. Code licensing should be chosen by the repository maintainers. No license is granted by this repository unless one is explicitly added.

## Contact

For scholarly questions, refer to the corresponding author and contact details in the published article.
