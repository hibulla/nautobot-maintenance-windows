# Development Guide

This project is packaged with standard Python packaging metadata in `pyproject.toml`.

## Local Environment

Create a virtual environment:

```shell
python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
```

Install the app in editable mode with development dependencies:

```shell
python -m pip install -e ".[dev]"
```

## Local Checks

Run linting:

```shell
python -m ruff check nautobot_maintenance_windows pyproject.toml
```

Run syntax validation:

```shell
python -m compileall nautobot_maintenance_windows
```

Build and validate distributions:

```shell
python -m build
python -m twine check dist/*
```

Run app tests from a configured Nautobot environment:

```shell
nautobot-server test nautobot_maintenance_windows
```

## CI Coverage

GitHub Actions runs on every push and pull request.

The CI workflow checks:

- dependency installation from `pyproject.toml`
- Ruff linting
- Python source compilation
- package build with `python -m build`
- package metadata validation with `twine check`
- Nautobot Docker image build with this app installed
- Nautobot system checks
- database migrations
- app tests against PostgreSQL and Redis

## Release Process

Releases are published to PyPI only from Git tags matching `v*`.

1. Update the package version in `pyproject.toml`.
2. Update `CHANGELOG.md`.
3. Run the local checks.
4. Commit the release changes:

```shell
git add pyproject.toml CHANGELOG.md
git commit -m "Release X.Y.Z"
```

5. Create a matching tag:

```shell
git tag vX.Y.Z
```

6. Push the commit and tag:

```shell
git push origin main
git push origin vX.Y.Z
```

Pushing the tag starts the `Publish to PyPI` workflow. The workflow validates that the tag matches the package version, builds the package, runs `twine check`, and publishes the distribution to PyPI.

The publishing workflow supports PyPI Trusted Publishing when the repository and PyPI project are configured for it. If Trusted Publishing is not configured, add a repository secret named `PYPI_API_TOKEN`; when that secret is present, the workflow publishes with the API token instead.

## Packaging Notes

- Project metadata lives in `pyproject.toml`.
- The Python package name is `nautobot-maintenance-windows`.
- The importable module name is `nautobot_maintenance_windows`.
- The Nautobot plugin package is enabled as `nautobot_maintenance_windows`.
- Templates are included as package data.
- The license file is included in source and wheel distributions.

## Compatibility Policy

The package currently supports:

- Nautobot `>=3.1.0,<4.0.0`
- Python `>=3.12,<3.15`

Compatibility changes should be reflected in:

- `pyproject.toml`
- `README.md`
- `CHANGELOG.md`
- CI matrix in `.github/workflows/ci.yml`
