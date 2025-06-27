#!/usr/bin/env python3
"""
market_indices_correlation_matrix.py

Download ~10 years of daily Close prices for all 11 GICS sector ETFs from Stooq,
compute six different 'views' of returns/volatility, and for each view write out:

  • supporting files/csv/sector_etf_<view>_returns.csv
  • supporting files/csv/sector_etf_correlation_<view>.csv

Views:
  - daily       : day-over-day % returns
  - monthly     : month-end % returns
  - quarterly   : quarter-end % returns
  - yoy         : rolling 252-day % returns
  - volatility  : |daily % returns|
  - rolling     : last 60 trading days of daily % returns

Old CSVs are purged at the start of each run.
"""
import os
import logging
from datetime import datetime, timedelta

import pandas as pd
from pandas_datareader import data as pdr

# ─── Configuration ─────────────────────────────────────────────────────────────
SECTORS        = ["SPY","XLK","XLF","XLE","XLI","XLP","XLU","XLV","XLY","XLB","XLRE","XLC"]
LOOKBACK_DAYS  = 3650         # target ~10 years
VIEWS          = ["daily", "monthly", "quarterly", "yoy", "volatility", "rolling"]
WINDOW_DAYS    = 5           # for the rolling-window view
CSV_DIR        = os.path.join("supporting files", "csv")
# ───────────────────────────────────────────────────────────────────────────────

# Ensure target directory exists
os.makedirs(CSV_DIR, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
    datefmt="%H:%M:%S",
)

def fetch_close(ticker: str, start: datetime, end: datetime) -> pd.Series:
    """Fetch daily Close prices for `ticker` from Stooq."""
    df = pdr.DataReader(ticker, "stooq", start, end)
    return df["Close"].sort_index()

def compute_view(df: pd.DataFrame, view: str) -> pd.DataFrame:
    """
    Transform the price DataFrame `df` into one of the requested views:
      - daily      : df.pct_change()
      - monthly    : df.resample('M').last().pct_change()
      - quarterly  : df.resample('Q').last().pct_change()
      - yoy        : df.pct_change(periods=252)
      - volatility : |df.pct_change()|
      - rolling    : last WINDOW_DAYS of df.pct_change()
    """
    if view == "daily":
        return df.pct_change(fill_method=None).dropna()
    if view == "monthly":
        return df.resample("M").last().pct_change().dropna()
    if view == "quarterly":
        return df.resample("Q").last().pct_change().dropna()
    if view == "yoy":
        return df.pct_change(periods=252).dropna()
    if view == "volatility":
        return df.pct_change(fill_method=None).abs().dropna()
    if view == "rolling":
        # rolling-window correlation: slice to most recent WINDOW_DAYS
        ret = df.pct_change(fill_method=None).dropna()
        return ret.tail(WINDOW_DAYS)
    raise ValueError(f"Unknown view: {view}")

def main():
    # 1) Purge any old CSVs
    for fname in os.listdir(CSV_DIR):
        if fname.endswith(".csv"):
            os.remove(os.path.join(CSV_DIR, fname))

    # 2) Fetch raw price data
    end   = datetime.today()
    start = end - timedelta(days=LOOKBACK_DAYS)
    prices = {}
    for sym in SECTORS:
        logging.info("Fetching %s …", sym)
        try:
            prices[sym] = fetch_close(sym, start, end)
        except Exception as e:
            logging.error("Failed to fetch %s: %s", sym, e)

    df_prices = pd.DataFrame(prices).dropna(how="all").sort_index()
    logging.info(
        "Price data from %s to %s (%d rows)",
        df_prices.index.min().date(),
        df_prices.index.max().date(),
        len(df_prices),
    )

    # 3) Compute each view, save returns & correlation
    for view in VIEWS:
        logging.info("Processing view: %s", view)
        df_view = compute_view(df_prices, view)

        # 3a) Save the full time-series
        rs_csv = os.path.join(CSV_DIR, f"sector_etf_{view}_returns.csv")
        df_view.to_csv(rs_csv)
        logging.info("  → Saved returns to %s", rs_csv)

        # 3b) Compute & save the 11×11 correlation matrix
        corr     = df_view.corr()
        corr_csv = os.path.join(CSV_DIR, f"sector_etf_correlation_{view}.csv")
        corr.to_csv(corr_csv)
        logging.info("  → Saved correlation to %s", corr_csv)

if __name__ == "__main__":
    main()