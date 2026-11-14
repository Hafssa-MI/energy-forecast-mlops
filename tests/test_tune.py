import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from tune import expand_grid  # noqa: E402


def test_expand_grid_cartesian_product():
    g = expand_grid({"a": [1, 2], "b": ["x"]})
    assert g == [{"a": 1, "b": "x"}, {"a": 2, "b": "x"}]


def test_expand_grid_keeps_list_values():
    g = expand_grid({"units_grid": [[16], [32]]})
    assert g == [{"units_grid": [16]}, {"units_grid": [32]}]