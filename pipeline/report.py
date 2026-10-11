"""Turns the SQL results into files: the weekly report, the data-quality report,
two PNG charts and a row in the run log. Presentation only - every number and
sentence here was computed in sql/."""
from __future__ import annotations

import csv
import subprocess
import textwrap
from decimal import Decimal
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

from .engine import ROOT, RunResult, now_utc  # noqa: E402

# Colours (reference palette from the dataviz guidelines): blue/red diverging
# poles for up/down, neutral ink for totals, recessive grey grid.
SURFACE = "#fcfcfb"
INK = "#0b0b0b"
INK_2 = "#52514e"
GRID = "#e4e3df"
UP = "#2a78d6"
UP_LIGHT = "#9cc3ef"
DOWN = "#e34948"
TOTAL = "#52514e"

RUN_LOG_FIELDS = ["run_timestamp_utc", "data_week", "status", "checks_passed", "checks_failed",
                  "blockers", "forecast_eur", "change_vs_last_run_eur", "git_commit"]


def eur(x) -> str:
    x = Decimal(x or 0)
    s = f"€{abs(x):,.0f}"
    return f"−{s}" if x < 0 else s


def eur_signed(x) -> str:
    x = Decimal(x or 0)
    return ("+" if x >= 0 else "−") + f"€{abs(x):,.0f}"


def gap_text(x) -> str:
    if x is None:
        return "–"
    return eur(x) if x >= 0 else f"€0 (over by {eur(-x)})"


def pct(x) -> str:
    return "–" if x is None else f"{x:.1f}%"


def md_table(headers: list[str], rows: list[list], align: str | None = None) -> str:
    align = align or "l" * len(headers)
    sep = ["---:" if a == "r" else ":---" for a in align]
    lines = ["| " + " | ".join(headers) + " |", "| " + " | ".join(sep) + " |"]
    lines += ["| " + " | ".join(str(c).replace("|", "\\|") for c in r) + " |" for r in rows]
    return "\n".join(lines)


def _style(ax):
    ax.set_facecolor(SURFACE)
    for s in ("top", "right", "left"):
        ax.spines[s].set_visible(False)
    ax.spines["bottom"].set_color(GRID)
    ax.tick_params(colors=INK_2, length=0)
    ax.grid(axis="y", color=GRID, linewidth=0.8)
    ax.set_axisbelow(True)


def _k(v: float) -> str:
    return f"€{v / 1000:,.0f}k"


def chart_bridge(res: RunResult, path: Path) -> None:
    t = res.one("SELECT * FROM bridge_totals")
    rows = [r for r in res.table("SELECT short_label, amount FROM bridge_summary ORDER BY bucket_order") if r["amount"] != 0]
    labels = ["Last week"] + [r["short_label"][0].upper() + r["short_label"][1:] for r in rows] + ["This week"]
    fig, ax = plt.subplots(figsize=(10, 4.6), dpi=150)
    fig.patch.set_facecolor(SURFACE)
    _style(ax)
    running = float(t["prev_forecast"])
    ax.bar(0, running, color=TOTAL, width=0.62)
    ax.text(0, running, _k(running), ha="center", va="bottom", fontsize=9, color=INK)
    for i, r in enumerate(rows, start=1):
        amt = float(r["amount"])
        bottom = running if amt >= 0 else running + amt
        ax.bar(i, abs(amt), bottom=bottom, color=UP if amt >= 0 else DOWN, width=0.62)
        ax.plot([i - 1 + 0.31, i - 0.31], [running, running], color=INK_2, linewidth=0.8)
        ax.text(i, bottom + abs(amt), ("+" if amt >= 0 else "−") + _k(abs(amt)),
                ha="center", va="bottom", fontsize=9, color=INK)
        running += amt
    n = len(rows) + 1
    ax.plot([n - 1 + 0.31, n - 0.31], [running, running], color=INK_2, linewidth=0.8)
    ax.bar(n, float(t["curr_forecast"]), color=TOTAL, width=0.62)
    ax.text(n, float(t["curr_forecast"]), _k(float(t["curr_forecast"])), ha="center", va="bottom", fontsize=9, color=INK)
    lo = min(float(t["prev_forecast"]), float(t["curr_forecast"]), running) * 0.85
    ax.set_ylim(bottom=lo)
    ax.set_xticks(range(n + 1))
    ax.set_xticklabels([textwrap.fill(l, 11) for l in labels], fontsize=8.5, color=INK_2)
    ax.yaxis.set_major_formatter(matplotlib.ticker.FuncFormatter(lambda v, _: _k(v)))
    ax.set_title(f"Forecast bridge {res.week_label}: why the number moved ({eur_signed(t['total_change'])})",
                 loc="left", fontsize=12, color=INK, pad=12)
    ax.text(0, -0.30, "Blue = added to the forecast, red = removed. Grey = weighted forecast total. "
            "Note the y-axis does not start at zero.", transform=ax.transAxes, fontsize=8, color=INK_2)
    fig.tight_layout()
    fig.savefig(path, facecolor=SURFACE, metadata={"Software": None})
    plt.close(fig)


def chart_quota(res: RunResult, path: Path) -> None:
    reps = res.table("SELECT * FROM rep_forecast WHERE quota_q > 0 ORDER BY team, rep_id")
    names = [f"{r['rep_name']}\n({r['team']})" for r in reps]
    fig, ax = plt.subplots(figsize=(10, 4.2), dpi=150)
    fig.patch.set_facecolor(SURFACE)
    _style(ax)
    ax.grid(axis="y", visible=False)
    ax.grid(axis="x", color=GRID, linewidth=0.8)
    y = list(range(len(reps)))[::-1]
    won = [float(r["closed_won"]) for r in reps]
    wopen = [float(r["weighted_open"]) for r in reps]
    quota = [float(r["quota_q"]) for r in reps]
    ax.barh(y, won, color=UP, height=0.5, label="Closed won")
    ax.barh(y, wopen, left=won, color=UP_LIGHT, height=0.5, label="Weighted open pipeline", edgecolor=SURFACE, linewidth=2)
    for yi, q, w, o, r in zip(y, quota, won, wopen, reps):
        ax.plot([q, q], [yi - 0.36, yi + 0.36], color=INK, linewidth=2)
        ax.text(max(q, w + o) + 6000, yi, f"{pct(r['forecast_pct_of_quota'])} of quota", va="center", fontsize=9, color=INK)
    ax.plot([], [], color=INK, linewidth=2, label="Quota")
    ax.set_yticks(y)
    ax.set_yticklabels(names, fontsize=9, color=INK_2)
    ax.xaxis.set_major_formatter(matplotlib.ticker.FuncFormatter(lambda v, _: _k(v)))
    ax.set_xlim(0, max(max(quota), max(a + b for a, b in zip(won, wopen))) * 1.25)
    ax.set_title(f"Forecast vs quota by rep, {res.week_label}", loc="left", fontsize=12, color=INK, pad=12)
    ax.legend(loc="lower right", frameon=False, fontsize=8.5, labelcolor=INK_2)
    fig.tight_layout()
    fig.savefig(path, facecolor=SURFACE, metadata={"Software": None})
    plt.close(fig)


def write_data_quality(res: RunResult, out_dir: Path) -> Path:
    p = res.one("SELECT * FROM params")
    lines = [f"# Data quality report, {res.week_label}", "",
             f"Snapshot of {p['run_week']:%d %b %Y}, compared with {p['prev_week']:%d %b %Y}. "
             "BLOCKER = the run stops, no forecast is produced. WARN = reported, fixed or flagged, run continues.", ""]
    blockers = [c for c in res.checks if c.severity == "BLOCKER" and not c.passed]
    if blockers:
        lines += ["**RUN STOPPED: a BLOCKER check failed. No forecast was produced for this week.**", ""]
    rows = []
    for c in res.checks:
        status = "PASS" if c.passed else ("FAIL (BLOCKER)" if c.severity == "BLOCKER" else "WARN")
        rows.append([c.check_id, c.severity, status, len(c.failing_rows), c.description])
    lines += ["## Checks", "", md_table(["Check", "Severity", "Result", "Rows", "What it checks"], rows, "lllrl"), ""]
    failing = [c for c in res.checks if not c.passed]
    if failing:
        lines += ["## Failing rows", ""]
        for c in failing:
            lines += [f"### {c.check_id} ({c.severity})", ""]
            lines += [f"- {r[2] or '(whole dataset)'}: {r[3]}" for r in c.failing_rows]
            lines += [""]
    if not res.blocked:
        log = res.table("SELECT * FROM clean_log ORDER BY step, deal_id, scope")
        lines += ["## Fixes applied (clean/ step)", "",
                  "Every automatic fix is logged here. Nothing is changed silently.", ""]
        lines += [md_table(["Fix", "Deal", "Where", "What was done"],
                           [[r["step"], r["deal_id"], r["scope"], r["action"]] for r in log]) if log else "_No fixes needed._", ""]
    path = out_dir / f"data_quality_{res.week_label}.md"
    path.write_text("\n".join(lines), encoding="utf-8")
    return path


def write_report(res: RunResult, out_dir: Path) -> Path:
    charts = out_dir / "charts"
    charts.mkdir(parents=True, exist_ok=True)
    bridge_png = charts / f"bridge_{res.week_label}.png"
    quota_png = charts / f"forecast_vs_quota_{res.week_label}.png"
    chart_bridge(res, bridge_png)
    chart_quota(res, quota_png)

    p = res.one("SELECT * FROM params")
    h = res.one("SELECT * FROM headline")
    tot = res.one("SELECT * FROM team_forecast WHERE team = 'Total'")
    t = res.one("SELECT * FROM bridge_totals")
    q = f"Q{(p['q_start'].month - 1) // 3 + 1} {p['q_start'].year}"
    out = [
        f"# Weekly forecast: Fernbrook Analytics, {res.week_label}", "",
        f"_{q} ({p['q_start']:%d %b} – {p['q_end']:%d %b %Y}) · snapshot of {p['run_week']:%d %b %Y} · "
        f"compared with {p['prev_week_label']} · all data is synthetic and fictional_", "",
        f"> **{h['headline']}**", "",
        "## The numbers", "",
        md_table(["", "This week", "Last week", "Change"], [
            ["Forecast (closed won + weighted open)", eur(t["curr_forecast"]), eur(t["prev_forecast"]), eur_signed(t["total_change"])],
        ], "lrrr"), "",
        md_table(["Measure", "Amount", "What it means"], [
            ["Quota", eur(tot["quota_q"]), "Sum of rep quotas for the quarter"],
            ["Closed won", eur(tot["closed_won"]), f"Attainment to date: {pct(tot['attainment_pct'])}"],
            ["Gap to quota", gap_text(tot["gap_to_quota"]), "Still needed from open deals"],
            ["Commit", eur(tot["commit_total"]), "Closed won + open deals reps marked commit"],
            ["Best case", eur(tot["best_case_total"]), "Commit + open deals marked best case"],
            ["Open pipeline (unweighted)", eur(tot["commit_open"] + tot["best_case_open"] + tot["pipeline_open"]),
             f"{tot['open_deals']} open deals due to close this quarter"],
            ["Forecast (weighted)", eur(tot["forecast"]), f"{pct(tot['forecast_pct_of_quota'])} of quota"],
        ], "lrl"), "",
        "## Why it moved: the bridge", "",
        f"![Forecast bridge](charts/{bridge_png.name})", "",
    ]
    rows = [[eur(t["prev_forecast"]), "Last week's forecast", ""]]
    for r in res.table("SELECT * FROM bridge_summary ORDER BY bucket_order"):
        if r["amount"] != 0:
            rows.append([eur_signed(r["amount"]), r["label"], f"{r['deals']} ({r['biggest_deal']})" if r["deals"] == 1
                         else f"{r['deals']} (biggest: {r['biggest_deal']})"])
    rows.append([eur(t["curr_forecast"]), "**This week's forecast**", ""])
    out += [md_table(["Amount", "Bucket", "Deals"], rows, "rll"), "",
            f"Buckets add up to the total change exactly: {eur_signed(t['bucket_sum'])} = "
            f"{eur(t['curr_forecast'])} − {eur(t['prev_forecast'])} (unexplained: €{t['unexplained']:.2f}).", ""]

    risk = res.table("SELECT * FROM deal_risk WHERE in_quarter ORDER BY risk_rank LIMIT 5")
    n_flagged = res.one("SELECT count(*) AS n FROM deal_risk")["n"]
    out += ["## Top 5 deals at risk", "",
            f"{n_flagged} open deals have at least one warning sign. These five count toward this quarter "
            "and have the most signs, then the most money at stake.", "",
            md_table(["#", "Deal", "Owner", "Stage", "Amount", "Close", "Why it is at risk"],
                     [[r["risk_rank"], r["deal_name"], r["rep_name"], r["stage"], eur(r["amount_eur"]),
                       f"{r['close_date']:%d %b}", r["reasons"]] for r in risk], "rlllrll"), ""]

    reps = res.table("SELECT * FROM rep_forecast")
    out += ["## Forecast vs quota by rep", "", f"![Forecast vs quota](charts/{quota_png.name})", "",
            md_table(["Rep", "Team", "Quota", "Closed won", "Attainment", "Commit", "Best case", "Forecast", "Gap to quota"],
                     [[r["rep_name"], r["team"], eur(r["quota_q"]) if r["quota_q"] else "–", eur(r["closed_won"]),
                       pct(r["attainment_pct"]), eur(r["commit_total"]), eur(r["best_case_total"]), eur(r["forecast"]),
                       gap_text(r["gap_to_quota"])] for r in reps],
                     "llrrrrrrr"), ""]

    failing = [c for c in res.checks if not c.passed]
    out += ["## Data issues found this run", "",
            f"{len(res.checks) - len(failing)} of {len(res.checks)} checks passed; "
            f"{len(failing)} raised warnings, none blocked the run. Full detail: "
            f"[data_quality_{res.week_label}.md](data_quality_{res.week_label}.md)", ""]
    out += [f"- **{c.check_id}**: {len(c.failing_rows)} row(s). {c.description}" for c in failing] + [""]

    probs = res.table("SELECT * FROM stage_probability WHERE order_index <= 5 ORDER BY order_index")
    out += ["## How deals were weighted", "",
            md_table(["Stage", "Probability used", "Source", "Default"],
                     [[r["stage"], f"{float(r['probability_used']):.0%}", r["source"], f"{float(r['default_probability']):.0%}"]
                      for r in probs], "lrll"), "",
            "Historical win rate = share of deals that reached the stage and were won, among deals closed before "
            "this quarter. Used when at least 10 such deals exist, otherwise the default. "
            "See [docs/methodology.md](../docs/methodology.md).", ""]
    path = out_dir / f"weekly_report_{res.week_label}.md"
    path.write_text("\n".join(out), encoding="utf-8")
    return path


def git_commit() -> str:
    try:
        return subprocess.run(["git", "rev-parse", "--short", "HEAD"], cwd=ROOT, capture_output=True,
                              text=True, check=True).stdout.strip()
    except Exception:
        return "not-a-git-checkout"


def append_run_log(res: RunResult, out_dir: Path) -> dict:
    path = out_dir / "run_log.csv"
    previous = None
    if path.exists():
        with path.open(newline="", encoding="utf-8") as f:
            done = [r for r in csv.DictReader(f) if r["forecast_eur"]]
            previous = done[-1] if done else None
    failed = [c for c in res.checks if not c.passed]
    forecast = None if res.blocked else res.one("SELECT curr_forecast FROM bridge_totals")["curr_forecast"]
    row = {
        "run_timestamp_utc": now_utc(),
        "data_week": res.week_label,
        "status": "blocked" if res.blocked else "ok",
        "checks_passed": len(res.checks) - len(failed),
        "checks_failed": len(failed),
        "blockers": sum(1 for c in failed if c.severity == "BLOCKER"),
        "forecast_eur": "" if forecast is None else f"{forecast:.2f}",
        "change_vs_last_run_eur": "" if forecast is None or previous is None
        else f"{forecast - Decimal(previous['forecast_eur']):.2f}",
        "git_commit": git_commit(),
    }
    new = not path.exists()
    with path.open("a", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=RUN_LOG_FIELDS, lineterminator="\n")
        if new:
            w.writeheader()
        w.writerow(row)
    return row
