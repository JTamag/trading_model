# Quant Trading Project Plan

Working plan based on our chat, 7 Oct 2026. This is a learning and research plan, not financial advice. Nothing here is guaranteed to make money.

## 1. Goal

Build a quantitative model that produces daily trading signals, test it honestly, and only then risk real money. The goal is not to beat SPY by trading SPY. The goal is to find out, with rigorous validation, whether a model can beat a simple buy-and-hold of the S&P 500 after costs and tax. Finding "no edge" and being able to explain why is still a strong result for a future quant career.

## 2. Starting situation

- Final-year BSc in Computer Science, based in Portugal.
- Broker: Trading 212 (already have an account).
- Capital: about 1,200 EUR of free money, currently sitting in NBIS (parked for now, not part of the plan yet).
- Mode: signal-only. The model outputs signals, and I place orders manually in Trading 212.
- Style wanted: more active than buy-and-hold.

## 3. Chosen strategy

**Cross-sectional momentum, swing trading on daily bars.**

- Each evening after the market close, rank a universe of 50-100 liquid large-cap stocks using features such as multi-window returns, volatility-adjusted momentum and short-term reversal.
- Buy only the top 3-5 names, hold for roughly 2-10 days (up to a couple of weeks).
- Trend filter: skip new trades when the broad market is in a downtrend (for example, index below its 200-day average).
- Benchmark: S&P 500 buy-and-hold.

Why this one: momentum is among the most documented effects in finance, it needs no speed or API, it limits cost drag compared with intraday, and ranking many stocks gives enough data for ML without overfitting as badly as a single asset.

Avoid: intraday trading, leverage, CFDs, and anything that requires watching charts all day.

## 4. Tickers and instruments

- **Research and benchmark data:** SPY from `yfinance` (longest clean history). Not tradable for EU retail clients, which is why it is not on Trading 212.
- **EUR / UCITS equivalents of the S&P 500** (accumulating): VUAA (Vanguard) or CSPX / SXR8 (iShares). On `yfinance` the Xetra versions usually end in `.DE` (for example `VUAA.DE`). Verify exact tickers by searching, I gave these from memory.
- These funds are built for long holding, so they are the benchmark, not what the model trades.
- **What the model trades:** individual large-cap stocks (US or European), using fractional shares if available on my account.
- Prefer euro-denominated stocks to avoid the currency conversion fee on US stocks.

## 5. Capital plan (small account)

- Ranking a 50-100 stock universe costs nothing. Only the top 3-5 are actually bought.
- Step 1: run the full model on paper (hypothetical portfolio, signals logged).
- Step 2: go live with a small amount using fractional shares in 3-5 positions.
- Alternative if single stocks feel too concentrated: a basket of 5-8 diversified ETFs with slower rotation (weeks to months).
- Risk 0.5-1% of the account per trade. Cap simultaneous positions. Set a maximum-drawdown level at which I pause trading.
- Note: the 1,200 EUR is concentrated in one stock (NBIS) right now. Position-sizing rules like the ones above are exactly what limits that kind of risk once the live phase starts.

## 6. Pipeline stages

1. **Data:** daily OHLCV for the universe and SPY via `yfinance`. Be aware of survivorship bias (use point-in-time index constituents if possible, otherwise document the limitation).
2. **Features:** returns over several windows, volatility, volume changes, momentum, short-term reversal, market-relative strength.
3. **Labels:** triple-barrier (profit target, stop, maximum holding time of about 5-10 days).
4. **Baseline first (no ML):** each month hold the top 10 stocks by 6-month return, skipping the most recent month, with costs included. Compare to buy-and-hold.
5. **ML ranker:** logistic regression, then LightGBM. Keep ML only if it beats the baseline after costs on walk-forward tests.
6. **Backtester:** use `vectorbt` or `backtesting.py` first, then write my own minimal one to understand where look-ahead bias creeps in.
7. **Signal output:** a nightly table with asset, direction, entry, stop, target, position size and reasoning.
8. **Execution:** place orders manually in Trading 212 (use its practice mode first if available) and log every signal and what I actually did.

## 7. Validation rules (non-negotiable)

- Never shuffle or use plain k-fold on time series.
- Walk-forward testing with purging and embargo between train and test.
- Include realistic costs: spread, FX conversion fees on non-euro stocks, slippage.
- Hold out a final test set and touch it once.
- Paper trade for 1-3 months before any real money, and compare live results with the backtest.
- Only go live if live behavior matches the backtest.

## 8. Costs and tax to check

- Trading 212 is commission-free, but spread and FX conversion (roughly 0.15% each way when I last checked, verify the current rate) add up to about 0.3% or more per round trip. The strategy's average gain per trade must clearly exceed this.
- Portuguese tax treatment of short-term gains may be less favorable than long-term holding. Check current rules or ask an accountant before going live.
- Check which instruments are available on my account and whether any are CFD-only. Avoid CFDs.

## 9. Extra data (later, only if the baseline works)

- **News and earnings:** use a news API or filings, run headlines through a language model for a sentiment score, and add it as one more feature column. Most of the immediate price move happens in seconds, so realistic edge is in slower effects such as post-earnings drift. Historical news needs accurate timestamps or the backtest will cheat.
- **Politician trades (STOCK Act disclosures):** available via Capitol Trades, Quiver Quantitative and the official disclosure sites. Weak as a standalone strategy because of the reporting delay (up to 45 days), vague value ranges and mixed evidence on whether copying works. Use only as an optional feature, timestamped by filing date, not trade date.
- **Order book / order flow:** skip. Only matters for very short horizons and is expensive.

## 10. Tools

- Python, Jupyter or VS Code, git repo from day one.
- Libraries: `pandas`, `yfinance`, `scikit-learn`, `lightgbm`, `vectorbt` or `backtesting.py`.
- QuantConnect (free tier) for a second opinion on backtests.
- Alpaca paper account for practicing execution code (check Portugal eligibility).
- Interactive Brokers if I later want live automation in the EU (Python API).

## 11. Roadmap

| Phase | What | Rough time |
| --- | --- | --- |
| 0 | Environment, git repo, pull SPY data, plot returns and look at fat tails | Week 1 |
| 1 | Baseline momentum strategy with costs, benchmark vs S&P 500 | Weeks 2-6 |
| 2 | Features, triple-barrier labels, ML ranker, walk-forward validation | Weeks 6-12 |
| 3 | Nightly signal pipeline and paper trading, signal log | Months 3-5 |
| 4 | Small live portfolio (3-5 positions) if live matches backtest | Month 5 onwards |
| 5 | Optional: news, earnings, politician-trade features | After Phase 4 |

## 12. Open questions to resolve

- Which exact UCITS ticker is available in my Trading 212 account for the benchmark?
- Which stocks support fractional shares, and what is the real spread and FX fee?
- Does Trading 212 currently offer a usable API, or do I stay manual?
- Portuguese tax rules for short-term gains.
- Could this be my final-year dissertation? Ask my department.

## 13. Reading list

- *Advances in Financial Machine Learning* by Marcos Lopez de Prado (triple-barrier labels, purged cross-validation).
- *Machine Learning for Algorithmic Trading* by Stefan Jansen (practical full pipeline).
- For quant interviews: *Heard on the Street* and *A Practical Guide to Quantitative Finance Interviews*.
- Probability, statistics and linear algebra refreshers.

## 14. Next action

Write the starter script: download a configurable list of tickers plus SPY as the benchmark, compute returns, volatility and momentum features, and run the monthly top-10 baseline with costs.
