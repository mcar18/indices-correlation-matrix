# market_indices_correlation_matrix.py
#!/usr/bin/env python3
"""
market_indices_correlation_matrix.py

Download 10-year daily Close prices from Stooq for all 11 GICS sector ETFs,
compute multiple correlation views (daily, annual, yoy, volatility),
and save each to its own CSV (overwriting existing).
Usage:
  python market_indices_correlation_matrix.py
Each run regenerates and overwrites:
  sector_etf_correlation_daily.csv
  sector_etf_correlation_annual.csv
  sector_etf_correlation_yoy.csv
  sector_etf_correlation_volatility.csv
"""
import os
import logging
from datetime import datetime, timedelta

import pandas as pd
from pandas_datareader import data as pdr

# ─── Configuration ─────────────────────────────────────────────────────────────
SECTORS = [
    "XLK", "XLF", "XLE", "XLI", "XLP",
    "XLU", "XLV", "XLY", "XLB", "XLRE", "XLC",
]
LOOKBACK_DAYS = 3650  # ~10 years
VIEWS = ["daily", "annual", "yoy", "volatility"]
# ───────────────────────────────────────────────────────────────────────────────

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
    datefmt="%H:%M:%S",
)


def fetch_close(ticker: str, start: datetime, end: datetime) -> pd.Series:
    """
    Fetch daily Close prices for `ticker` from Stooq.
    """
    df = pdr.DataReader(ticker, "stooq", start, end)
    return df["Close"].sort_index()


def compute_view(df: pd.DataFrame, view: str) -> pd.DataFrame:
    """
    Transform price DataFrame `df` into the requested `view`:
    - daily: daily percent returns
    - annual: year-end percent returns
    - yoy: rolling 252-day percent returns
    - volatility: absolute daily returns
    """
    if view == "daily":
        return df.pct_change(fill_method=None).dropna()
    if view == "annual":
        return df.resample('Y').last().pct_change().dropna()
    if view == "yoy":
        return df.pct_change(periods=252).dropna()
    if view == "volatility":
        return df.pct_change(fill_method=None).abs().dropna()
    raise ValueError(f"Unknown view: {view}")


def main():
    # Remove old view CSVs
    for v in VIEWS:
        path = f"sector_etf_correlation_{v}.csv"
        if os.path.exists(path):
            os.remove(path)

    end = datetime.today()
    start = end - timedelta(days=LOOKBACK_DAYS)

    # Fetch raw prices
    data = {}
    for sym in SECTORS:
        logging.info("Fetching %s…", sym)
        try:
            data[sym] = fetch_close(sym, start, end)
        except Exception as e:
            logging.error("Failed to fetch %s: %s", sym, e)
    df = pd.DataFrame(data).dropna(how='all').sort_index()

    # Compute and save each view's correlation
    for v in VIEWS:
        view_df = compute_view(df, v)
        corr = view_df.corr()
        out_csv = f"sector_etf_correlation_{v}.csv"
        logging.info("Saving %s", out_csv)
        corr.to_csv(out_csv)

if __name__ == "__main__":
    main()