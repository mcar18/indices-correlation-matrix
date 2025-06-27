#!/usr/bin/env python3
"""
market_indices_correlation_av.py

Download 1-year daily Adjusted Close from Alpha Vantage for a set of sector ETFs,
compute daily returns, and print/save the correlation matrix.
"""

import os
import time
import logging
from typing import Dict, Optional

import pandas as pd
from alpha_vantage.timeseries import TimeSeries

# ——— Configuration ——————————————————————————————————————————
SECTORS = [
    "XLK", "XLF", "XLE", "XLI", "XLP",
    "XLU", "XLV", "XLY", "XLB", "XLRE",
]
API_KEY       = os.getenv("ALPHAVANTAGE_API_KEY")
CALLS_PER_MIN = 5
DELAY_SEC     = 60 / CALLS_PER_MIN + 1   # ~13s between calls
# ——————————————————————————————————————————————————————

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
    datefmt="%H:%M:%S",
)

def fetch_av_adj_close(
    ticker: str
) -> Optional[pd.Series]:
    """
    Fetch daily adjusted close prices for the past year via Alpha Vantage.
    Returns a pd.Series indexed by date, or None on failure.
    """
    if not API_KEY:
        logging.error("ALPHAVANTAGE_API_KEY not set in environment.")
        return None

    ts = TimeSeries(key=API_KEY, output_format="pandas", indexing_type="date")
    try:
        data, meta = ts.get_daily_adjusted(symbol=ticker, outputsize="compact")
        # '5. adjusted close' holds the adjusted close
        adj = data["5. adjusted close"].sort_index()
        # keep only last 252 trading days (~1 year)
        return adj.iloc[-252:]
    except Exception as e:
        logging.error("[%s] Alpha Vantage error: %s", ticker, e)
        return None

def main():
    # 1) Fetch each ticker one at a time
    series_map: Dict[str, pd.Series] = {}
    for sym in SECTORS:
        logging.info("Fetching %s …", sym)
        s = fetch_av_adj_close(sym)
        if s is not None and not s.empty:
            series_map[sym] = s
        else:
            logging.warning(" → %s skipped (no data).", sym)
        time.sleep(DELAY_SEC)

    if len(series_map) < 2:
        logging.error("Not enough data to compute correlations. Exiting.")
        return

    # 2) Build DataFrame, compute returns
    df = pd.DataFrame(series_map).sort_index()
    returns = df.pct_change().dropna()

    # 3) Correlation matrix
    corr = returns.corr()

    # 4) Output
    pd.set_option("display.precision", 4)
    print("\nDaily‐return correlation matrix:\n", corr, "\n")
    corr.to_csv("sector_etf_correlation_av.csv")
    logging.info("Correlation matrix saved to sector_etf_correlation_av.csv")

if __name__ == "__main__":
    main()