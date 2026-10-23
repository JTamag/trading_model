# Cross-sectional momentum: does ML beat a simple baseline after costs?

Research question: on liquid large-cap stocks, does a machine-learning ranker add
value over a simple momentum baseline and over buy-and-hold, after realistic costs
and with leakage-free validation, and does it hold up in live paper trading?

## Setup
    python -m venv .venv && source .venv/bin/activate    # Windows: .venv\Scripts\activate
    pip install -r requirements.txt

## Run (from this folder)

### 1. Explore data
Look at distribution, rolling volatility, and autocorrelation (generates 3 plots):
```powershell
python explore.py
```

### 2. Run the baseline backtest (interactive check)
Runs the monthly top-N momentum baseline, trend filter, and benchmarks without saving:
```powershell
python baseline.py
```

### 3. Record an experiment
Runs the backtest and automatically records the experiment into `results/exp_NNN_<name>/`:
```powershell
python baseline.py --save <name> --note "<what changed>"
```
Examples:
```powershell
# Save an experiment with notes:
python baseline.py --save shorter_lookback --note "Testing 63d lookback"

# Save an experiment without generating/saving the equity chart:
python baseline.py --save test_costs --note "Changed cost bps" --no-chart
```

The first run downloads prices to `data/prices.csv`. Delete it to refresh.

When an experiment is saved:
1. It creates `results/exp_NNN_<name>/` containing:
   - `config_snapshot.json` (full parameters, git commit, and data fingerprint)
   - `stats.csv` (standardized performance metrics)
   - `output.txt` (console report)
   - `equity.png` (equity curves and drawdowns chart)
2. Appends a tracking row to `results/runs.csv`.
3. Prints a markdown row to copy-paste into `log.md`.

## Files
- `config.py`       all settings (universe, parameters, costs)
- `data.py`         download + cache
- `explore.py`      distribution, volatility, autocorrelation
- `baseline.py`     monthly top-N momentum, trend filter, cost-aware backtest
- `experiment.py`   automatic experiment tracking and snapshot saving
- `log.md`          log of every idea tried and rejected
- `results/`        saved experiment runs and index

## Known limitations (keep this list honest and growing)
- Universe = today's large caps, so survivorship bias inflates results.
- Flat cost per side, weights not drifted between rebalances, no taxes.
- SPY is a research benchmark only. EU retail trades a UCITS equivalent
  (see TRADING_MAP in config.py; verify the ticker in Trading 212).

## Next
Labels (triple barrier), features, purged walk-forward validation, LightGBM ranker,
IC and quintile plots, nightly signal output.

IC and quintile plots, nightly signal output.