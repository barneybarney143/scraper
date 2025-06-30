def test_sanity():
    """Simple sanity check importing the package."""
    import sys
    import importlib.util
    from pathlib import Path

    root = Path(__file__).resolve().parents[1]
    spec_path = root / "src" / "__init__.py"
    spec = importlib.util.spec_from_file_location("src", spec_path)
    module = importlib.util.module_from_spec(spec)
    sys.modules["src"] = module
    spec.loader.exec_module(module)

    assert module.add(1, 2) == 3
