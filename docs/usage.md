# Usage Guide

This guide describes how to use Nautobot Maintenance Windows after the app has been installed and enabled.

## Navigation

The app adds a `Maintenance` navigation tab with these views:

- `Maintenance Windows`
- `Coverage`
- `Schedules`
- `Device Assignments`

Access to individual views follows Nautobot object permissions.

## Modeling Maintenance Policy

Use `MaintenanceWindow` records to describe global operational windows:

- `MAINTENANCE`: an allowed maintenance period. These windows are informational.
- `EXCLUSION`: a blackout period. Consuming automation should block changes during these windows.

Each window can have multiple schedules and can be assigned to multiple devices.

## Schedule Rules

All schedules are UTC.

The app stores weekly recurring schedules with these fields:

- `start_day_of_week`: Monday is `0`, Sunday is `6`
- `start_time`: UTC time in `HH:MM` format
- `end_day_of_week`: Monday is `0`, Sunday is `6`
- `end_time`: UTC time in `HH:MM` format
- `timezone`: always `UTC`

Schedules may cross midnight or span multiple days.

Example:

| Start | End | Meaning |
| --- | --- | --- |
| Monday `01:00` | Monday `03:00` | Two-hour Monday window |
| Friday `22:00` | Saturday `02:00` | Four-hour overnight window |
| Saturday `18:00` | Sunday `06:00` | Weekend overnight window |

Schedules with identical start and end day/time are rejected.

## Assigning Windows to Devices

Use `DeviceMaintenanceWindowAssignment` records to attach windows to devices.

Assignments can be created from:

- the `Device Assignments` UI
- the assigned devices panel on a Maintenance Window detail page
- the REST API
- the `Bulk Maintenance Window Assignment` job

The assignment model is explicit by design. It is the future extension point for metadata such as owner, source system, ticket ID, reason, or expiration policy.

## Evaluation Behavior

Device state evaluation returns one of:

- `IN_EXCLUSION`
- `IN_MAINTENANCE`
- `NONE`

If a device matches both `MAINTENANCE` and `EXCLUSION` windows at the same time, the state is `IN_EXCLUSION`.

Change validation returns:

- `BLOCKED` if any assigned `EXCLUSION` schedule overlaps the proposed change interval
- `ALLOWED` otherwise

Matching `MAINTENANCE` windows are returned as context, but they do not block changes.

## Jobs

### Device Maintenance Eligibility

Evaluates selected devices at the current UTC timestamp.

Returned data includes:

- device
- state
- matched windows
- matched schedule details
- UTC evaluation timestamp

### Change Validation

Evaluates selected devices against a proposed UTC interval.

Inputs:

- devices
- proposed start in ISO-8601 UTC format
- proposed end in ISO-8601 UTC format

Valid input example:

```text
2026-07-06T09:00:00+00:00
```

Naive datetimes and non-UTC datetimes are rejected.

### Bulk Maintenance Window Assignment

Assigns or unassigns selected maintenance windows from selected devices.

The job is idempotent:

- existing assignments are counted as unchanged
- missing assignments during unassign are counted as unchanged
- integrity errors are logged and returned in the summary

### Audit Maintenance Window Coverage

Reports data quality gaps:

- devices without active Maintenance Window assignments
- Maintenance Windows without schedules
- inactive Maintenance Windows still assigned to devices
- schedules without device impact
- devices with only exclusion windows

## Coverage Dashboard

The coverage dashboard is available from the `Coverage` navigation item.

Use it to find incomplete data before relying on the app in change automation. The dashboard is informational and does not modify objects.

## Permissions

The app uses normal Nautobot object permissions.

Operators who only need to inspect state should have view permissions for:

- `Maintenance Window`
- `Maintenance Window Schedule`
- `Device Maintenance Window Assignment`

Operators who manage assignments need add/change/delete permissions for `Device Maintenance Window Assignment`.

Operators who run bulk assignment need permission to add or delete assignment records depending on the selected action.

## Operational Notes

- Keep all external automation inputs in UTC.
- Do not use local wall-clock time in API or job inputs.
- Use `EXCLUSION` for blackout periods that should block changes.
- Use `MAINTENANCE` for informational allowed windows.
- Treat the app output as policy facts; the consuming automation decides whether and how to enforce those facts.
