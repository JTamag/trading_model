"""Download and cache daily adjusted close prices"""
import pandas as pd

from config import BENCHMARK, DATA_DIR, START, UNIVERSE

CACHE = DATA_DIR / "prices.csv"

def get_prices(refresh:bool = False) -> pd.DataFrame:
    """Adjusted close prices, one column per ticker
    The first call downloads from Yahoo Finance and caches to data/prices.csv.
    Later calls read the cache. Pass refresh=True to re-download
    """

    tickers = sorted(set(UNIVERSE + [BENCHMARK]))
    if CACHE.exists() and not refresh:
        return pd.read_csv(CACHE,index_col=0,parse_dates=True)

    import yfinance as yf # imported here so the rest of the code works

    raw = yf.download(tickers,start = START, auto_adjust=True,progress=False)
    prices = raw["Close"]

    if isinstance(prices,pd.Series):
        prices = prices.to_frame(tickers[0])

    prices.index = pd.to_datetime(prices.index).tz_localize(None)
    prices = prices.sort_index().dropna(axis=1,how="all")

    failed = [t for t in tickers if t not in prices.columns]
    if failed:
        print(f"Warning: no data for {failed}")
    DATA_DIR.mkdir(exist_ok=True)
    prices.to_csv(CACHE)
    return prices