"""Generate the synthetic CRM dataset for Fernbrook Analytics (a fictional company).

Everything here is invented: the company, the reps, the accounts and the deals.
Same seed -> byte-identical CSV files.

Usage:
    python generate_data.py                  # seed 42, writes data/sample/
    python generate_data.py --seed 7 --out /tmp/data

The simulation walks every deal week by week (Monday snapshots), moving it
through the stages, changing amounts and pushing close dates the way real
pipelines drift. After the simulation a small, documented set of data problems
is injected into the last two weeks so the quality checks have something real
to catch. Which deal got which problem is written to injected_issues.json, and
the tests use that file to prove every problem is caught by the right check.
"""
from __future__ import annotations

import argparse
import csv
import json
import random
from datetime import date, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parent

FIRST_WEEK = date(2026, 1, 5)   # Monday, start of history (Q1 2026)
LAST_WEEK = date(2026, 8, 17)   # Monday, the sample "this week" (mid Q3 2026)

STAGES = [
    # stage, order_index, default_probability
    ("Qualification", 1, 0.10),
    ("Discovery", 2, 0.20),
    ("Solution Design", 3, 0.40),
    ("Proposal", 4, 0.60),
    ("Negotiation", 5, 0.80),
    ("Closed Won", 6, 1.00),
    ("Closed Lost", 7, 0.00),
]
OPEN_STAGES = [s for s, i, _ in STAGES if i <= 5]
CATEGORY_BY_STAGE = {
    "Qualification": "pipeline",
    "Discovery": "pipeline",
    "Solution Design": "best_case",
    "Proposal": "best_case",
    "Negotiation": "commit",
}
CATEGORY_LADDER = ["pipeline", "best_case", "commit"]

REPS = [
    # rep_id, name, team, quota_q (EUR per quarter)
    ("R01", "Lena Hartwig", "Mid-Market", 260_000),
    ("R02", "Jonas Brenner", "Mid-Market", 250_000),
    ("R03", "Mira Okonkwo", "Enterprise", 420_000),
    ("R04", "Tobias Lindvall", "Enterprise", 400_000),
]

ACCOUNT_PREFIXES = [
    "Alsterbogen", "Brückenhof", "Deichgraf", "Elbwiese", "Fleetkante", "Grünspan",
    "Hafenkran", "Ilmenau", "Kranichfeld", "Lotsenhaus", "Moorblick", "Nordkliff",
    "Ostkai", "Pfefferland", "Quellwerk", "Rotklinker", "Sandtorhafen", "Tidenhub",
    "Uferlicht", "Wellenbrecher", "Zollkontor", "Backsteinhof", "Dünenweg", "Möwenkai",
]
INDUSTRIES = ["Logistics", "Retail", "Manufacturing", "Healthcare", "Energy", "Insurance", "Media", "Hospitality"]
INDUSTRY_WORD = {
    "Logistics": "Logistik", "Retail": "Handel", "Manufacturing": "Maschinenbau",
    "Healthcare": "Medizintechnik", "Energy": "Energie", "Insurance": "Versicherung",
    "Media": "Medien", "Hospitality": "Gastgewerbe",
}
REGIONS = ["North", "West", "South", "East", "DACH-Remote"]
SIZE_BANDS = [("SMB", 6_000, 22_000), ("Mid", 18_000, 60_000), ("Large", 45_000, 140_000)]
PRODUCTS = [
    "Revenue Dashboard rollout", "Analytics platform licence", "Forecasting module",
    "Seat expansion", "Data quality audit", "Onboarding package", "Reporting automation",
    "Pipeline analytics pilot", "BI migration", "Annual renewal uplift",
]
ACTIVITY_TYPES = ["email", "call", "meeting", "demo"]


def mondays(start: date, end: date) -> list[date]:
    out, d = [], start
    while d <= end:
        out.append(d)
        d += timedelta(days=7)
    return out


def round_to(x: float, step: int = 500) -> int:
    return int(round(x / step) * step)


def build_accounts(rng: random.Random) -> list[dict]:
    accounts = []
    prefixes = ACCOUNT_PREFIXES[:]
    rng.shuffle(prefixes)
    for i, prefix in enumerate(prefixes):
        industry = INDUSTRIES[i % len(INDUSTRIES)]
        band = rng.choices(SIZE_BANDS, weights=[4, 4, 2])[0][0]
        legal = "AG" if band == "Large" and rng.random() < 0.5 else "GmbH"
        accounts.append({
            "account_id": f"A{i + 1:03d}",
            "name": f"{prefix} {INDUSTRY_WORD[industry]} {legal}",
            "industry": industry,
            "size_band": band,
            "region": rng.choice(REGIONS),
        })
    return accounts


def simulate(seed: int) -> dict:
    rng = random.Random(seed)
    weeks = mondays(FIRST_WEEK, LAST_WEEK)
    accounts = build_accounts(rng)
    band_range = {b: (lo, hi) for b, lo, hi in SIZE_BANDS}
    stage_idx = {s: i for s, i, _ in STAGES}

    deals: list[dict] = []           # static attributes
    states: dict[str, dict] = {}     # mutable current state per deal
    history: list[dict] = []         # weekly snapshots
    activities: list[dict] = []
    deal_counter = 0

    for wi, week in enumerate(weeks):
        # 1) move existing open deals (state as seen at this Monday)
        for deal in deals:
            st = states[deal["deal_id"]]
            if st["stage"] in ("Closed Won", "Closed Lost") or st["created_week"] == week:
                continue
            idx = stage_idx[st["stage"]]
            r = rng.random()
            new_stage = st["stage"]
            if idx == 5:
                if r < 0.30:
                    new_stage = "Closed Won"
                elif r < 0.37:
                    new_stage = "Closed Lost"
                elif r < 0.40:
                    new_stage = "Proposal"
            else:
                lose_p = 0.07 if idx <= 2 else 0.05
                if r < 0.21:
                    new_stage = OPEN_STAGES[idx]          # advance one stage
                elif r < 0.21 + lose_p:
                    new_stage = "Closed Lost"
                elif idx > 1 and r < 0.21 + lose_p + 0.025:
                    new_stage = OPEN_STAGES[idx - 2]      # move backwards
            if new_stage != st["stage"]:
                st["stage"] = new_stage
                if new_stage in CATEGORY_BY_STAGE:
                    base = CATEGORY_LADDER.index(CATEGORY_BY_STAGE[new_stage])
                    shift = rng.choices([-1, 0, 1], weights=[1, 8, 1])[0]
                    st["forecast_category"] = CATEGORY_LADDER[max(0, min(2, base + shift))]
            if st["stage"] in ("Closed Won", "Closed Lost"):
                st["forecast_category"] = "closed_won" if st["stage"] == "Closed Won" else "closed_lost"
                st["close_date"] = week - timedelta(days=rng.randint(1, 5))
            else:
                # amount drift
                if rng.random() < 0.08:
                    st["amount"] = max(2_000, round_to(st["amount"] * rng.choice([0.7, 0.85, 1.1, 1.25])))
                # close date drift
                if st["close_date"] < week and rng.random() < 0.85:
                    st["close_date"] = week + timedelta(days=rng.randint(10, 45))
                elif rng.random() < 0.04:
                    st["close_date"] = st["close_date"] + timedelta(days=rng.randint(14, 42))
                elif st["close_date"] > week + timedelta(days=28) and rng.random() < 0.04:
                    st["close_date"] = st["close_date"] - timedelta(days=rng.randint(10, 25))

        # 2) new deals created during the week before this Monday
        for rep_id, _, team, _ in REPS:
            n_new = rng.choices([0, 1, 2], weights=[2, 5, 3] if team == "Mid-Market" else [3, 5, 2])[0]
            for _ in range(n_new):
                deal_counter += 1
                deal_id = f"D{deal_counter:04d}"
                acct = rng.choice(accounts)
                lo, hi = band_range[acct["size_band"]]
                if team == "Enterprise":
                    lo, hi = int(lo * 1.4), int(hi * 1.4)
                created = week - timedelta(days=rng.randint(1, 6))
                stage = rng.choices(["Qualification", "Discovery"], weights=[3, 1])[0]
                deals.append({
                    "deal_id": deal_id,
                    "account_id": acct["account_id"],
                    "rep_id": rep_id,
                    "name": f"{acct['name'].split(' ')[0]} – {rng.choice(PRODUCTS)}",
                    "created_at": created,
                })
                states[deal_id] = {
                    "stage": stage,
                    "amount": round_to(rng.uniform(lo, hi)),
                    "close_date": created + timedelta(days=rng.randint(35, 120)),
                    "forecast_category": "pipeline",
                    "created_week": week,
                    "goes_dark_after": (week + timedelta(days=7 * rng.randint(2, 8))) if rng.random() < 0.18 else None,
                }

        # 3) activities logged during the week leading up to this Monday
        for deal in deals:
            st = states[deal["deal_id"]]
            if st["stage"] in ("Closed Won", "Closed Lost"):
                continue
            if st["goes_dark_after"] is not None and week > st["goes_dark_after"]:
                continue
            if rng.random() < 0.6:
                for _ in range(rng.choice([1, 1, 2])):
                    activities.append({
                        "deal_id": deal["deal_id"],
                        "type": rng.choice(ACTIVITY_TYPES),
                        "occurred_at": max(deal["created_at"], week - timedelta(days=rng.randint(1, 7))),
                    })

        # 4) snapshot
        for deal in deals:
            st = states[deal["deal_id"]]
            history.append({
                "deal_id": deal["deal_id"],
                "snapshot_week": week,
                "stage": st["stage"],
                "amount_eur": st["amount"],
                "close_date": st["close_date"],
                "forecast_category": st["forecast_category"],
            })

    return {"weeks": weeks, "accounts": accounts, "deals": deals, "states": states,
            "history": history, "activities": activities, "rng": rng}


def inject_issues(sim: dict) -> tuple[list[dict], list[dict], dict]:
    """Inject realistic data problems into the last two weeks. Returns (deal_rows, history, manifest)."""
    rng: random.Random = sim["rng"]
    history = sim["history"]
    last, prev = sim["weeks"][-1], sim["weeks"][-2]
    q_start, q_end = date(2026, 7, 1), date(2026, 9, 30)

    def rows(deal_id: str, week: date) -> list[dict]:
        return [h for h in history if h["deal_id"] == deal_id and h["snapshot_week"] == week]

    def open_in_quarter_both_weeks() -> list[str]:
        ok = []
        for d in sim["deals"]:
            r_last, r_prev = rows(d["deal_id"], last), rows(d["deal_id"], prev)
            if r_last and r_prev and all(
                r["stage"] in OPEN_STAGES and q_start <= r["close_date"] <= q_end for r in r_last + r_prev
            ):
                ok.append(d["deal_id"])
        return ok

    candidates = open_in_quarter_both_weeks()
    picks = rng.sample(candidates, 5)
    manifest: dict[str, list[str]] = {}

    # 1) negative amount (typo: minus sign) this week only
    d = picks[0]
    for r in rows(d, last):
        r["amount_eur"] = -abs(r["amount_eur"])
    manifest["dq_negative_amount"] = [d]

    # 2) missing amount, both weeks
    d = picks[1]
    for r in rows(d, last) + rows(d, prev):
        r["amount_eur"] = None
    manifest["dq_missing_amount"] = [d]

    # 3) unknown stage names that have a known meaning (typo / old picklist value)
    legacy_names = {"Qualification": "Qualified", "Discovery": "Disco", "Solution Design": "Solution design",
                    "Proposal": "Proposal Sent", "Negotiation": "Negotation"}
    d = picks[2]
    for r in rows(d, last):
        r["stage"] = legacy_names[r["stage"]]
    d2 = picks[3]
    for r in rows(d2, last) + rows(d2, prev):
        r["stage"] = legacy_names[r["stage"]]
    manifest["dq_unknown_stage_mapped"] = [d, d2]

    # 4) orphan rep_id: rep left, id no longer in the reps table
    orphan_deal = picks[4]
    manifest["dq_orphan_rep"] = [orphan_deal]

    # 5) duplicate: same deal exported twice this week
    dup_deal = rng.choice([x for x in candidates if x not in picks])
    for r in rows(dup_deal, last):
        history.append(dict(r))
    manifest["dq_duplicate_deal"] = [dup_deal]

    # 6) open deal whose close date is already in the past (rep never updated it)
    stale_close = rng.choice([x for x in candidates if x not in picks and x != dup_deal])
    for r in rows(stale_close, last):
        r["close_date"] = last - timedelta(days=9)
    manifest["dq_close_date_in_past"] = [stale_close]

    # Scenario for the sample week (not a data problem): the kind of week a
    # forecast call is about. The largest late-stage deal slips into next
    # quarter, and one next-quarter deal is pulled in. Everything else in the
    # week comes from the simulation.
    used = set(picks) | {dup_deal, stale_close}
    late_stage = [x for x in candidates if x not in used
                  and all(r["stage"] in ("Proposal", "Negotiation") for r in rows(x, last) + rows(x, prev))]
    slip = max(late_stage, key=lambda x: (rows(x, last)[0]["amount_eur"], x))
    for r in rows(slip, last):
        r["close_date"] = date(2026, 10, 16)
    next_q = [d["deal_id"] for d in sim["deals"]
              if rows(d["deal_id"], last) and rows(d["deal_id"], prev)
              and all(r["stage"] in OPEN_STAGES and r["close_date"] > q_end
                      for r in rows(d["deal_id"], last) + rows(d["deal_id"], prev))]
    pull = sorted(next_q)[0]
    for r in rows(pull, last):
        r["close_date"] = date(2026, 9, 25)
    manifest["scenario_slipped_to_next_quarter"] = [slip]
    manifest["scenario_pulled_into_quarter"] = [pull]

    deal_rows = []
    latest = {}
    for h in history:
        if h["snapshot_week"] == last:
            latest.setdefault(h["deal_id"], h)
    for d in sim["deals"]:
        h = latest[d["deal_id"]]
        stage = h["stage"]
        deal_rows.append({
            "deal_id": d["deal_id"],
            "account_id": d["account_id"],
            "rep_id": "R09" if d["deal_id"] == orphan_deal else d["rep_id"],
            "name": d["name"],
            "amount_eur": h["amount_eur"],
            "stage": stage,
            "created_at": d["created_at"],
            "close_date": h["close_date"],
            "forecast_category": h["forecast_category"],
            "is_closed": stage in ("Closed Won", "Closed Lost"),
            "is_won": stage == "Closed Won",
        })
        if d["deal_id"] == dup_deal:
            deal_rows.append(dict(deal_rows[-1]))
    return deal_rows, history, manifest


def write_csv(path: Path, rows: list[dict], fields: list[str]) -> None:
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields, lineterminator="\n")
        w.writeheader()
        for r in rows:
            w.writerow({k: ("" if r.get(k) is None else r.get(k)) for k in fields})


def generate(out_dir: Path, seed: int = 42) -> dict:
    out_dir.mkdir(parents=True, exist_ok=True)
    sim = simulate(seed)
    deal_rows, history, manifest = inject_issues(sim)

    # facts derived from the simulation itself, for the tests
    manifest["dq_stale_no_activity_21d"] = "derived: deals whose activity stopped (goes_dark_after)"
    manifest["dq_close_date_pushed_2x"] = "derived: close dates pushed by the weekly simulation"

    acts = sorted(sim["activities"], key=lambda a: (a["occurred_at"], a["deal_id"], a["type"]))
    for i, a in enumerate(acts, start=1):
        a["activity_id"] = f"ACT{i:05d}"

    history = sorted(history, key=lambda h: (h["snapshot_week"], h["deal_id"]))
    write_csv(out_dir / "reps.csv", [dict(zip(["rep_id", "name", "team", "quota_q"], r)) for r in REPS],
              ["rep_id", "name", "team", "quota_q"])
    write_csv(out_dir / "accounts.csv", sim["accounts"], ["account_id", "name", "industry", "size_band", "region"])
    write_csv(out_dir / "stages.csv", [dict(zip(["stage", "order_index", "default_probability"], s)) for s in STAGES],
              ["stage", "order_index", "default_probability"])
    write_csv(out_dir / "deals.csv", deal_rows,
              ["deal_id", "account_id", "rep_id", "name", "amount_eur", "stage", "created_at", "close_date",
               "forecast_category", "is_closed", "is_won"])
    write_csv(out_dir / "deal_history.csv", history,
              ["deal_id", "snapshot_week", "stage", "amount_eur", "close_date", "forecast_category"])
    write_csv(out_dir / "activities.csv", acts, ["activity_id", "deal_id", "type", "occurred_at"])
    (out_dir / "injected_issues.json").write_text(
        json.dumps({"seed": seed, "run_week": LAST_WEEK.isoformat(), "issues": manifest}, indent=2) + "\n",
        encoding="utf-8")
    return manifest


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--seed", type=int, default=42)
    p.add_argument("--out", type=Path, default=ROOT / "data" / "sample")
    a = p.parse_args()
    generate(a.out, a.seed)
    print(f"Synthetic data written to {a.out} (seed={a.seed})")


if __name__ == "__main__":
    main()
