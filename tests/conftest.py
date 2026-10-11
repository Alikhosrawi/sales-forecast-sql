import shutil
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from pipeline.engine import run_pipeline  # noqa: E402

SAMPLE = ROOT / "data" / "sample"
TINY = ROOT / "tests" / "fixtures" / "tiny"


@pytest.fixture(scope="session")
def sample_result():
    return run_pipeline(SAMPLE)


@pytest.fixture
def sample_copy(tmp_path):
    """A writable copy of the sample data, for tests that break it on purpose."""
    dst = tmp_path / "data"
    shutil.copytree(SAMPLE, dst)
    return dst
