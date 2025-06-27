#!/usr/bin/env python3
"""
plot_sector_correlation.py

Auto-detect all CSV files in the current directory (or a subdirectory),
treat each as a square correlation matrix of sector tickers,
and for each produce a labeled heatmap PNG.
"""

import os
import sys
from glob import glob
from typing import Dict

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# ─── TICKER → INDUSTRY MAPPING ────────────────────────────────────────────────
INDUSTRY_LABELS: Dict[str,str] = {
    "XLK":  "Technology",
    "XLF":  "Financials",
    "XLE":  "Energy",
    "XLI":  "Industrials",
    "XLP":  "Consumer Staples",
    "XLU":  "Utilities",
    "XLV":  "Health Care",
    "XLY":  "Consumer Discretionary",
    "XLB":  "Materials",
    "XLRE": "Real Estate",
    "XLC":  "Communication Services",
}
# ────────────────────────────────────────────────────────────────────────────────

def derive_title_and_output(csv_path: str) -> (str, str):
    """
    From "sector_etf_correlation_stooq_full.csv" returns:
      title = "Sector Etf Correlation Stooq Full"
      out_png = "sector_etf_correlation_stooq_full.png"
    """
    base = os.path.basename(csv_path)
    stem, _ = os.path.splitext(base)
    # Title: replace separators with spaces, title-case
    title = stem.replace("_", " ").replace("-", " ").title()
    # Output PNG path
    out_png = f"{stem}.png"
    return title, out_png

def plot_heatmap(
    corr: pd.DataFrame,
    labels: list[str],
    title: str,
    out_png: str
):
    """
    Render and save a heatmap of `corr` with axis labels `labels`.
    """
    fig, ax = plt.subplots(figsize=(10, 8))
    im = ax.imshow(corr.values, cmap="bwr", vmin=-1, vmax=1)

    # Tick marks + labels
    ax.set_xticks(np.arange(len(labels)))
    ax.set_yticks(np.arange(len(labels)))
    ax.set_xticklabels(labels, rotation=45, ha="right")
    ax.set_yticklabels(labels)

    # Annotate each cell
    for i in range(corr.shape[0]):
        for j in range(corr.shape[1]):
            ax.text(
                j, i,
                f"{corr.iat[i,j]:.2f}",
                ha="center", va="center",
                fontsize="small",
                color="black"
            )

    # Colorbar & title
    cbar = fig.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
    cbar.set_label("Correlation", rotation=270, labelpad=15)
    plt.title(title)
    plt.tight_layout()

    # Save
    fig.savefig(out_png, format="png")
    print(f"✅ Saved heatmap: {out_png}")
    plt.close(fig)

def process_csv(csv_path: str):
    # 1) Load the CSV
    corr = pd.read_csv(csv_path, index_col=0)
    # 2) Validate it's a square matrix
    if corr.shape[0] != corr.shape[1]:
        print(f"⚠️  Skipping {csv_path}: not square ({corr.shape})", file=sys.stderr)
        return

    # 3) Derive labels
    tickers = corr.columns.tolist()
    labels = [INDUSTRY_LABELS.get(t, t) for t in tickers]

    # 4) Derive title & output filename
    title, out_png = derive_title_and_output(csv_path)

    # 5) Plot & save
    plot_heatmap(corr, labels, title, out_png)

def main():
    # Optionally take a directory as an argument; otherwise use cwd
    folder = sys.argv[1] if len(sys.argv) > 1 else "."
    pattern = os.path.join(folder, "*.csv")
    csv_files = glob(pattern)

    if not csv_files:
        print(f"No CSV files found in {folder}", file=sys.stderr)
        sys.exit(1)

    for csv in csv_files:
        process_csv(csv)

if __name__ == "__main__":
    main()