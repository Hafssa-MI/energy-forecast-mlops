
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest

pytest.importorskip("mlflow")
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from promote import better  # noqa: E402


def mv(mae):
    return SimpleNamespace(tags={"mae": str(mae)})


def test_first_model_is_promoted():
    assert better(1000, None, 0.02)


def test_small_gain_is_not_promoted():
    assert not better(990, mv(1000), 0.02)  # 1% < 2%


def test_large_gain_is_promoted():
    assert better(900, mv(1000), 0.02)
