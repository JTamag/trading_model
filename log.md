# Experiment log



| # | Date | What changed | Key result (net of costs) | Kept? | Notes |
|---|------|--------------|---------------------------|-------|-------|
| 1 | 2026-10-22 | Baseline: top 10 by 6m-1m momentum, monthly, 20 bps/side, 40 large caps, 2010-2026 | Mom net: CAGR 20.1%, Sharpe 1.03, MaxDD -30.2%. Trend-filter variant: 13.0%, 0.84, -30.4%. SPY: 14.9%, 0.91, -33.7% | Baseline kept; trend filter rejected | Survivorship-biased universe. Turnover 6.8x/yr |
| 2 | 2026-10-22 | Added equal-weight universe benchmark (no strategy change) | EW universe: CAGR 18.1%, Sharpe 1.10, MaxDD -31.5% | Kept as benchmark | Most of the gap vs SPY is the stock list. Momentum Sharpe not better than EW. EW line assumes zero costs |



## Decisions and rejected ideas
 
- **Trend filter (200d SPY average, month-end check): rejected.** Gave up about 7 points of CAGR and did not reduce max drawdown (-30.4% vs -30.2%). The 2020 crash was too fast for a month-end rule and the filter sat in cash through the rebounds. Do not re-tune it on this data. If it is revisited, log each variant as a new configuration and update the counter above.
## Bar the ML model must beat (net of costs, out of sample)
 
1. Equal-weight universe (CAGR 18.1%, Sharpe 1.10)
2. Plain momentum baseline (CAGR 20.1%, Sharpe 1.03)
3. Buy & hold SPY (CAGR 14.9%, Sharpe 0.91)
Beating SPY alone is not evidence of anything, because the universe is hindsight-picked.
 
## Holdout
 
`HOLDOUT_START = "2024-01-01"` (to be added to `config.py`). Do not evaluate model results on data after this date until the final holdout stage.