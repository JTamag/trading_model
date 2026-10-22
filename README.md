# Cross-sectional momentum: does ML beat a simple baseline after costs?

Research question: on liquid large-cap stocks, does a machine-learning ranker add
value over a simple momentum baseline and over buy-and-hold, after realistic costs
and with leakage-free validation, and does it hold up in live paper trading?

## Setup
    python -m venv .venv && source .venv/bin/activate    # Windows: .venv\Scripts\activate
    pip install -r requirements.txt

## Run (from this folder)
    python explore.py      # step 1: look at the data (3 figures + key stats)
    python baseline.py     # step 2: momentum baseline vs buy & hold, with costs

The first run downloads prices to data/prices.csv. Delete it to refresh.

## Files
- config.py       all settings (universe, parameters, costs)
- data.py         download + cache
- explore.py      distribution, volatility, autocorrelation
- baseline.py     monthly top-N momentum, trend filter, cost-aware backtest
- log.md  log of every idea tried

## Known limitations (keep this list honest and growing)
- Universe = today's large caps, so survivorship bias inflates results.
- Flat cost per side, weights not drifted between rebalances, no taxes.
- SPY is a research benchmark only. EU retail trades a UCITS equivalent
  (see TRADING_MAP in config.py; verify the ticker in Trading 212).

## Next
Labels (triple barrier), features, purged walk-forward validation, LightGBM ranker,
IC and quintile plots, nightly signal output.