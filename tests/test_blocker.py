"""A BLOCKER stops the run: no forecast, a clear message, and the stop is logged."""
import csv

import pytest

from pipeline.engine import run_pipeline
from run import run_once


def _rewrite(path, fn):
    with path.open(newline="") as f:
        rows = list(csv.DictReader(f))
    fields = list(rows[0].keys())
    rows = fn(rows)
    with path.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields, lineterminator="\n")
        w.writeheader()
        w.writerows(rows)


def _assert_stopped(data, out, check_id, week="2026-W34"):
    code = run_once(data, out, week)
    assert code == 2
    assert not list(out.glob("weekly_report_*.md")), "no report may be written when blocked"
    dq = (out / f"data_quality_{week}.md").read_text()
    assert "RUN STOPPED" in dq and check_id in dq
    with (out / "run_log.csv").open() as f:
        last = list(csv.DictReader(f))[-1]
    assert last["status"] == "blocked" and last["blockers"] != "0" and last["forecast_eur"] == ""


def test_unmapped_stage_stops_the_run(sample_copy, tmp_path):
    def break_stage(rows):
        for r in rows:
            if r["snapshot_week"] == "2026-08-17" and r["stage"] == "Proposal":
                r["stage"] = "Waiting for budget"
                break
        return rows
    _rewrite(sample_copy / "deal_history.csv", break_stage)
    res = run_pipeline(sample_copy)
    assert res.blocked
    assert not res.con.execute("SELECT count(*) FROM information_schema.tables WHERE table_name = 'deal_values'").fetchone()[0]
    _assert_stopped(sample_copy, tmp_path / "out", "dq_unknown_stage_unmapped")


def test_missing_quota_stops_the_run(sample_copy, tmp_path):
    def drop_quota(rows):
        rows[0]["quota_q"] = ""
        return rows
    _rewrite(sample_copy / "reps.csv", drop_quota)
    _assert_stopped(sample_copy, tmp_path / "out", "dq_missing_quota")


def test_week_without_snapshot_stops_the_run(sample_copy, tmp_path):
    _assert_stopped(sample_copy, tmp_path / "out", "dq_snapshot_missing", week="2026-W40")


@pytest.mark.parametrize("week", ["2026-W34"])
def test_warnings_alone_do_not_stop_the_run(sample_copy, tmp_path, week):
    assert run_once(sample_copy, tmp_path / "out", week) == 0
