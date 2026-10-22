"""First step: Look at the data before modelling things

When running explore.py [TICKER] we'll get three figures, each answering one question:

1. Are returns normally distributed? (histogram + QQ plot)
2. Is risk constant over time? (rolling volatility)
3. Is anything predictable? (autocorrelation of returns and squared returns)

"""

import sys

import matplotlib.pyplot as plt
import numpy as np
from scipy import stats

from config import BENCHMARK, FIG_DIR
from data import get_prices

def main(ticker: str = BENCHMARK) -> None:
    prices = get_prices()
    r = np.log(prices[ticker]).diff().dropna() # daily log returns
    FIG_DIR.mkdir(exist_ok=True)

    # Numbers 
    sigma = r.std()
    beyond_3 = (np.abs(r-r.mean())>3 * sigma ).mean()
    print(f"\n{ticker}: {len(r)} daily returns, {r.index[0].date()} to {r.index[-1].date()}")
    print(f" annualised return (mean*252): {r.mean()*252:6.1%}")
    print(f" annualised volatility: {sigma * np.sqrt(252):6.1%}")
    print(f" skew:                {stats.skew(r):6.2f} (normal= 0)")
    print(f" excess kurtosis:     {stats.kurtosis(r):6.2f} (normal = 0)")
    print(f" days beyond 3 sigma: {beyond_3:6.2%} (normal predicts 0.27%)")
    print(f" Worst 5 days:")
    for d, v in r.nsmallest(5).items():
        print(f"  {d.date()}  {v: 7.2%}")

    # Figure 1 - Distribuition
    fig, ax = plt.subplots(1,2,figsize=(12,4.5))
    ax[0].hist(r,bins=120,density=True,alpha=0.6,label="actual")
    x = np.linspace(r.min(),r.max(),400)
    ax[0].plot(x,stats.norm.pdf(x,r.mean(),sigma),"r",label="normal with the same mean/std")
    ax[0].set_title(f"{ticker} daily log returns")
    ax[0].legend()
    stats.probplot(r,dist= "norm",plot= ax[1])
    ax[1].set_title(f"QQ plot (points off the line at the ends = fat tails)")
    fig.tight_layout()
    fig.savefig(FIG_DIR / f"{ticker}_distribuition.png",dpi=130)

    # Figure 2 - Rolling volatility
    fig, ax = plt.subplots(figsize=(12,4))
    (r.rolling(21).std() * np.sqrt(252)).plot(ax= ax , label="21-day")
    (r.rolling(126).std() * np.sqrt(252)).plot(ax= ax , label="126-day")
    ax.set_title(f"{ticker} rolling annualised volatility (calm and bad regimes)")
    ax.legend()
    fig.tight_layout()
    fig.savefig(FIG_DIR / f"{ticker}_rolling_vol.png",dpi=130)
    
    # Figure 3 - Autocorrelation
    lags = range(1,31)
    band = 1.96 / np.sqrt(len(r))
    fig, ax = plt.subplots(1,2,figsize=(12,4),sharey = True)
    for a, series, name in [(ax[0],r,"returns"),(ax[1],r**2,"squared returns")]:
        a.bar(lags,[series.autocorr(l) for l in lags])
        a.axhline(band,color="r",ls="--")
        a.axhline(-band,color="r",ls="--")
        a.set_title(f"Autocorrelation of {name}")
        a.set_xlabel("lag (days)")
    fig.tight_layout()
    fig.savefig(FIG_DIR / f"{ticker}_autocorr.png",dpi=130)


    print(f"\nFigures saved to {FIG_DIR}")
    plt.show()
if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv)>1 else BENCHMARK)