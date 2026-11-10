# Dataset documentation

## Source and intended use

The dataset accompanies the paper *Fishing for Phishers: Learning-Based Phishing Detection in Ethereum Transactions* (ACM DLT, 2026). It contains Ethereum transaction records and a binary phishing label. The original records were collected through Etherscan, and known phishing addresses were sourced from the [Scams on Ethereum](https://github.com/YNclusk/scamsonethereum) repository as described in the paper.

## Access

Full archive: **ADD ZENODO DOI URL**. The file is not included in this GitHub repository.

Expected proposed archive name: `fishing-for-phishers-ethereum-transactions-v1.0.csv.zip`. Replace this with the actual published filename if different.

## Schema

See [`schema.json`](schema.json) for the 24 columns present in the supplied CSV header. Blank values are possible in some columns. The schema is based on the shared header and a few example rows, **not a complete audit of the dataset**.

`label`: `1` phishing, `0` benign (per the paper). Ethereum `value` and related large integers must not be read through binary floating point if exact precision matters.

## Paper-reported dataset statistics

- Total transactions: 3,359,325
- Phishing transactions: 671,865
- Benign transactions: 2,687,460
- Known phishing addresses in the source list: 7,915

These values require verification against the actual archive before asserting that the release is identical to the experimental corpus.

## Label and evaluation cautions

The paper describes labeling transactions involving verified phishing addresses and then classifying Ethereum addresses using a GCN. Document the precise mapping from transaction-level labels to node labels, how repeated transactions and duplicate hashes are handled, and whether training/testing splits are address-disjoint or chronological before publishing a benchmark-ready release. A benign label indicates absence of a known association under the labeling procedure, not proof of benignness.

## Missing release metadata to complete

- [ ] Zenodo DOI and exact released filename
- [ ] Actual row count, class counts, date range, and SHA-256 checksum
- [ ] Exact data collection dates and filtering/cleaning steps
- [ ] Redistribution/license assessment for upstream sources
- [ ] Original train/test splits and node-label construction, if available
- [ ] Original feature extraction and model-training code, if available
