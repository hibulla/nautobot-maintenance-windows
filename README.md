# Nautobot Maintenance Windows

[![CI](https://github.com/hibulla/nautobot-maintenance-windows/actions/workflows/ci.yml/badge.svg)](https://github.com/hibulla/nautobot-maintenance-windows/actions/workflows/ci.yml)

A Nautobot app for managing global UTC maintenance windows and exclusion windows for network devices.

The app helps NetDevOps teams answer two operational questions:

- Is a device currently inside an assigned maintenance or exclusion window?
- Would a proposed change window overlap any assigned exclusion window?

It is intentionally informational and evaluative. It does not implement priority, conflict resolution, approval workflows, or change orchestration logic. Those decisions remain with Nautobot Jobs, CI/CD pipelines, change systems, or other external automation.

## Features

- Global `MaintenanceWindow` objects.
- `MAINTENANCE` and `EXCLUSION` window types.
- Explicit many-to-many assignments between Nautobot `Device` objects and maintenance windows.
- Normalized relational schedules via `MaintenanceWindowSchedule`.
- Strict UTC-only schedule handling.
- Support for schedules that cross midnight or span multiple days.
- Nautobot UI views, tables, forms, navigation, and RBAC permissions.
- REST API serializers, filters, and viewsets.
- Nautobot Jobs for device eligibility, change validation, and bulk assignment.
- Unit tests for schedule matching, exclusion blocking, jobs, and assignment behavior.

## Compatibility

- Nautobot: `>=3.1.0,<4.0.0`
- Python: `>=3.12,<3.15`

## Data Model

### MaintenanceWindow

Global object representing either an allowed maintenance period or a blackout period.

Fields:

- `name`
- `description`
- `is_active`
- `window_type`
  - `MAINTENANCE`
  - `EXCLUSION`

### MaintenanceWindowSchedule

Normalized UTC schedule attached to a `MaintenanceWindow`.

Fields:

- `maintenance_window`
- `start_day_of_week`, where Monday is `0` and Sunday is `6`
- `start_time`
- `end_day_of_week`
- `end_time`
- `timezone`, always `UTC`

All schedules are UTC-only. The app does not perform local timezone conversion and does not include DST logic.

### DeviceMaintenanceWindowAssignment

Explicit through model linking devices to maintenance windows.

This is used instead of a hidden many-to-many table so the assignment model can be extended later with operational metadata such as source system, owner, reason, ticket ID, or expiration policy.

## Behavior

`EXCLUSION` windows represent blackout periods where changes must be blocked by consuming automation.

`MAINTENANCE` windows are informational only. A proposed change that overlaps only maintenance windows is returned as `ALLOWED`, with matching maintenance windows included in the job output for context.

The app does not resolve conflicts or prioritize windows. If a device matches both `MAINTENANCE` and `EXCLUSION` at the same time, device eligibility reports `IN_EXCLUSION` and includes all matched windows.

## Jobs

### Device Maintenance Eligibility

Evaluates selected devices at the current UTC timestamp.

Output per device:

- `IN_MAINTENANCE`
- `IN_EXCLUSION`
- `NONE`
- matched windows
- matched schedule details
- UTC evaluation timestamp

### Change Validation

Evaluates selected devices against a proposed UTC change interval.

Inputs:

- devices
- proposed start, ISO-8601 UTC datetime
- proposed end, ISO-8601 UTC datetime

Output:

- `BLOCKED` if any assigned `EXCLUSION` schedule overlaps the proposed interval
- `ALLOWED` otherwise
- per-device exclusion matches
- per-device maintenance matches for informational context

Datetime inputs must include explicit UTC timezone information, for example:

```text
2026-07-06T09:00:00+00:00
```

### Bulk Maintenance Window Assignment

Assigns or unassigns selected maintenance windows from selected devices.

The job is idempotent:

- existing assignments are counted as unchanged
- missing assignments during unassign are counted as unchanged
- integrity errors are logged and returned in the summary

## REST API

The app exposes API endpoints for:

- maintenance windows
- schedules
- device assignments

Assignments should be managed through `DeviceMaintenanceWindowAssignment`; direct many-to-many mutation on `MaintenanceWindow.devices` is intentionally not part of the public serializer surface.

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

Run migrations and restart Nautobot:

```shell
nautobot-server migrate
nautobot-server post_upgrade
sudo systemctl restart nautobot nautobot-worker
```

## Development

Install dependencies:

```shell
poetry install
```

Run syntax validation:

```shell
python -m compileall nautobot_maintenance_windows
```

Run tests from a configured Nautobot development environment:

```shell
nautobot-server test nautobot_maintenance_windows
```

## Continuous Integration

GitHub Actions runs on pushes to `main` and on pull requests.

The CI workflow currently checks:

- dependency installation with Poetry
- Ruff linting
- Python source compilation
- package build

## Design Notes

- All schedule values are UTC.
- Naive datetimes are rejected in change validation paths.
- Schedule logic lives in `nautobot_maintenance_windows.services.evaluator`.
- Models contain only minimal validation and relational constraints.
- The explicit assignment model is the extension point for future enterprise metadata.
- The app reports facts; external automation decides what to do with those facts.

## License

Apache-2.0
