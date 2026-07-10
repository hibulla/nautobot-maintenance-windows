# REST API

Nautobot Maintenance Windows exposes REST API endpoints under the Nautobot plugin API namespace.

The exact root depends on the Nautobot deployment URL. In a default deployment, the endpoints are available below:

```text
/api/plugins/maintenance-windows/
```

## Endpoints

| Resource | Endpoint |
| --- | --- |
| Maintenance windows | `/api/plugins/maintenance-windows/maintenance-windows/` |
| Schedules | `/api/plugins/maintenance-windows/schedules/` |
| Device assignments | `/api/plugins/maintenance-windows/device-assignments/` |

## Authentication and Permissions

Use standard Nautobot REST API authentication and object permissions.

The API does not bypass Nautobot RBAC. Users and tokens need the same object permissions they would need in the UI.

## Maintenance Windows

### Fields

- `id`
- `url`
- `display`
- `name`
- `description`
- `is_active`
- `window_type`
- `device_count`
- `schedule_count`
- `created`
- `last_updated`

### Create Example

```json
{
  "name": "Weekly Core Maintenance",
  "description": "Standard weekly core network maintenance window.",
  "is_active": true,
  "window_type": "MAINTENANCE"
}
```

Valid `window_type` values:

- `MAINTENANCE`
- `EXCLUSION`

## Schedules

### Fields

- `id`
- `url`
- `display`
- `maintenance_window`
- `start_day_of_week`
- `start_time`
- `end_day_of_week`
- `end_time`
- `timezone`

`timezone` is read-only and always set to `UTC`.

Day values:

| Value | Day |
| --- | --- |
| `0` | Monday |
| `1` | Tuesday |
| `2` | Wednesday |
| `3` | Thursday |
| `4` | Friday |
| `5` | Saturday |
| `6` | Sunday |

### Create Example

```json
{
  "maintenance_window": "00000000-0000-0000-0000-000000000000",
  "start_day_of_week": 4,
  "start_time": "22:00:00",
  "end_day_of_week": 5,
  "end_time": "02:00:00"
}
```

This creates a Friday 22:00 UTC through Saturday 02:00 UTC schedule.

## Device Assignments

### Fields

- `id`
- `url`
- `display`
- `device`
- `maintenance_window`

### Create Example

```json
{
  "device": "00000000-0000-0000-0000-000000000001",
  "maintenance_window": "00000000-0000-0000-0000-000000000000"
}
```

Assignments should be managed through `DeviceMaintenanceWindowAssignment`.

Direct many-to-many mutation on `MaintenanceWindow.devices` is intentionally not part of the public serializer surface.

## API Usage Notes

- Use object IDs accepted by your Nautobot API version for related fields.
- Send schedule times in UTC.
- Do not send the `timezone` field when creating or updating schedules.
- Use `EXCLUSION` windows for blackout periods that should block consuming automation.
- Use `MAINTENANCE` windows for informational allowed windows.
- Run the `Change Validation` job when you need interval-based change approval output.
