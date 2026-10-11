"""The backtest scores week 6 of each of the past two quarters, and the file matches the run."""
import re
from decimal import Decimal
from pathlib import Path

from conftest import ROOT, SAMPLE
from pipeline.engine import run_pipeline
from run import run_once

D = Decimal


def _money(cell: str) -> Decimal:
    text = cell.strip().replace("−", "-").replace("€", "").replace(",", "").replace("+", "")
    return D(text)


def _pct(cell: str):
    text = cell.strip()
    if text.lower() == "n/a":
        return None
    text = text.replace("−", "-").replace("%", "").replace("+", "")
    return D(text)


def _table_rows(text: str) -> list[dict]:
    rows = []
    for line in text.splitlines():
        if not re.match(r"^\| Q\d", line):
            continue
        cells = [c.strip() for c in line.strip("|").split("|")]
        quarter, as_of, forecast, actual, error, error_pct = cells
        rows.append({
            "quarter": quarter,
            "as_of": as_of,
            "forecast": _money(forecast),
            "actual": _money(actual),
            "error": _money(error),
            "error_pct": _pct(error_pct),
        })
    return rows


def test_backtest_matches_pipeline_and_output_file(tmp_path):
    out = tmp_path / "out"
    assert run_once(SAMPLE, out, "2026-W34") == 0
    text = (out / "backtest.md").read_text(encoding="utf-8")
    parsed = _table_rows(text)
    res = run_pipeline(SAMPLE, "2026-W34")
    rows = res.table("SELECT * FROM backtest ORDER BY quarter_start")
    assert len(rows) == 2
    assert len(parsed) == 2
    for got, row in zip(parsed, rows):
        assert got["quarter"] == row["quarter_label"]
        assert row["as_of_label"] in got["as_of"]
        assert got["forecast"] == D(row["forecast_eur"])
        assert got["actual"] == D(row["actual_eur"])
        assert got["error"] == D(row["error_eur"])
        if row["error_pct"] is None:
            assert got["error_pct"] is None
            assert "percent not defined" in text
        else:
            assert got["error_pct"] == D(row["error_pct"])
            assert f"{got['error_pct']:.1f}%" in text
        assert got["error"] == got["forecast"] - got["actual"]
        # The week-6 number is the real forecast, not a second formula.
        sub = run_pipeline(SAMPLE, row["as_of_week"].isoformat())
        assert not sub.blocked
        forecast = sub.one("SELECT forecast FROM team_forecast WHERE team = 'Total'")["forecast"]
        assert D(row["forecast_eur"]) == D(forecast)
        assert got["quarter"] in text
    report = (out / "weekly_report_2026-W34.md").read_text(encoding="utf-8")
    assert "Backtest, week-6 forecast versus actual closed won:" in report
    for row in rows:
        assert row["quarter_label"] in report


def test_committed_backtest_files_match_a_fresh_run(tmp_path):
    out = tmp_path / "out"
    assert run_once(SAMPLE, out, "2026-W34") == 0
    fresh = (out / "backtest.md").read_bytes()
    committed = ROOT / "output" / "backtest.md"
    sample = ROOT / "output" / "sample" / "backtest.md"
    assert committed.is_file() and sample.is_file()
    assert fresh == committed.read_bytes()
    assert fresh == sample.read_bytes()


def test_backtest_sentence_uses_the_file_numbers():
    text = (ROOT / "output" / "backtest.md").read_text(encoding="utf-8")
    assert "Error = forecast − actual" in text
    assert re.search(r"Q[12] 2026", text)
