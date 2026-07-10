# Nautobot Maintenance Windows

[![CI](https://github.com/hibulla/nautobot-maintenance-windows/actions/workflows/ci.yml/badge.svg)](https://github.com/hibulla/nautobot-maintenance-windows/actions/workflows/ci.yml)
[![License](https://img.shields.io/badge/license-Apache--2.0-blue.svg)](LICENSE)

A Nautobot app for managing global UTC maintenance windows and exclusion windows for network devices.

The app helps NetDevOps teams answer two operational questions:

- Is a device currently inside an assigned maintenance or exclusion window?
- Would a proposed change window overlap any assigned exclusion window?

It is intentionally informational and evaluative. It does not implement priority, conflict resolution, approval workflows, or change orchestration logic. Those decisions remain with Nautobot Jobs, CI/CD pipelines, change systems, or other external automation.

## Features

- Global `MaintenanceWindow` records.
- `MAINTENANCE` and `EXCLUSION` window types.
- Explicit assignments between Nautobot `Device` records and maintenance windows.
- Normalized weekly UTC schedules via `MaintenanceWindowSchedule`.
- Support for schedules that cross midnight or span multiple days.
- Nautobot UI views, tables, forms, navigation, and RBAC permissions.
- Coverage dashboard for identifying incomplete Maintenance Window data.
- REST API serializers, filters, and viewsets.
- Nautobot Jobs for device eligibility, change validation, coverage audit, and bulk assignment.
- Tests for schedule matching, exclusion blocking, jobs, template content, and assignment behavior.

## Compatibility

| Component | Supported versions |
| --- | --- |
| Nautobot | `>=3.1.0,<4.0.0` |
| Python | `>=3.12,<3.15` |

All schedule values are UTC. The app does not perform local timezone conversion and does not include DST logic.

## Installation

Install the package into the Nautobot environment:

```shell
pip install nautobot-maintenance-windows
```

Enable the app in `nautobot_config.py`:

```python
PLUGINS = [
    "nautobot_maintenance_windows",
]
```

Run migrations and Nautobot post-upgrade tasks:

```shell
nautobot-server migrate
nautobot-server post_upgrade
```

Restart Nautobot services. The exact service names depend on your deployment, for example:

```shell
sudo systemctl restart nautobot nautobot-worker
```

## Quick Start

1. Open the Nautobot `Maintenance` navigation tab.
2. Create a `Maintenance Window`.
3. Add one or more UTC `Schedules` to the window.
4. Assign the window to devices through `Device Assignments` or the bulk assignment job.
5. Use the eligibility and change-validation jobs, REST API, or consuming automation to evaluate device state.

Example schedule:

| Field | Value |
| --- | --- |
| Window type | `EXCLUSION` |
| Start day | `Friday` |
| Start time | `22:00` |
| End day | `Saturday` |
| End time | `02:00` |
| Timezone | `UTC` |

This schedule blocks changes every Friday 22:00 UTC through Saturday 02:00 UTC for assigned devices.

## Documentation

- [Usage Guide](docs/usage.md)
- [REST API](docs/api.md)
- [Development Guide](docs/development.md)
- [Changelog](CHANGELOG.md)
- [Security Policy](SECURITY.md)
- [Contributing](CONTRIBUTING.md)

## Core Concepts

### MaintenanceWindow

Global object representing either an allowed maintenance period or a blackout period.

Main fields:

- `name`
- `description`
- `is_active`
- `window_type`: `MAINTENANCE` or `EXCLUSION`

### MaintenanceWindowSchedule

Normalized UTC weekly recurrence attached to a `MaintenanceWindow`.

Main fields:

- `maintenance_window`
- `start_day_of_week`, where Monday is `0` and Sunday is `6`
- `start_time`
- `end_day_of_week`
- `end_time`
- `timezone`, always `UTC`

### DeviceMaintenanceWindowAssignment

Explicit through model linking devices to maintenance windows.

Assignments are intentionally modeled as first-class records so they can be extended later with operational metadata such as source system, owner, reason, ticket ID, or expiration policy.

## Behavior

`EXCLUSION` windows represent blackout periods where changes must be blocked by consuming automation.

`MAINTENANCE` windows are informational. A proposed change that overlaps only maintenance windows is returned as `ALLOWED`, with matching maintenance windows included in the output for context.

The app does not resolve conflicts or prioritize windows. If a device matches both `MAINTENANCE` and `EXCLUSION` at the same time, device eligibility reports `IN_EXCLUSION` and includes all matched windows.

## Jobs

The app registers four Nautobot Jobs:

- `Device Maintenance Eligibility`: reports the current UTC maintenance state for selected devices.
- `Change Validation`: returns `BLOCKED` when any assigned `EXCLUSION` schedule overlaps a proposed UTC change interval.
- `Bulk Maintenance Window Assignment`: assigns or unassigns selected windows from selected devices.
- `Audit Maintenance Window Coverage`: reports devices and windows with incomplete Maintenance Window data.

Datetime inputs for change validation must include explicit UTC timezone information:

```text
2026-07-06T09:00:00+00:00
```

## REST API

The app exposes plugin API endpoints for:

- maintenance windows
- schedules
- device assignments

Assignments should be managed through `DeviceMaintenanceWindowAssignment`; direct many-to-many mutation on `MaintenanceWindow.devices` is intentionally not part of the public serializer surface.

See [REST API](docs/api.md) for endpoint paths and payload examples.

## Development

Create a virtual environment and install the app with development dependencies:

```shell
python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
```

Run local checks:

```shell
python -m ruff check nautobot_maintenance_windows pyproject.toml
python -m compileall nautobot_maintenance_windows
python -m build
python -m twine check dist/*
```

Run tests from a configured Nautobot development environment:

```shell
nautobot-server test nautobot_maintenance_windows
```

See [Development Guide](docs/development.md) for the CI test matrix and release process.

## License

This project is licensed under the Apache License 2.0. See [LICENSE](LICENSE).
