#!/usr/bin/env python3
"""
analyze_sector_correlation.py

Auto-detect all correlation-matrix CSVs in a directory, for each:
  • Infer a title from the filename (Daily %, Annual %, YoY %, Volatility)
  • Print the CSV filename and the title
  • Compute and print the top 5 least- and most-correlated sector pairs
"""
import os
import sys
import re
from glob import glob
from typing import List, Tuple

import pandas as pd

# ─── TICKER → INDUSTRY MAPPING ────────────────────────────────────────────────
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
# ────────────────────────────────────────────────────────────────────────────────

def derive_title(stem: str) -> str:
    """Generate a human-friendly title from the CSV stem."""
    s = stem.lower()
    if "annual" in s:
        return "Annual % Correlation"
    if "yoy" in s or "year" in s:
        return "Year-over-Year % Correlation"
    if "volatility" in s or "vol" in s:
        return "Volatility Correlation"
    return "Daily % Correlation"

def flatten_corr(
    corr: pd.DataFrame
) -> List[Tuple[str,str,float]]:
    """Return list of (ticker1, ticker2, corr_val) for each i<j."""
    tickers = corr.columns.tolist()
    pairs = []
    for i in range(len(tickers)):
        for j in range(i+1, len(tickers)):
            pairs.append((tickers[i], tickers[j], corr.iat[i, j]))
    return pairs

def analyze_csv(path: str, top_n: int = 5):
    """Load one CSV and print its filename, title, and top/bottom correlated pairs."""
    base = os.path.basename(path)
    stem = os.path.splitext(base)[0]
    title = derive_title(stem)
    print(f"\n=== {base} ===")
    print(f"Dataset: {base}")
    print(f"Title: {title}\n")

    df = pd.read_csv(path, index_col=0)
    if df.shape[0] != df.shape[1]:
        print(f"⚠️  Skipping {base}: not a square matrix ({df.shape})\n")
        return

    pairs = flatten_corr(df)
    dfp = pd.DataFrame(pairs, columns=["Sector1","Sector2","Correlation"])

    least = dfp.nsmallest(top_n, "Correlation")
    most  = dfp.nlargest(top_n,  "Correlation")

    # Map to industry names
    least["Sector1"] = least["Sector1"].map(lambda t: INDUSTRY_LABELS.get(t, t))
    least["Sector2"] = least["Sector2"].map(lambda t: INDUSTRY_LABELS.get(t, t))
    most ["Sector1"] = most ["Sector1"].map(lambda t: INDUSTRY_LABELS.get(t, t))
    most ["Sector2"] = most ["Sector2"].map(lambda t: INDUSTRY_LABELS.get(t, t))

    print(f"Top {top_n} least-correlated pairs:")
    print(least.to_string(index=False))
    print(f"\nTop {top_n} most-correlated pairs:")
    print(most.to_string(index=False))
    print()

def main():
    folder = sys.argv[1] if len(sys.argv) > 1 else "."
    csvs = sorted(glob(os.path.join(folder, "*.csv")))
    if not csvs:
        print(f"No CSV files found in {folder}", file=sys.stderr)
        sys.exit(1)

    for path in csvs:
        analyze_csv(path)

if __name__ == "__main__":
    main()