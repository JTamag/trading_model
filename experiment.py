"""Experiment tracking: saves runs to results/exp_NNN_name/.

Each saved run folder contains:
    config_snapshot.json   full parameters, git commit, and data fingerprint
    stats.csv              standardized performance metrics table
    output.txt             text report printed to console
    equity.png             the equity curves and drawdowns chart

Also logs each experiment to results/runs.csv for trial-counting and auditability.
"""
import csv
import hashlib
import json
import re
import subprocess
from datetime import date
from pathlib import Path

import pandas as pd

import config as C

RESULTS = C.ROOT / "results"
RUNS_LOG = RESULTS / "runs.csv"


def _git(*args):
    try:
        return subprocess.check_output(
            ["git", *args], cwd=C.ROOT, text=True, stderr=subprocess.DEVNULL
        ).strip()
    except Exception:
        return None


def _data_fingerprint() -> str | None:
    """Short hash of cached prices. Detects if Yahoo adjusted prices changed later."""
    path = C.DATA_DIR / "prices.csv"
    if path.exists():
        return hashlib.sha256(path.read_bytes()).hexdigest()[:12]
    return None


def _next_id() -> int:
    RESULTS.mkdir(exist_ok=True)
    ids = [int(m.group(1)) for p in RESULTS.iterdir() if (m := re.match(r"exp_(\d+)_", p.name))]
    return max(ids, default=0) + 1


def _format_stats_csv(table: pd.DataFrame) -> pd.DataFrame:
    """Formats table matching exp_001 and exp_002 stats.csv exact schema and precision."""
    rows = []
    for strat, row in table.iterrows():
        cagr = f"{row['CAGR']:.3f}" if "CAGR" in row and pd.notna(row["CAGR"]) else ""
        vol = f"{row['Vol']:.3f}" if "Vol" in row and pd.notna(row["Vol"]) else ""
        sharpe = f"{row['Sharpe']:.2f}" if "Sharpe" in row and pd.notna(row["Sharpe"]) else ""
        max_dd = f"{row['MaxDD']:.3f}" if "MaxDD" in row and pd.notna(row["MaxDD"]) else ""
        turnover = ""
        if "Turnover/yr" in row and pd.notna(row["Turnover/yr"]):
            turnover = f"{row['Turnover/yr']:.1f}"

        rows.append({
            "strategy": strat,
            "cagr": cagr,
            "vol": vol,
            "sharpe": sharpe,
            "max_drawdown": max_dd,
            "turnover_per_year": turnover,
        })
    return pd.DataFrame(rows)


def _format_key_result(table: pd.DataFrame) -> str:
    """Builds a one-line summary for log.md."""
    parts = []
    if "Momentum (with costs)" in table.index:
        r = table.loc["Momentum (with costs)"]
        parts.append(f"Mom net: CAGR {r['CAGR']:.1%}, Sharpe {r['Sharpe']:.2f}, MaxDD {r['MaxDD']:.1%}")
    if "Equal-weight universe" in table.index:
        r = table.loc["Equal-weight universe"]
        parts.append(f"EW: CAGR {r['CAGR']:.1%}, Sharpe {r['Sharpe']:.2f}")
    return ". ".join(parts) if parts else "TODO"


def save_run(
    name: str,
    table: pd.DataFrame,
    fig=None,
    console_text: str | None = None,
    note: str = "",
    period: tuple | None = None,
    data_dates: tuple | None = None,
) -> Path:
    RESULTS.mkdir(exist_ok=True)

    exp_id = _next_id()
    slug = re.sub(r"[^a-z0-9]+", "_", name.lower()).strip("_") or "run"
    folder = RESULTS / f"exp_{exp_id:03d}_{slug}"
    folder.mkdir(parents=True, exist_ok=True)

    commit = _git("rev-parse", "--short", "HEAD")
    dirty = bool(_git("status", "--porcelain", "--untracked-files=no"))
    today = date.today().isoformat()
    fingerprint = _data_fingerprint()

    # Determine data dates
    data_start = str(data_dates[0].date()) if data_dates else C.START
    data_end = str(data_dates[1].date()) if data_dates else today
    eval_period_str = f"{period[0].date()} to {period[1].date()}" if period else f"{data_start} to {data_end}"

    # 1. config_snapshot.json (matches exact flat schema of exp_001 and exp_002)
    config_dict = {
        "run_date": today,
        "data_start": data_start,
        "data_end": data_end,
        "evaluation_period": eval_period_str,
        "benchmark": C.BENCHMARK,
        "universe_size": len(C.UNIVERSE),
        "universe": C.UNIVERSE,
        "lookback_days": C.LOOKBACK,
        "skip_days": C.SKIP,
        "top_n": C.TOP_N,
        "rebalance": "month-end",
        "trend_window_days": C.TREND_WINDOW,
        "delay_days": C.DELAY,
        "cost_bps_per_side": C.COST_BPS_PER_SIDE,
        "known_limitations": [
            "survivorship-biased universe (today's large caps)",
            "flat cost per side; weights not drifted between rebalances; no taxes",
        ],
        "experiment": folder.name,
        "git_commit": commit or "uncommitted",
        "variants": list(table.index),
    }
    if note:
        config_dict["change_vs_previous"] = note

    (folder / "config_snapshot.json").write_text(
        json.dumps(config_dict, indent=2), encoding="utf-8"
    )

    # 2. stats.csv (exact matching schema & precision)
    df_stats = _format_stats_csv(table)
    df_stats.to_csv(folder / "stats.csv", index=False)

    # 3. output.txt (named output.txt to match existing experiments)
    if console_text:
        (folder / "output.txt").write_text(console_text, encoding="utf-8")

    # 4. equity.png
    if fig is not None:
        fig.savefig(folder / "equity.png", dpi=130)

    # 5. Append to results/runs.csv
    new_log = not RUNS_LOG.exists()
    with open(RUNS_LOG, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        if new_log:
            writer.writerow(["id", "date", "name", "git_commit", "dirty", "data_fingerprint", "note"])
        writer.writerow([exp_id, today, folder.name, commit, dirty, fingerprint, note])

    rel_folder = folder.relative_to(C.ROOT)
    print(f"\nSaved run to {rel_folder}")
    if commit is None or dirty:
        print("Warning: uncommitted changes (or no git repo). Commit before relying on reproducibility.")

    key_res = _format_key_result(table)
    print("\nPaste into log.md:")
    print(f"| {exp_id} | {today} | {note or name} | {key_res} | TODO | TODO |")

    return folder
