# Contributing

Contributions are welcome through GitHub issues and pull requests.

## Development Setup

Create a virtual environment and install development dependencies:

```shell
python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
```

## Checks

Run these checks before opening a pull request:

```shell
python -m ruff check nautobot_maintenance_windows pyproject.toml
python -m compileall nautobot_maintenance_windows
python -m build
python -m twine check dist/*
```

Run Nautobot tests from a configured Nautobot development environment:

```shell
nautobot-server test nautobot_maintenance_windows
```

## Pull Requests

Please keep pull requests focused.

For behavior changes, include or update tests. For user-facing behavior, update the relevant documentation in `README.md` or `docs/`.

## Design Constraints

- All schedule values must remain UTC.
- Do not add local timezone or DST conversion semantics.
- `EXCLUSION` windows block consuming automation.
- `MAINTENANCE` windows are informational.
- Keep assignments as explicit first-class records.
- Preserve Nautobot compatibility for the supported version range in `pyproject.toml`.

## Reporting Bugs

When reporting a bug, include:

- Nautobot version
- Python version
- package version
- installation method
- relevant traceback or job log output
- minimal steps to reproduce
