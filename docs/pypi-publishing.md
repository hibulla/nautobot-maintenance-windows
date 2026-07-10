# Publishing to PyPI

This document describes how to configure PyPI and GitHub so releases of `nautobot-maintenance-windows` are published automatically by the `Publish to PyPI` workflow.

The preferred method is PyPI Trusted Publishing. Use an API token only when Trusted Publishing is not available for the PyPI project yet.

## Current Repository Values

Use these values when configuring PyPI and GitHub:

| Field | Value |
| --- | --- |
| PyPI project name | `nautobot-maintenance-windows` |
| GitHub owner / organization | `hibulla` |
| GitHub repository | `nautobot-maintenance-windows` |
| GitHub workflow filename | `publish.yml` |
| GitHub workflow path | `.github/workflows/publish.yml` |
| GitHub environment | `pypi` |
| Release tag format | `vX.Y.Z`, for example `v0.1.0` |
| GitHub secret fallback | `PYPI_API_TOKEN` |

The publishing workflow is triggered only by tags matching `v*`. It validates that the tag matches the version in `pyproject.toml`, builds the package with `python -m build`, validates it with `twine check`, and publishes it to PyPI.

## Option A: Trusted Publishing

Trusted Publishing is the recommended configuration. It lets GitHub Actions publish to PyPI without storing a long-lived PyPI API token in GitHub secrets.

### Create the GitHub Environment

1. Open the GitHub repository.
2. Go to `Settings` -> `Environments`.
3. Create a new environment named:

```text
pypi
```

4. Optional but recommended: add required reviewers for the environment.
5. Optional but recommended: restrict deployments to release tags matching the release policy.

The environment name must match the value configured in PyPI. This repository's workflow uses `environment: pypi`.

### If the PyPI Project Does Not Exist Yet

Use a pending Trusted Publisher.

1. Log in to PyPI.
2. Open your account publishing settings.
3. Add a new pending publisher.
4. Select `GitHub Actions`.
5. Fill in the fields:

| PyPI field | Value |
| --- | --- |
| PyPI project name | `nautobot-maintenance-windows` |
| Owner | `hibulla` |
| Repository name | `nautobot-maintenance-windows` |
| Workflow name / workflow filename | `publish.yml` |
| Environment name | `pypi` |

6. Save the pending publisher.

A pending publisher does not reserve the project name. The project is created only when the first publish succeeds. If another user registers the name before the first release, the pending publisher will no longer be valid.

### If the PyPI Project Already Exists

Use a normal Trusted Publisher attached to the existing project.

1. Log in to PyPI.
2. Open the `nautobot-maintenance-windows` project.
3. Go to `Manage` -> `Publishing`.
4. Add a new publisher.
5. Select `GitHub Actions`.
6. Fill in the fields:

| PyPI field | Value |
| --- | --- |
| Owner | `hibulla` |
| Repository name | `nautobot-maintenance-windows` |
| Workflow name / workflow filename | `publish.yml` |
| Environment name | `pypi` |

7. Save the publisher.

After this, the configured GitHub workflow can request a short-lived PyPI publishing token through OpenID Connect during release runs.

## Option B: API Token Fallback

Use this only if Trusted Publishing is not configured.

### Create the Token in PyPI

1. Log in to PyPI.
2. Verify the account email address if it is not already verified.
3. Open `Account settings`.
4. Go to the `API tokens` section.
5. Select `Add API token`.
6. Fill in the fields:

| PyPI field | Recommended value |
| --- | --- |
| Token name | `GitHub Actions - nautobot-maintenance-windows` |
| Scope | `Project: nautobot-maintenance-windows` if the project already exists |

If the project does not exist yet and Trusted Publishing is not used, PyPI cannot create a project-scoped token for that project. In that case, use a temporary account-scoped token for the first upload, then replace it with a project-scoped token immediately after the project exists.

Copy the generated token value. It starts with `pypi-` and is shown only once.

### Add the Token to GitHub

1. Open the GitHub repository.
2. Go to `Settings` -> `Secrets and variables` -> `Actions`.
3. Select `New repository secret`.
4. Fill in:

| GitHub field | Value |
| --- | --- |
| Name | `PYPI_API_TOKEN` |
| Secret | the full PyPI token value, including the `pypi-` prefix |

5. Save the secret.

When `PYPI_API_TOKEN` exists, the workflow publishes with the token fallback. When the secret is absent, the workflow attempts Trusted Publishing.

## Release Checklist

1. Update the version in `pyproject.toml`.
2. Update `CHANGELOG.md`.
3. Run local validation:

```shell
python -m ruff check nautobot_maintenance_windows pyproject.toml
python -m compileall nautobot_maintenance_windows
python -m build
python -m twine check dist/*
```

4. Commit the release:

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

7. Watch the `Publish to PyPI` workflow in GitHub Actions.
8. Confirm the release appears on:

```text
https://pypi.org/project/nautobot-maintenance-windows/
```

## Troubleshooting

### `invalid-publisher` or `invalid-pending-publisher`

Check that these values match exactly between PyPI and GitHub:

- owner: `hibulla`
- repository: `nautobot-maintenance-windows`
- workflow filename: `publish.yml`
- environment: `pypi`

Also check that the workflow still has `id-token: write` permission.

### Tag Does Not Match Version

The workflow requires the tag to match the package version.

If `pyproject.toml` contains:

```toml
version = "0.1.0"
```

the tag must be:

```shell
git tag v0.1.0
```

### Project Name Conflict

For pending Trusted Publishing, PyPI does not reserve the package name until the first successful publish. If the name is taken before the first publish, choose a new package name and update `pyproject.toml`, PyPI publisher settings, and documentation.

### Token Authentication Fails

For API token fallback:

- the GitHub secret name must be exactly `PYPI_API_TOKEN`
- the secret value must include the `pypi-` prefix
- the token should be scoped to `nautobot-maintenance-windows` after the project exists
- if the token is revoked or regenerated in PyPI, update the GitHub secret

## References

- PyPI Trusted Publishing: <https://docs.pypi.org/trusted-publishers/>
- Adding a Trusted Publisher: <https://docs.pypi.org/trusted-publishers/adding-a-publisher/>
- Creating a PyPI Project with a Trusted Publisher: <https://docs.pypi.org/trusted-publishers/creating-a-project-through-oidc/>
- Publishing with a Trusted Publisher: <https://docs.pypi.org/trusted-publishers/using-a-publisher/>
- PyPI API tokens: <https://pypi.org/help/#apitoken>
