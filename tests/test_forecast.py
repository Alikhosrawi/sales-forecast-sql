"""The forecast matches values worked out by hand on a five-deal fixture
(see tests/fixtures/tiny/README.md for the arithmetic)."""
import csv
import shutil
from decimal import Decimal

from conftest import TINY
from pipeline.engine import run_pipeline

D = Decimal


def test_forecast_matches_hand_calculation():
    res = run_pipeline(TINY, "2026-W34")
    assert not res.blocked
    values = {r["deal_id"]: r["weighted_value"]
              for r in res.table("SELECT deal_id, weighted_value FROM deal_values WHERE which = 'curr'")}
    assert values == {"T1": D("8000.00"), "T2": D("12000.00"), "T3": D("5000.00"), "T4": D("0.00"), "T5": D("333.30")}
    t = res.one("SELECT * FROM bridge_totals")
    assert t["curr_forecast"] == D("25333.30")
    assert t["prev_forecast"] == D("23400.00")
    total = res.one("SELECT * FROM team_forecast WHERE team = 'Total'")
    assert total["commit_total"] == D("15000.00")
    assert total["closed_won"] == D("5000.00")
    assert total["gap_to_quota"] == D("95000.00")


def test_bridge_matches_hand_calculation():
    res = run_pipeline(TINY, "2026-W34")
    got = {r["bucket"]: r["amount"] for r in res.table("SELECT bucket, amount FROM bridge_summary WHERE amount <> 0")}
    assert got == {"stage_moves": D("2000.00"), "won": D("1000.00"), "slipped": D("-1400.00"), "new": D("333.30")}


def test_defaults_used_when_fewer_than_10_closed_deals():
    res = run_pipeline(TINY, "2026-W34")
    neg = res.one("SELECT * FROM stage_probability WHERE stage = 'Negotiation'")
    assert neg["probability_used"] == D("0.8000")
    assert neg["source"].startswith("default")


def test_historical_win_rate_used_when_10_or_more(tmp_path):
    data = tmp_path / "tiny"
    shutil.copytree(TINY, data)
    # 10 deals closed in Q2 that all reached Negotiation: 7 won, 3 lost -> 70%.
    with (data / "deal_history.csv").open("a", newline="") as f:
        w = csv.writer(f, lineterminator="\n")
        for i in range(10):
            w.writerow([f"H{i}", "2026-05-04", "Negotiation", 1000, "2026-05-20", "commit"])
            w.writerow([f"H{i}", "2026-05-25", "Closed Won" if i < 7 else "Closed Lost", 1000, "2026-05-22",
                        "closed_won" if i < 7 else "closed_lost"])
    with (data / "deals.csv").open("a", newline="") as f:
        w = csv.writer(f, lineterminator="\n")
        for i in range(10):
            w.writerow([f"H{i}", "A001", "R01", f"H{i}", 1000, "Closed Won" if i < 7 else "Closed Lost",
                        "2026-04-01", "2026-05-22", "closed_won" if i < 7 else "closed_lost", "true", str(i < 7).lower()])
    res = run_pipeline(data, "2026-W34")
    neg = res.one("SELECT * FROM stage_probability WHERE stage = 'Negotiation'")
    assert neg["hist_n"] == 10
    assert neg["probability_used"] == D("0.7000")
    assert neg["source"] == "historical win rate (n=10)"
    t1 = res.one("SELECT weighted_value FROM deal_values WHERE which = 'curr' AND deal_id = 'T1'")
    assert t1["weighted_value"] == D("7000.00")
