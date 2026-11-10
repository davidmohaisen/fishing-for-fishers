"""Research reimplementation of the method described in Alghuried et al. (2026).

Not the authors' original implementation. See implementation/README.md for assumptions.
"""
import argparse
import json
import random
from pathlib import Path

import numpy as np
import pandas as pd
import torch
import torch.nn.functional as F
from sklearn.metrics import accuracy_score, precision_recall_fscore_support
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import MinMaxScaler
from torch_geometric.data import Data
from torch_geometric.nn import GCNConv

IMPLICIT = ["from_tx_cnt", "to_tx_cnt", "total_val_sent", "total_val_received",
            "avg_gas_sent", "avg_gas_received", "mean_hour_sent", "mean_hour_received",
            "std_hour_sent", "std_hour_received", "avg_time_bw_tx", "min_time_bw_tx",
            "max_time_bw_tx", "tx_duration", "weekend_ratio_sent", "weekend_ratio_received"]
EXPLICIT = ["mean_timestamp", "mean_value_sent", "mean_value_received", "mean_gas",
            "mean_gas_price", "mean_gas_used"]


def build_features(df):
    """Aggregate transaction-level fields into node features; retain wei as Python integers."""
    df = df.copy()
    df["from"] = df["from"].fillna("").str.lower()
    df["to"] = df["to"].fillna("").str.lower()
    df = df[df["from"].str.startswith("0x") & df["to"].str.startswith("0x")]
    df["timeStamp"] = pd.to_numeric(df["timeStamp"], errors="coerce")
    for field in ("gas", "gasPrice", "gasUsed"):
        df[field] = pd.to_numeric(df[field], errors="coerce")
    # Convert wei with Python's arbitrary-precision integers, not float64.
    df["value"] = df["value"].map(lambda x: int(str(x)) if pd.notna(x) and str(x).strip() else 0)
    df["label"] = pd.to_numeric(df["label"], errors="coerce")
    df = df.dropna(subset=["timeStamp", "label"])
    df = df[df["label"].isin([0, 1])]
    df["hour"] = pd.to_datetime(df["timeStamp"], unit="s", utc=True).dt.hour
    df["weekend"] = pd.to_datetime(df["timeStamp"], unit="s", utc=True).dt.dayofweek >= 5
    addresses = pd.Index(pd.concat([df["from"], df["to"]]).unique())
    nodes = pd.DataFrame(index=addresses)
    # Transaction-label-to-node-label mapping is NOT specified unambiguously by the paper.
    # This is a proxy: mark a node positive if ANY incident transaction is labeled phishing.
    positive = set(df.loc[df["label"] == 1, "from"]) | set(df.loc[df["label"] == 1, "to"])
    nodes["label"] = nodes.index.isin(positive).astype(int)

    for direction, addr_col, suffix in (("sent", "from", "sent"), ("received", "to", "received")):
        grp = df.groupby(addr_col, sort=False)
        nodes[f"{'from' if direction == 'sent' else 'to'}_tx_cnt"] = grp.size()
        nodes[f"total_val_{suffix}"] = grp["value"].sum().map(lambda v: float(v) / 1e18)
        nodes[f"avg_gas_{suffix}"] = grp["gasUsed"].mean()
        nodes[f"mean_hour_{suffix}"] = grp["hour"].mean()
        nodes[f"std_hour_{suffix}"] = grp["hour"].std()
        nodes[f"weekend_ratio_{suffix}"] = grp["weekend"].mean()

    sent_sorted = df.sort_values(["from", "timeStamp"])
    gaps = sent_sorted.groupby("from")["timeStamp"].diff()
    sent_sorted = sent_sorted.assign(gap=gaps)
    g = sent_sorted.groupby("from")
    nodes["avg_time_bw_tx"] = g["gap"].mean()
    nodes["min_time_bw_tx"] = g["gap"].min()
    nodes["max_time_bw_tx"] = g["gap"].max()
    nodes["tx_duration"] = g["timeStamp"].max() - g["timeStamp"].min()
    # Explicit features in the paper are transaction-level. This node aggregation is an
    # implementation choice required to compare them with address-level GCN labels.
    for name, col, field in (("mean_timestamp", "from", "timeStamp"),
                             ("mean_value_sent", "from", "value"),
                             ("mean_value_received", "to", "value"),
                             ("mean_gas", "from", "gas"),
                             ("mean_gas_price", "from", "gasPrice"),
                             ("mean_gas_used", "from", "gasUsed")):
        series = df.groupby(col)[field].mean()
        if field == "value":
            series = series.map(lambda v: float(v) / 1e18)
        nodes[name] = series
    nodes = nodes.fillna(0)
    node_ids = pd.Series(np.arange(len(nodes)), index=nodes.index)
    edges = np.stack([df["from"].map(node_ids).to_numpy(dtype=np.int64),
                      df["to"].map(node_ids).to_numpy(dtype=np.int64)])
    return nodes, edges


class GCN(torch.nn.Module):
    def __init__(self, n_features, hidden, dropout):
        super().__init__()
        self.conv1 = GCNConv(n_features, hidden)
        self.conv2 = GCNConv(hidden, 2)
        self.dropout = dropout

    def forward(self, data):
        x = self.conv1(data.x, data.edge_index).relu()
        x = F.dropout(x, p=self.dropout, training=self.training)
        return self.conv2(x, data.edge_index)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--csv", required=True, help="Extracted CSV or single-CSV ZIP")
    parser.add_argument("--features", choices=["implicit", "explicit"], default="implicit")
    parser.add_argument("--epochs", type=int, default=100)
    parser.add_argument("--hidden", type=int, default=64)
    parser.add_argument("--dropout", type=float, default=0.5)
    parser.add_argument("--lr", type=float, default=0.01)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--output", default="results/metrics.json")
    args = parser.parse_args()
    random.seed(args.seed); np.random.seed(args.seed); torch.manual_seed(args.seed)
    cols = ["from", "to", "timeStamp", "value", "gas", "gasPrice", "gasUsed", "label"]
    # Loading the full CSV in memory can require substantially more RAM than the CSV size.
    df = pd.read_csv(args.csv, usecols=cols, dtype={"from": "string", "to": "string", "value": "string"}, low_memory=False)
    nodes, edges = build_features(df)
    del df
    selected = IMPLICIT if args.features == "implicit" else EXPLICIT
    y = nodes["label"].to_numpy(dtype=np.int64)
    idx = np.arange(len(y))
    train, test = train_test_split(idx, test_size=0.2, stratify=y, random_state=args.seed)
    scaler = MinMaxScaler().fit(nodes.iloc[train][selected].to_numpy(dtype=np.float64))
    x = scaler.transform(nodes[selected].to_numpy(dtype=np.float64))
    data = Data(x=torch.tensor(x, dtype=torch.float32), edge_index=torch.tensor(edges, dtype=torch.long),
                y=torch.tensor(y, dtype=torch.long))
    model = GCN(len(selected), args.hidden, args.dropout)
    opt = torch.optim.Adam(model.parameters(), lr=args.lr)
    counts = np.bincount(y[train], minlength=2)
    if np.any(counts == 0):
        raise ValueError("Training set must contain both classes")
    weights = torch.tensor(len(train) / (2 * counts), dtype=torch.float32)
    for epoch in range(args.epochs):
        model.train(); opt.zero_grad()
        logits = model(data)
        loss = F.cross_entropy(logits[train], data.y[train], weight=weights)
        loss.backward(); opt.step()
        if (epoch + 1) % 10 == 0 or epoch == 0:
            print(f"epoch={epoch+1} loss={loss.item():.4f}")
    model.eval()
    with torch.no_grad():
        predictions = model(data)[test].argmax(dim=1).cpu().numpy()
    precision, recall, f1, _ = precision_recall_fscore_support(y[test], predictions, average="binary", zero_division=0)
    metrics = dict(accuracy=float(accuracy_score(y[test], predictions)), precision=float(precision),
                   recall=float(recall), f1=float(f1), train_nodes=len(train), test_nodes=len(test),
                   total_nodes=len(y), edges=edges.shape[1], features=args.features,
                   implementation="independent reconstruction; not original authors' code")
    path = Path(args.output); path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(metrics, indent=2) + "\n")
    print(json.dumps(metrics, indent=2))


if __name__ == "__main__":
    main()
