All Python must follow PEP 8 with line length <= 88, meaningful inline comments,
and Google style docstrings. Use Ruff in strict mode with:

```
[tool.ruff]
select = ["ALL"]
ignore = ["D203", "ANN101"]
line-length = 88
target-version = "py311"
```

Run `pre-commit install` to enable `astral-sh/ruff-pre-commit` (with --fix) and
`pre-commit run --all-files` before committing. Unit tests are required and
coverage may not fall below 90%.

CI runs only `pytest --cov=src --cov-report=xml --cov-fail-under=90`.
Use https://github.com/astral-sh/ruff-pre-commit to lint locally.
