"""The bridge buckets add up to the total change, to the cent, for every week."""
from decimal import Decimal

import pytest

from conftest import SAMPLE
from pipeline.engine import run_pipeline

Q3_WEEKS = [f"2026-W{w}" for w in range(28, 35)]


@pytest.mark.parametrize("week", Q3_WEEKS)
def test_buckets_sum_to_total_change_to_the_cent(week):
    res = run_pipeline(SAMPLE, week)
    t = res.one("SELECT * FROM bridge_totals")
    buckets = res.table("SELECT amount FROM bridge_summary")
    total = sum((Decimal(b["amount"]) for b in buckets), Decimal("0.00"))
    assert total == t["curr_forecast"] - t["prev_forecast"]
    assert t["unexplained"] == Decimal("0.00")


def test_each_deal_change_is_fully_allocated(sample_result):
    bad = sample_result.table("""
        WITH per_deal AS (SELECT deal_id, sum(delta) AS allocated FROM bridge_deals GROUP BY deal_id),
        actual AS (
            SELECT coalesce(c.deal_id, p.deal_id) AS deal_id,
                   coalesce(c.weighted_value, 0) - coalesce(p.weighted_value, 0) AS change
            FROM (SELECT * FROM deal_values WHERE which = 'curr') c
            FULL OUTER JOIN (SELECT * FROM deal_values WHERE which = 'prev') p ON p.deal_id = c.deal_id)
        SELECT a.deal_id, a.change, coalesce(d.allocated, 0) AS allocated
        FROM actual a LEFT JOIN per_deal d USING (deal_id)
        WHERE a.change <> coalesce(d.allocated, 0)""")
    assert bad == []


def test_sample_week_story(sample_result):
    import json
    manifest = json.loads((SAMPLE / "injected_issues.json").read_text())["issues"]
    rows = {(r["bucket"], r["deal_id"]) for r in sample_result.table("SELECT bucket, deal_id FROM bridge_deals")}
    assert ("slipped", manifest["scenario_slipped_to_next_quarter"][0]) in rows
    assert ("pulled_in", manifest["scenario_pulled_into_quarter"][0]) in rows
    assert ("data_fixes", manifest["dq_negative_amount"][0]) in rows


def test_headline_is_generated_from_the_bridge(sample_result):
    h = sample_result.one("SELECT * FROM headline")
    assert h["headline"].startswith("Forecast is €")
    assert "vs last week" in h["headline"]
    direction = "down" if h["total_change"] < 0 else "up"
    assert f"{direction} €" in h["headline"]
