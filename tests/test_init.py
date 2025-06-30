"""Basic sanity check for the src package."""

import importlib.util
import sys
from pathlib import Path

EXPECTED_SUM = 3


def test_sanity() -> None:
    """Import package and verify simple math."""
    root = Path(__file__).resolve().parents[1]
    spec_path = root / "src" / "__init__.py"
    spec = importlib.util.spec_from_file_location("src", spec_path)
    module = importlib.util.module_from_spec(spec)
    sys.modules["src"] = module
    spec.loader.exec_module(module)

    assert module.add(1, 2) == EXPECTED_SUM  # noqa: S101
