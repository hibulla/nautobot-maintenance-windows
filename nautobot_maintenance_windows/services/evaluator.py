"""UTC schedule evaluation services."""

from dataclasses import dataclass
from datetime import datetime, time, timezone
from math import floor
from typing import Iterable

from django.db.models import Prefetch

from nautobot_maintenance_windows.choices import (
    ChangeValidationResultChoices,
    MaintenanceStateChoices,
    MaintenanceWindowTypeChoices,
)
from nautobot_maintenance_windows.models import MaintenanceWindow, MaintenanceWindowSchedule

SECONDS_PER_DAY = 24 * 60 * 60
SECONDS_PER_WEEK = 7 * SECONDS_PER_DAY


@dataclass(frozen=True)
class ScheduleMatch:
    """A matched window schedule."""

    window: MaintenanceWindow
    schedule: MaintenanceWindowSchedule
    device: object | None = None


@dataclass(frozen=True)
class DeviceEvaluation:
    """Current maintenance state for a device."""

    device: object
    state: str
    matched_windows: tuple[ScheduleMatch, ...]
    evaluated_at: datetime


@dataclass(frozen=True)
class ChangeValidation:
    """Validation outcome for a proposed change interval."""

    result: str
    blocked_by: tuple[ScheduleMatch, ...]
    maintenance_matches: tuple[ScheduleMatch, ...]
    evaluated_start: datetime
    evaluated_end: datetime


def require_utc_datetime(value: datetime, field_name: str = "timestamp") -> datetime:
    """Require an aware UTC datetime."""
    if not isinstance(value, datetime):
        raise TypeError(f"{field_name} must be a datetime.")
    if value.tzinfo is None:
        raise ValueError(f"{field_name} must include explicit UTC timezone information.")
    if value.utcoffset() != timezone.utc.utcoffset(value):
        raise ValueError(f"{field_name} must be expressed in UTC.")
    return value


def schedule_contains(schedule: MaintenanceWindowSchedule, timestamp: datetime) -> bool:
    """Return whether a schedule contains a UTC timestamp."""
    timestamp = require_utc_datetime(timestamp)
    second = _datetime_week_second(timestamp)
    start = _schedule_week_second(schedule.start_day_of_week, schedule.start_time)
    end = _schedule_week_second(schedule.end_day_of_week, schedule.end_time)
    if start < end:
        return start <= second < end
    return second >= start or second < end


def schedule_overlaps_interval(schedule: MaintenanceWindowSchedule, start: datetime, end: datetime) -> bool:
    """Return whether a weekly recurring schedule overlaps a UTC interval."""
    start = require_utc_datetime(start, "start")
    end = require_utc_datetime(end, "end")
    if start >= end:
        raise ValueError("Change window start must be before end.")

    interval_start = _absolute_week_second(start)
    interval_end = _absolute_week_second(end)
    schedule_start = _schedule_week_second(schedule.start_day_of_week, schedule.start_time)
    schedule_end = _schedule_week_second(schedule.end_day_of_week, schedule.end_time)
    if schedule_start > schedule_end:
        schedule_end += SECONDS_PER_WEEK

    first_week = floor(interval_start / SECONDS_PER_WEEK) - 1
    last_week = floor(interval_end / SECONDS_PER_WEEK) + 1
    for week in range(first_week, last_week + 1):
        occurrence_start = week * SECONDS_PER_WEEK + schedule_start
        occurrence_end = week * SECONDS_PER_WEEK + schedule_end
        if occurrence_start < interval_end and interval_start < occurrence_end:
            return True
    return False


def evaluate_device(device, evaluated_at: datetime | None = None) -> DeviceEvaluation:
    """Evaluate the current state of one device against assigned active windows."""
    timestamp = require_utc_datetime(evaluated_at or datetime.now(timezone.utc), "evaluated_at")
    matches = tuple(_matching_schedules(_assigned_windows(device), timestamp))

    if any(match.window.window_type == MaintenanceWindowTypeChoices.EXCLUSION for match in matches):
        state = MaintenanceStateChoices.IN_EXCLUSION
    elif any(match.window.window_type == MaintenanceWindowTypeChoices.MAINTENANCE for match in matches):
        state = MaintenanceStateChoices.IN_MAINTENANCE
    else:
        state = MaintenanceStateChoices.NONE
    return DeviceEvaluation(device=device, state=state, matched_windows=matches, evaluated_at=timestamp)


def evaluate_devices(devices: Iterable, evaluated_at: datetime | None = None) -> tuple[DeviceEvaluation, ...]:
    """Evaluate multiple devices."""
    timestamp = require_utc_datetime(evaluated_at or datetime.now(timezone.utc), "evaluated_at")
    device_list = list(devices)
    windows_by_device = _assigned_windows_by_device(device_list)
    return tuple(_evaluate_device_windows(device, windows_by_device.get(device.pk, ()), timestamp) for device in device_list)


def validate_change_window(devices: Iterable, start: datetime, end: datetime) -> ChangeValidation:
    """Evaluate whether an external change interval is blocked by assigned exclusion windows."""
    start = require_utc_datetime(start, "start")
    end = require_utc_datetime(end, "end")
    if start >= end:
        raise ValueError("Change window start must be before end.")

    device_list = list(devices)
    windows_by_device = _assigned_windows_by_device(device_list)
    blocked = []
    maintenance = []
    for device in device_list:
        for window in windows_by_device.get(device.pk, ()):
            for schedule in window.schedules.all():
                if schedule_overlaps_interval(schedule, start, end):
                    match = ScheduleMatch(window=window, schedule=schedule, device=device)
                    if window.window_type == MaintenanceWindowTypeChoices.EXCLUSION:
                        blocked.append(match)
                    else:
                        maintenance.append(match)

    if blocked:
        result = ChangeValidationResultChoices.BLOCKED
    else:
        result = ChangeValidationResultChoices.ALLOWED
    return ChangeValidation(
        result=result,
        blocked_by=tuple(blocked),
        maintenance_matches=tuple(maintenance),
        evaluated_start=start,
        evaluated_end=end,
    )


def _assigned_windows(device):
    return (
        MaintenanceWindow.objects.filter(device_assignments__device=device, is_active=True)
        .prefetch_related(Prefetch("schedules", queryset=MaintenanceWindowSchedule.objects.all()))
        .distinct()
    )


def _assigned_windows_by_device(devices):
    device_ids = [device.pk for device in devices]
    if not device_ids:
        return {}

    windows = (
        MaintenanceWindow.objects.filter(device_assignments__device_id__in=device_ids, is_active=True)
        .prefetch_related(
            Prefetch("schedules", queryset=MaintenanceWindowSchedule.objects.all()),
            Prefetch("device_assignments"),
        )
        .distinct()
    )
    windows_by_device = {device.pk: [] for device in devices}
    device_id_set = set(device_ids)
    for window in windows:
        for assignment in window.device_assignments.all():
            if assignment.device_id in device_id_set:
                windows_by_device[assignment.device_id].append(window)
    return windows_by_device


def _evaluate_device_windows(device, windows, timestamp: datetime) -> DeviceEvaluation:
    matches = tuple(_matching_schedules(windows, timestamp, device=device))
    if any(match.window.window_type == MaintenanceWindowTypeChoices.EXCLUSION for match in matches):
        state = MaintenanceStateChoices.IN_EXCLUSION
    elif any(match.window.window_type == MaintenanceWindowTypeChoices.MAINTENANCE for match in matches):
        state = MaintenanceStateChoices.IN_MAINTENANCE
    else:
        state = MaintenanceStateChoices.NONE
    return DeviceEvaluation(device=device, state=state, matched_windows=matches, evaluated_at=timestamp)


def _matching_schedules(windows, timestamp: datetime, device=None):
    for window in windows:
        for schedule in window.schedules.all():
            if schedule_contains(schedule, timestamp):
                yield ScheduleMatch(window=window, schedule=schedule, device=device)


def _datetime_week_second(value: datetime) -> int:
    return value.weekday() * SECONDS_PER_DAY + value.hour * 3600 + value.minute * 60 + value.second


def _absolute_week_second(value: datetime) -> int:
    days = value.toordinal() - 1
    return days * SECONDS_PER_DAY + value.hour * 3600 + value.minute * 60 + value.second


def _schedule_week_second(day_of_week: int, value: time) -> int:
    return day_of_week * SECONDS_PER_DAY + value.hour * 3600 + value.minute * 60 + value.second
