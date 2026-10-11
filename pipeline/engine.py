"""Runs the SQL pipeline. Python only loads files, executes the .sql steps in
order and hands the results to the report writer. All business rules live in sql/."""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from datetime import date, datetime, timedelta
from pathlib import Path

import duckdb

ROOT = Path(__file__).resolve().parent.parent
SQL_DIR = ROOT / "sql"
SEEDS_DIR = ROOT / "data" / "seeds"

# (table, file, column types). Types are explicit so a messy file can't
# silently change a column's type.
TABLES = {
    "reps": ("reps.csv", {"rep_id": "VARCHAR", "name": "VARCHAR", "team": "VARCHAR", "quota_q": "DECIMAL(18,2)"}),
    "accounts": ("accounts.csv", {"account_id": "VARCHAR", "name": "VARCHAR", "industry": "VARCHAR",
                                  "size_band": "VARCHAR", "region": "VARCHAR"}),
    "stages": ("stages.csv", {"stage": "VARCHAR", "order_index": "INTEGER", "default_probability": "DECIMAL(6,4)"}),
    "deals": ("deals.csv", {"deal_id": "VARCHAR", "account_id": "VARCHAR", "rep_id": "VARCHAR", "name": "VARCHAR",
                            "amount_eur": "DECIMAL(18,2)", "stage": "VARCHAR", "created_at": "DATE",
                            "close_date": "DATE", "forecast_category": "VARCHAR", "is_closed": "BOOLEAN",
                            "is_won": "BOOLEAN"}),
    "deal_history": ("deal_history.csv", {"deal_id": "VARCHAR", "snapshot_week": "DATE", "stage": "VARCHAR",
                                          "amount_eur": "DECIMAL(18,2)", "close_date": "DATE",
                                          "forecast_category": "VARCHAR"}),
    "activities": ("activities.csv", {"activity_id": "VARCHAR", "deal_id": "VARCHAR", "type": "VARCHAR",
                                      "occurred_at": "DATE"}),
}
STEPS_AFTER_CHECKS = ["clean", "forecast", "risk", "bridge", "report"]


class BlockerError(RuntimeError):
    """Raised when a BLOCKER data-quality check fails. The run stops; no forecast is produced."""


@dataclass
class Check:
    check_id: str
    severity: str
    description: str
    failing_rows: list[tuple] = field(default_factory=list)

    @property
    def passed(self) -> bool:
        return not self.failing_rows


def sql_files(step: str) -> list[Path]:
    return sorted((SQL_DIR / step).glob("*.sql"))


def parse_week(value: str) -> date:
    """Accepts '2026-W34' or a date like '2026-08-17'; returns that ISO week's Monday."""
    value = value.strip()
    m = re.fullmatch(r"(\d{4})-W(\d{1,2})", value)
    if m:
        return date.fromisocalendar(int(m.group(1)), int(m.group(2)), 1)
    d = date.fromisoformat(value)
    return d - timedelta(days=d.weekday())


def load(con: duckdb.DuckDBPyConnection, data_dir: Path) -> None:
    for table, (fname, cols) in TABLES.items():
        path = data_dir / fname
        if not path.exists():
            raise FileNotFoundError(f"Missing input file: {path}")
        con.execute(f"CREATE OR REPLACE TABLE {table} AS SELECT * FROM read_csv(?, header=true, columns=?)",
                    [str(path), cols])
    con.execute("CREATE OR REPLACE TABLE stage_aliases AS SELECT * FROM read_csv(?, header=true, columns=?)",
                [str(SEEDS_DIR / "stage_aliases.csv"), {"raw_stage": "VARCHAR", "stage": "VARCHAR", "note": "VARCHAR"}])


def run_step(con: duckdb.DuckDBPyConnection, step: str) -> None:
    for f in sql_files(step):
        try:
            con.execute(f.read_text(encoding="utf-8"))
        except duckdb.Error as e:  # make the failing file obvious
            raise RuntimeError(f"SQL error in {f.relative_to(ROOT)}: {e}") from e


def run_checks(con: duckdb.DuckDBPyConnection) -> list[Check]:
    checks = []
    for f in sql_files("checks"):
        text = f.read_text(encoding="utf-8")
        meta = dict(re.findall(r"^--\s*(check|severity|description):\s*(.+)$", text, flags=re.M))
        rows = con.execute(text).fetchall()
        rows = sorted(rows, key=lambda r: tuple("" if v is None else str(v) for v in r))
        checks.append(Check(meta["check"].strip(), meta["severity"].strip(), meta["description"].strip(), rows))
    return checks


@dataclass
class RunResult:
    run_week: date
    week_label: str
    checks: list[Check]
    con: duckdb.DuckDBPyConnection
    blocked: bool = False

    def table(self, sql: str) -> list[dict]:
        cur = self.con.execute(sql)
        cols = [c[0] for c in cur.description]
        return [dict(zip(cols, r)) for r in cur.fetchall()]

    def one(self, sql: str) -> dict:
        rows = self.table(sql)
        return rows[0] if rows else {}


def run_pipeline(data_dir: Path, week: str | date | None = None) -> RunResult:
    """Run checks -> clean -> forecast -> risk -> bridge -> report (SQL). Raises BlockerError on a BLOCKER."""
    con = duckdb.connect()
    load(con, data_dir)
    if week is None:
        run_week = con.execute("SELECT max(snapshot_week) FROM deal_history").fetchone()[0]
    else:
        run_week = week if isinstance(week, date) else parse_week(week)
    con.execute("CREATE OR REPLACE TABLE run_request AS SELECT CAST(? AS DATE) AS run_week", [run_week])
    run_step(con, "staging")
    checks = run_checks(con)
    label = con.execute("SELECT week_label FROM params").fetchone()[0]
    result = RunResult(run_week, label, checks, con)
    if any(c.severity == "BLOCKER" and not c.passed for c in checks):
        result.blocked = True
        return result
    for step in STEPS_AFTER_CHECKS:
        run_step(con, step)
    return result


def now_utc() -> str:
    return datetime.utcnow().replace(microsecond=0).isoformat() + "Z"
