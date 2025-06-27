#!/usr/bin/env python3
"""
market_indices_correlation_matrix.py

Download ~10 years of daily Close prices from Stooq for all 11 GICS sector ETFs,
compute four different 'views' (daily returns, annual returns, YoY returns, volatility),
and for each view write out:
  • supporting files/csv/sector_etf_<view>_returns.csv
  • supporting files/csv/sector_etf_correlation_<view>.csv
Existing CSVs are cleared at the start of each run.
"""

import os
import logging
from datetime import datetime, timedelta

import pandas as pd
from pandas_datareader import data as pdr

# ─── Configuration ─────────────────────────────────────────────────────────────
SECTORS       = ["XLK","XLF","XLE","XLI","XLP","XLU","XLV","XLY","XLB","XLRE","XLC"]
LOOKBACK_DAYS = 3650   # ~10 years
VIEWS         = ["daily", "annual", "yoy", "volatility"]
CSV_DIR       = os.path.join("supporting files", "csv")
# ───────────────────────────────────────────────────────────────────────────────

# Ensure output directory exists
os.makedirs(CSV_DIR, exist_ok=True)

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
    Transform price DataFrame `df` into one of the four views:
      - daily:       day-over-day pct_change
      - annual:      year-end pct_change
      - yoy:         rolling 252-day pct_change
      - volatility:  absolute daily pct_change
    """
    if view == "daily":
        return df.pct_change(fill_method=None).dropna()
    if view == "annual":
        return df.resample("Y").last().pct_change().dropna()
    if view == "yoy":
        return df.pct_change(periods=252).dropna()
    if view == "volatility":
        return df.pct_change(fill_method=None).abs().dropna()
    raise ValueError(f"Unknown view: {view}")

def main():
    # 1) Clear out old CSVs
    for f in os.listdir(CSV_DIR):
        if f.endswith(".csv"):
            os.remove(os.path.join(CSV_DIR, f))

    # 2) Fetch raw prices
    end   = datetime.today()
    start = end - timedelta(days=LOOKBACK_DAYS)
    data  = {}
    for sym in SECTORS:
        logging.info("Fetching %s…", sym)
        try:
            data[sym] = fetch_close(sym, start, end)
        except Exception as e:
            logging.error("Failed to fetch %s: %s", sym, e)

    df_prices = pd.DataFrame(data).dropna(how="all").sort_index()
    logging.info("Prices from %s to %s (%d rows)",
                 df_prices.index.min().date(),
                 df_prices.index.max().date(),
                 len(df_prices))

    # 3) For each view, save the time-series and its correlation
    for view in VIEWS:
        logging.info("Processing view: %s", view)
        df_view = compute_view(df_prices, view)

        # 3a) Save full time-series
        ts_csv = os.path.join(CSV_DIR, f"sector_etf_{view}_returns.csv")
        df_view.to_csv(ts_csv)
        logging.info("  → saved time-series: %s", ts_csv)

        # 3b) Compute & save correlation matrix
        corr    = df_view.corr()
        corr_csv = os.path.join(CSV_DIR, f"sector_etf_correlation_{view}.csv")
        corr.to_csv(corr_csv)
        logging.info("  → saved correlation: %s", corr_csv)

if __name__ == "__main__":
    main()