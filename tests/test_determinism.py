"""Same seed -> same data -> same report, byte for byte."""
from pathlib import Path

from conftest import SAMPLE
from generate_data import generate
from run import run_once

FILES = ["reps.csv", "accounts.csv", "stages.csv", "deals.csv", "deal_history.csv", "activities.csv",
         "injected_issues.json"]


def test_same_seed_gives_identical_data(tmp_path):
    a, b = tmp_path / "a", tmp_path / "b"
    generate(a, 42)
    generate(b, 42)
    for f in FILES:
        assert (a / f).read_bytes() == (b / f).read_bytes(), f


def test_committed_sample_is_exactly_seed_42(tmp_path):
    generate(tmp_path, 42)
    for f in FILES:
        assert (tmp_path / f).read_bytes() == (SAMPLE / f).read_bytes(), f"{f} differs from seed 42 output"


def test_different_seed_gives_different_data(tmp_path):
    generate(tmp_path / "a", 42)
    generate(tmp_path / "b", 7)
    assert (tmp_path / "a" / "deal_history.csv").read_bytes() != (tmp_path / "b" / "deal_history.csv").read_bytes()


def test_same_data_gives_identical_outputs(tmp_path):
    outs = []
    for name in ("run1", "run2"):
        out = tmp_path / name
        assert run_once(SAMPLE, out, "2026-W34") == 0
        outs.append(out)
    produced = sorted(p.relative_to(outs[0]) for p in outs[0].rglob("*") if p.is_file() and p.name != "run_log.csv")
    assert any(str(p).endswith(".png") for p in produced)
    for rel in produced:
        assert (outs[0] / rel).read_bytes() == (outs[1] / rel).read_bytes(), rel
