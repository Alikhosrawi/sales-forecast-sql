"""Weekly sales forecast: one command.

    python run.py                    # latest week in the data, results in output/
    python run.py --week 2026-W33    # a specific week
    python run.py --sample           # rebuild output/sample/ (last week + this week)

Exit code 0 = report written, 2 = stopped by a BLOCKER data-quality check.
"""
from __future__ import annotations

import argparse
import shutil
import sys
from datetime import timedelta
from pathlib import Path

from pipeline.engine import ROOT, run_pipeline
from pipeline.report import append_run_log, write_backtest, write_data_quality, write_report

DEFAULT_DATA = ROOT / "data" / "sample"


def run_once(data_dir: Path, out_dir: Path, week: str | None) -> int:
    out_dir.mkdir(parents=True, exist_ok=True)
    res = run_pipeline(data_dir, week)
    dq = write_data_quality(res, out_dir)
    log = append_run_log(res, out_dir)
    if res.blocked:
        print(f"\nSTOPPED for {res.week_label}: a BLOCKER data-quality check failed. No forecast was produced.")
        for c in res.checks:
            if c.severity == "BLOCKER" and not c.passed:
                for r in c.failing_rows[:10]:
                    print(f"  [{c.check_id}] {r[2] or ''} {r[3]}")
        print(f"Details: {dq.relative_to(Path.cwd()) if dq.is_relative_to(Path.cwd()) else dq}")
        return 2
    report = write_report(res, out_dir)
    backtest = write_backtest(res, out_dir)
    headline = res.one("SELECT headline FROM headline")["headline"]
    warns = sum(1 for c in res.checks if not c.passed)
    print(f"\n{res.week_label}: {headline}")
    print(f"  data checks: {len(res.checks) - warns} passed, {warns} warnings, 0 blockers")
    print(f"  report:      {report}")
    print(f"  backtest:    {backtest}")
    print(f"  run log:     {out_dir / 'run_log.csv'} (git {log['git_commit']})")
    return 0


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="Weekly sales forecast that explains itself.")
    p.add_argument("--week", help="ISO week like 2026-W34 or a date (default: latest snapshot in the data)")
    p.add_argument("--data", type=Path, default=DEFAULT_DATA, help="folder with the CRM CSV files")
    p.add_argument("--out", type=Path, default=ROOT / "output", help="where reports go")
    p.add_argument("--sample", action="store_true", help="rebuild output/sample/ for last week and this week")
    a = p.parse_args(argv)

    if not (a.data / "deal_history.csv").exists():
        if a.data != DEFAULT_DATA:
            p.error(f"no deal_history.csv in {a.data}")
        from generate_data import generate
        print("No data found, generating the synthetic sample (seed 42)...")
        generate(a.data, 42)

    if a.sample:
        out = ROOT / "output" / "sample"
        if out.exists():
            shutil.rmtree(out)
        import duckdb
        latest = duckdb.sql(f"SELECT max(snapshot_week) FROM read_csv('{a.data / 'deal_history.csv'}')").fetchone()[0]
        code = 0
        for w in (latest - timedelta(days=7), latest):   # last week first, so the run log shows the change
            code = max(code, run_once(a.data, out, w.isoformat()))
        sample_bt = out / "backtest.md"
        if sample_bt.exists():
            (ROOT / "output" / "backtest.md").write_bytes(sample_bt.read_bytes())
        return code
    return run_once(a.data, a.out, a.week)


if __name__ == "__main__":
    sys.exit(main())
