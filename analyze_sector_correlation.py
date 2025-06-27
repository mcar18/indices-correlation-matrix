#!/usr/bin/env python3
"""
analyze_sector_correlation.py

Read `sector_etf_correlation.csv`, and print:

  • Top 5 most correlated sector-pairs  
  • Top 5 least correlated sector-pairs

Optionally, you can tweak `TOP_N` or filter by a minimum/maximum threshold.
"""

import pandas as pd

INPUT_CSV = "sector_etf_correlation.csv"
TOP_N     = 5

def main():
    # 1) Load the matrix
    corr = pd.read_csv(INPUT_CSV, index_col=0)

    # 2) Flatten upper triangle (exclude self‐pairs)
    pairs = []
    tickers = corr.columns.tolist()
    for i, t1 in enumerate(tickers):
        for j, t2 in enumerate(tickers):
            if j <= i:
                continue
            pairs.append((t1, t2, corr.iat[i, j]))

    df_pairs = pd.DataFrame(pairs, columns=["Sector1","Sector2","Correlation"])

    # 3) Sort ascending and descending
    least = df_pairs.nsmallest(TOP_N, "Correlation")
    most  = df_pairs.nlargest(TOP_N,  "Correlation")

    # 4) Print
    print(f"\nTop {TOP_N} least-correlated sector pairs:")
    print(least.to_string(index=False))

    print(f"\nTop {TOP_N} most-correlated sector pairs:")
    print(most.to_string(index=False))


if __name__ == "__main__":
    main()