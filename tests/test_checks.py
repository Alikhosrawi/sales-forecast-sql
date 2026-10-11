"""Every problem injected into the synthetic data is caught by the right check."""
import csv
import json
from datetime import date, timedelta

import pytest

from conftest import SAMPLE

MANIFEST = json.loads((SAMPLE / "injected_issues.json").read_text())["issues"]
INJECTED = {k: v for k, v in MANIFEST.items() if k.startswith("dq_") and isinstance(v, list)}
RUN_WEEK = date(2026, 8, 17)


def failing_deals(result, check_id):
    check = next(c for c in result.checks if c.check_id == check_id)
    return {r[2] for r in check.failing_rows}


@pytest.mark.parametrize("check_id,deal_ids", sorted(INJECTED.items()))
def test_injected_problem_is_caught_by_its_check(sample_result, check_id, deal_ids):
    assert set(deal_ids) <= failing_deals(sample_result, check_id)


def test_every_injected_problem_type_is_covered():
    expected = {"dq_negative_amount", "dq_missing_amount", "dq_unknown_stage_mapped", "dq_orphan_rep",
                "dq_duplicate_deal", "dq_close_date_in_past"}
    assert expected <= set(INJECTED)


def test_sample_has_warnings_but_no_blockers(sample_result):
    assert not sample_result.blocked
    assert all(c.passed for c in sample_result.checks if c.severity == "BLOCKER")
    assert sum(1 for c in sample_result.checks if not c.passed) >= 6


def _rows(name):
    with (SAMPLE / name).open(newline="") as f:
        return list(csv.DictReader(f))


def _open_now():
    return {r["deal_id"] for r in _rows("deal_history.csv")
            if r["snapshot_week"] == RUN_WEEK.isoformat() and r["stage"] not in ("Closed Won", "Closed Lost")}


def test_stale_deals_match_an_independent_python_count(sample_result):
    created = {r["deal_id"]: date.fromisoformat(r["created_at"]) for r in _rows("deals.csv")}
    last = {}
    for a in _rows("activities.csv"):
        d = date.fromisoformat(a["occurred_at"])
        if d <= RUN_WEEK:
            last[a["deal_id"]] = max(last.get(a["deal_id"], d), d)
    cutoff = RUN_WEEK - timedelta(days=21)
    expected = {d for d in _open_now() if created[d] <= cutoff and (d not in last or last[d] < cutoff)}
    assert expected, "the sample should contain stale deals"
    assert failing_deals(sample_result, "dq_stale_no_activity_21d") == expected


def test_pushed_close_dates_match_an_independent_python_count(sample_result):
    by_deal = {}
    for r in _rows("deal_history.csv"):
        by_deal.setdefault(r["deal_id"], {})[r["snapshot_week"]] = r["close_date"]
    expected = set()
    for deal in _open_now():
        dates = [by_deal[deal][w] for w in sorted(by_deal[deal])]
        if sum(1 for a, b in zip(dates, dates[1:]) if b > a) >= 2:
            expected.add(deal)
    assert expected, "the sample should contain deals pushed 2+ times"
    assert failing_deals(sample_result, "dq_close_date_pushed_2x") == expected


def test_every_fix_is_logged(sample_result):
    log = sample_result.table("SELECT step, deal_id FROM clean_log")
    steps = {(r["step"], r["deal_id"]) for r in log}
    assert ("dedupe", INJECTED["dq_duplicate_deal"][0]) in steps
    assert ("negative_amount", INJECTED["dq_negative_amount"][0]) in steps
    assert ("missing_amount", INJECTED["dq_missing_amount"][0]) in steps
    assert ("orphan_rep", INJECTED["dq_orphan_rep"][0]) in steps
    for d in INJECTED["dq_unknown_stage_mapped"]:
        assert ("stage_alias", d) in steps


def test_cleaned_snapshot_has_one_row_per_deal_and_valid_amounts(sample_result):
    r = sample_result.one("""SELECT count(*) AS n, count(DISTINCT which || deal_id) AS distinct_n,
                                    count(*) FILTER (WHERE amount_eur < 0 OR amount_eur IS NULL) AS bad
                             FROM snap_clean""")
    assert r["n"] == r["distinct_n"]
    assert r["bad"] == 0
