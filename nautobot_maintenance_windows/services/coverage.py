"""Coverage reporting services for Maintenance Windows."""

from dataclasses import dataclass

from django.db.models import Count, Q
from nautobot.dcim.models import Device

from nautobot_maintenance_windows.choices import MaintenanceWindowTypeChoices
from nautobot_maintenance_windows.models import MaintenanceWindow, MaintenanceWindowSchedule


@dataclass(frozen=True)
class CoverageReport:
    """Maintenance Window coverage report."""

    total_devices: int
    covered_devices: int
    uncovered_devices: int
    active_windows: int
    windows_without_schedules_count: int
    active_assignments: int
    inactive_assigned_windows_count: int
    schedules_without_device_impact_count: int
    devices_only_exclusion_count: int
    devices_without_windows: object
    windows_without_schedules: object
    inactive_assigned_windows: object
    schedules_without_device_impact: object
    devices_only_exclusion: object

    @property
    def summary(self):
        """Return a compact summary dictionary."""
        return {
            "total_devices": self.total_devices,
            "covered_devices": self.covered_devices,
            "uncovered_devices": self.uncovered_devices,
            "active_windows": self.active_windows,
            "windows_without_schedules": self.windows_without_schedules_count,
            "active_assignments": self.active_assignments,
            "inactive_assigned_windows": self.inactive_assigned_windows_count,
            "schedules_without_device_impact": self.schedules_without_device_impact_count,
            "devices_only_exclusion": self.devices_only_exclusion_count,
        }

    @property
    def log_lines(self):
        """Return job-friendly report lines."""
        return [
            f"Devices without active Maintenance Window assignments: {self.uncovered_devices}",
            f"Maintenance Windows without schedules: {self.windows_without_schedules_count}",
            f"Inactive Maintenance Windows assigned to devices: {self.inactive_assigned_windows_count}",
            f"Schedules without device impact: {self.schedules_without_device_impact_count}",
            f"Devices with only EXCLUSION windows: {self.devices_only_exclusion_count}",
        ]


def get_coverage_report(user=None):
    """Build a Maintenance Window coverage report."""
    device_queryset = Device.objects.all()
    if user is not None:
        device_queryset = device_queryset.restrict(user, "view")

    window_queryset = MaintenanceWindow.objects.all()
    if user is not None:
        window_queryset = window_queryset.restrict(user, "view")

    schedule_queryset = MaintenanceWindowSchedule.objects.select_related("maintenance_window")
    if user is not None:
        schedule_queryset = schedule_queryset.filter(maintenance_window__in=window_queryset)

    devices_with_counts = device_queryset.annotate(
        active_window_count=Count(
            "maintenance_window_assignments",
            filter=Q(maintenance_window_assignments__maintenance_window__is_active=True),
            distinct=True,
        ),
        active_maintenance_count=Count(
            "maintenance_window_assignments",
            filter=Q(
                maintenance_window_assignments__maintenance_window__is_active=True,
                maintenance_window_assignments__maintenance_window__window_type=MaintenanceWindowTypeChoices.MAINTENANCE,
            ),
            distinct=True,
        ),
        active_exclusion_count=Count(
            "maintenance_window_assignments",
            filter=Q(
                maintenance_window_assignments__maintenance_window__is_active=True,
                maintenance_window_assignments__maintenance_window__window_type=MaintenanceWindowTypeChoices.EXCLUSION,
            ),
            distinct=True,
        ),
    )

    devices_without_windows = devices_with_counts.filter(active_window_count=0).order_by("name")
    devices_only_exclusion = devices_with_counts.filter(
        active_window_count__gt=0,
        active_exclusion_count__gt=0,
        active_maintenance_count=0,
    ).order_by("name")

    windows_with_counts = window_queryset.annotate(
        schedule_count=Count("schedules", distinct=True),
        assigned_device_count=Count("device_assignments", distinct=True),
    )
    windows_without_schedules = windows_with_counts.filter(schedule_count=0).order_by("name")
    inactive_assigned_windows = windows_with_counts.filter(is_active=False, device_assignments__isnull=False).distinct()

    schedules_without_device_impact = schedule_queryset.annotate(
        active_device_count=Count(
            "maintenance_window__device_assignments",
            filter=Q(maintenance_window__is_active=True),
            distinct=True,
        ),
    ).filter(active_device_count=0)

    total_devices = device_queryset.count()
    uncovered_devices = devices_without_windows.count()
    return CoverageReport(
        total_devices=total_devices,
        covered_devices=total_devices - uncovered_devices,
        uncovered_devices=uncovered_devices,
        active_windows=window_queryset.filter(is_active=True).count(),
        windows_without_schedules_count=windows_without_schedules.count(),
        active_assignments=window_queryset.filter(is_active=True).aggregate(
            assignment_count=Count("device_assignments", distinct=True)
        )["assignment_count"],
        inactive_assigned_windows_count=inactive_assigned_windows.count(),
        schedules_without_device_impact_count=schedules_without_device_impact.count(),
        devices_only_exclusion_count=devices_only_exclusion.count(),
        devices_without_windows=devices_without_windows,
        windows_without_schedules=windows_without_schedules,
        inactive_assigned_windows=inactive_assigned_windows.order_by("name"),
        schedules_without_device_impact=schedules_without_device_impact.order_by(
            "maintenance_window__name",
            "start_day_of_week",
            "start_time",
        ),
        devices_only_exclusion=devices_only_exclusion,
    )
