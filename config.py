"""Central settings"""
from pathlib import Path

ROOT = Path(__file__).parent
DATA_DIR = ROOT / "data"
FIG_DIR = ROOT / "figures"

START = "2010-01-01"

#Research benchmark, since spy is not available in EU we will watch it but map to VUAA

BENCHMARK = "SPY"
TRADING_MAP = { "SPY" : "VUAA.DE" }

# UoD : liquid large caps
# Fyi: These are companies that are "big" today.
# bias( we are picking stocks that are already big, and not necessarily the ones that will be big in the future)
# Fix later with point-in-time index constituents.
UNIVERSE = [
    "AAPL", "MSFT", "AMZN", "GOOGL", "META", "NVDA", "JPM", "JNJ", "XOM", "PG",
    "V", "UNH", "HD", "KO", "PEP", "WMT", "CSCO", "INTC", "ORCL", "IBM",
    "MRK", "PFE", "T", "VZ", "BAC", "WFC", "CVX", "MCD", "NKE", "DIS",
    "ADBE", "CRM", "TXN", "QCOM", "COST", "ABT", "TMO", "HON", "CAT", "BA",
]

# Momentum baseline
LOOKBACK = 126 #trading days, 6 months
SKIP = 21 #trading days, skip most recent month
TOP_N = 10 #top N stocks to trade
TREND_WINDOW = 200 #market trend filter, hold cash if benchmark < its 200 avg

# Execution model.
# Signal is computed at the close of day t. DELAY=2 means we trade at the close of
# t+1 and first earn the return of day t+2. Conservative on purpose.
DELAY = 2

# Cost per side (each buy or each sell), in basis points. 20 bps = 0.20%.
# Placeholder: spread + FX conversion. Replace with real numbers from your broker.
# If direct mapping is taken in place this value might be altered to 0 since ur trading in euros.
COST_BPS_PER_SIDE = 20