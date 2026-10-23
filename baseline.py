""" Baseline - no ML yet

Run: python baseline.py

Strategy : At the end of the month, rank stocks by their trailing return, 
hold the top TOP_N equal-weighted for the next month.
Optional: If the benchmark is below its long-term average go to cash.

Simplifications to be removed later on:
    * weights are held constant between rebalances , e.g. drift is rebalanced for free.
    Understating turnover.
    * Costs are currently a bps per side.Real spreads vary by stock and day.
    * No taxes.
    * Survivorship bias.

"""

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

import config as C
from data import get_prices


# Signals 
def month_end_dates(index:pd.DatetimeIndex) -> pd.DatetimeIndex:
    """Last day of each calendar month present in the index"""
    s = index.to_series()
    return pd.DatetimeIndex(s.groupby([s.index.year,s.index.month]).max().values)

def momentum_signal(prices: pd.DataFrame, lookback:int,skip:int) -> pd.DataFrame:
    """ Return from (t-skip-lookback) to (t-skip). Uses only data up to day t"""
    return prices.shift(skip) / prices.shift(skip+lookback)-1

def target_weights(prices, universe,top_n,lookback,skip,benchmark=None, trend_window=None):
    """Weights decided at the close of each month-end. NaN on all other days."""
    mom = momentum_signal(prices[universe],lookback,skip)
    trend_ok = None

    if benchmark is not None and trend_window:
        b = prices[benchmark]
        trend_ok = b > b.rolling(trend_window).mean()

    W = pd.DataFrame(np.nan,index=prices.index,columns=universe)
    for d in month_end_dates(prices.index):
        W.loc[d] = 0.0
        if trend_ok is not None and not trend_ok.loc[d]:
            continue #downtrend : opt for cash
        scores = mom.loc[d].dropna()
        if len(scores) < top_n:
            continue # not enough info : opt for cash
        W.loc[d,scores.nlargest(top_n).index] = 1.0/top_n

    return W

# Backtest

def backtest(prices: pd.DataFrame, W : pd.DataFrame, cost_bps : float, delay : int) -> pd.DataFrame:
    """ Daily gross and net returns.
        Weights chosen at the close of day t only become positions `delay` rows later
        (shift), so the strategy never trades on information it would not have had.
    """
    rets = prices[W.columns].pct_change().fillna(0.0)
    pos = W.ffill().fillna(0.0).shift(delay).fillna(0.0)
    gross = (pos * rets).sum(axis = 1)
    turnover = pos.diff().abs().sum(axis=1).fillna(0.0)
    net = gross - turnover * cost_bps/1e4
    return pd.DataFrame({"gross": gross, "net": net,"turnover":turnover})


# Metrics

def perf_stats(daily : pd.Series, turnover: pd.Series | None = None) -> dict:
    eq = (1+daily).cumprod()
    years = len(daily)/252
    out = {
        "CAGR": eq.iloc[-1] ** (1 / years) - 1,
        "Vol": daily.std() * np.sqrt(252),
        "Sharpe": daily.mean() / daily.std() * np.sqrt(252) if daily.std() > 0 else np.nan,
        "MaxDD": (eq / eq.cummax() - 1).min(),
    }

    if turnover is not None:
        out["Turnover/yr"] = turnover.sum() / years

    return out

def run(prices: pd.DataFrame) -> tuple[pd.DataFrame,pd.DataFrame]:
    """Run all variants"""
    universe = [c for c in prices.columns if c!= C.BENCHMARK]

    W_plain = target_weights(prices, universe, C.TOP_N, C.LOOKBACK, C.SKIP)
    W_trend = target_weights(prices, universe, C.TOP_N, C.LOOKBACK, C.SKIP, benchmark= C.BENCHMARK,trend_window= C.TREND_WINDOW)

    bt_plain = backtest(prices,W_plain,C.COST_BPS_PER_SIDE,C.DELAY)
    bt_trend = backtest(prices, W_trend,C.COST_BPS_PER_SIDE,C.DELAY)

    daily = pd.DataFrame({
        "Momentum (no costs)": bt_plain["gross"],
        "Momentum (with costs)": bt_plain["net"],
        "Momentum + trend filter (with costs)": bt_trend["net"],
        f"Buy & hold {C.BENCHMARK}": prices[C.BENCHMARK].pct_change().fillna(0.0),
    })
    turnover = {
        "Momentum (no costs)": bt_plain["turnover"],
        "Momentum (with costs)": bt_plain["turnover"],
        "Momentum + trend filter (with costs)": bt_trend["turnover"],
    }

    # Comparisons over the same window: from the first day any strategy holds stocks

    first_pos = bt_plain.index[(bt_plain["gross"] != 0).argmax()]
    daily = daily.loc[first_pos:]
    table = pd.DataFrame({k:perf_stats(daily[k],turnover.get(k,None)[daily.index] if k in turnover else None) for k in daily})

    return daily, table.T


# Main
def main() -> None:
    prices = get_prices()
    daily,table = run(prices)
    C.FIG_DIR.mkdir(exist_ok=True)

    fmt = table.copy()

    for col in ["CAGR","Vol","MaxDD"]:
        fmt[col] = fmt[col].map("{:.1%}".format)
    fmt["Sharpe"] = fmt["Sharpe"].map("{:.2f}".format)
    if "Turnover/yr" in fmt:
        fmt["Turnover/yr"] = fmt["Turnover/yr"].map(lambda x : "" if pd.isna(x) else f"{x:.1f}x")

    print(f"\nPeriod: {daily.index[0].date()} to {daily.index[-1].date()}")
    print(f"Cost per side: {C.COST_BPS_PER_SIDE} bps | Top {C.TOP_N} | "
          f"lookback {C.LOOKBACK}d skip {C.SKIP}d\n")
    print(fmt.to_string())
    print("\nReminder: the universe has survivorship bias, so strong numbers are NOT evidence of edge.") 

    eq = (1+daily).cumprod()
    fig,ax = plt.subplots(2,1,figsize=(12,8),sharex = True,height_ratios=[3,1.5])
    eq.plot(ax=ax[0],logy=True)
    ax[0].set_title("Equity curves (start = 1, log scale)")
    (eq / eq.cummax() - 1).plot(ax=ax[1], legend=False)
    ax[1].set_title("Drawdowns")
    fig.tight_layout()
    fig.savefig(C.FIG_DIR / "baseline_equity.png", dpi=130)
    print(f"Figure saved to {C.FIG_DIR / 'baseline_equity.png'}")
    plt.show()

if __name__ == "__main__":
    main()