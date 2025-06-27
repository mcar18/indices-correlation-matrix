# plot_sector_correlation.py
#!/usr/bin/env python3
"""
plot_sector_correlation.py

Scan `supporting files/csv/` for all “sector_etf_correlation_*.csv”, and for each:
  • Plot a blue–white–red heatmap with industry labels
  • Infer title from filename
  • Save as PNG in `supporting files/png/` (overwriting existing)
"""
import os
import sys
from glob import glob
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# Map tickers → industry names
INDUSTRY_LABELS = {
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
CSV_DIR = os.path.join("supporting files", "csv")
PNG_DIR = os.path.join("supporting files", "png")

# ensure png directory exists
os.makedirs(PNG_DIR, exist_ok=True)

def derive_title(stem: str) -> str:
    s = stem.lower()
    if "annual" in s:
        return "Annual % Correlation"
    if "yoy" in s or "year" in s:
        return "Year-over-Year % Correlation"
    if "volatility" in s or "vol" in s:
        return "Volatility Correlation"
    return "Daily % Correlation"

def plot_one(csv_path: str):
    stem = os.path.splitext(os.path.basename(csv_path))[0]
    title = derive_title(stem)
    out_png = os.path.join(PNG_DIR, f"{stem}.png")

    # remove old if exists
    if os.path.exists(out_png):
        os.remove(out_png)

    corr = pd.read_csv(csv_path, index_col=0)
    if corr.shape[0] != corr.shape[1]:
        print(f"⚠️ Skipping {csv_path}: not square {corr.shape}", file=sys.stderr)
        return

    tickers = corr.columns.tolist()
    labels = [INDUSTRY_LABELS.get(t, t) for t in tickers]

    fig, ax = plt.subplots(figsize=(10, 8))
    im = ax.imshow(corr.values, cmap="bwr", vmin=-1, vmax=1)
    ax.set_xticks(np.arange(len(labels)))
    ax.set_yticks(np.arange(len(labels)))
    ax.set_xticklabels(labels, rotation=45, ha="right")
    ax.set_yticklabels(labels)
    for i in range(len(labels)):
        for j in range(len(labels)):
            ax.text(j, i, f"{corr.iat[i,j]:.2f}", ha="center", va="center", fontsize="small")

    cbar = fig.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
    cbar.set_label("Correlation", rotation=270, labelpad=15)
    plt.title(title)
    plt.tight_layout()

    fig.savefig(out_png, format="png")
    plt.close(fig)
    print(f"✅ Saved heatmap: {out_png}")


def main():
    # clear old PNGs
    for f in glob(os.path.join(PNG_DIR, "*.png")):
        os.remove(f)

    csvs = sorted(glob(os.path.join(CSV_DIR, "sector_etf_correlation_*.csv")))
    if not csvs:
        print(f"No CSV files found in {CSV_DIR}", file=sys.stderr)
        sys.exit(1)

    for path in csvs:
        plot_one(path)

if __name__ == "__main__":
    main()
