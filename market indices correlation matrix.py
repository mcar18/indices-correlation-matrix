#!/usr/bin/env python3
"""
market_indices_correlation_stooq_full.py

Download 1-year daily Close prices from Stooq for all 11 GICS sector ETFs,
compute daily returns, and print/save the correlation matrix.
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, Optional

import pandas as pd
from pandas_datareader import data as pdr

# ——— Configuration ——————————————————————————————————————————
SECTORS = [
    "XLK",   # Technology
    "XLF",   # Financials
    "XLE",   # Energy
    "XLI",   # Industrials
    "XLP",   # Consumer Staples
    "XLU",   # Utilities
    "XLV",   # Health Care
    "XLY",   # Consumer Discretionary
    "XLB",   # Materials
    "XLRE",  # Real Estate
    "XLC",   # Communication Services
]
LOOKBACK_DAYS = 3650
# ——————————————————————————————————————————————————————

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
    datefmt="%H:%M:%S",
)

def fetch_close(ticker: str, 
                start: datetime, 
                end: datetime
               ) -> Optional[pd.Series]:
    """
    Fetch daily Close prices for `ticker` from Stooq.
    Returns a pd.Series indexed by date, or None on failure.
    """
    try:
        df = pdr.DataReader(ticker, "stooq", start, end)
        series = df["Close"].sort_index()
        if series.empty:
            raise ValueError("empty series")
        return series
    except Exception as e:
        logging.error("[%s] fetch failed: %s", ticker, e)
        return None

def main():
    end = datetime.today()
    start = end - timedelta(days=LOOKBACK_DAYS)

    # 1) Fetch each series
    data_map: Dict[str, pd.Series] = {}
    for sym in SECTORS:
        logging.info("Fetching %s …", sym)
        s = fetch_close(sym, start, end)
        if s is not None:
            data_map[sym] = s
        else:
            logging.warning(" → %s skipped.", sym)

    if len(data_map) < 2:
        logging.error("Not enough data to compute correlations. Exiting.")
        return

    # 2) Build DataFrame, compute returns
    df = pd.DataFrame(data_map).sort_index()
    returns = df.pct_change().dropna()

    # after building df of raw Close prices:
    print("=== PRICE–LEVEL CORRELATION ===")
    print(df.corr().round(3))

    # after computing returns:
    returns = df.pct_change().dropna()
    print("\n=== DAILY‐RETURN CORRELATION ===")
    print(returns.corr().round(3))

    corr = returns.corr()


    # 3) Correlation matrix
    corr = returns.corr()

    # 4) Output
    pd.set_option("display.precision", 4)
    print("\nDaily‐return correlation matrix:\n", corr, "\n")
    corr.to_csv("sector_etf_correlation_stooq_full.csv")
    logging.info("Correlation matrix saved to sector_etf_correlation_stooq_full.csv")

if __name__ == "__main__":
    main()