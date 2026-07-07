"""Tables for nautobot_maintenance_windows."""

import django_tables2 as tables
from django.utils.html import format_html_join
from nautobot.apps.tables import BaseTable, BooleanColumn, ButtonsColumn, LinkedCountColumn, ToggleColumn
from nautobot.apps.ui import ObjectsTablePanel
from nautobot.dcim.models import Device

from nautobot_maintenance_windows import models


class MaintenanceWindowTable(BaseTable):
    """Table for MaintenanceWindow list view."""

    pk = ToggleColumn()
    name = tables.Column(linkify=True)
    is_active = BooleanColumn()
    device_count = LinkedCountColumn(
        viewname="plugins:nautobot_maintenance_windows:devicemaintenancewindowassignment_list",
        url_params={"maintenance_window": "name"},
        verbose_name="Devices",
    )
    schedule_count = LinkedCountColumn(
        viewname="plugins:nautobot_maintenance_windows:maintenancewindowschedule_list",
        url_params={"maintenance_window": "name"},
        verbose_name="Schedules",
    )
    actions = ButtonsColumn(models.MaintenanceWindow, pk_field="pk")

    class Meta(BaseTable.Meta):
        """Meta attributes."""

        model = models.MaintenanceWindow
        fields = ("pk", "name", "window_type", "description", "is_active", "device_count", "schedule_count", "actions")
        default_columns = ("pk", "name", "window_type", "is_active", "device_count", "schedule_count", "actions")


class MaintenanceWindowScheduleTable(BaseTable):
    """Table for MaintenanceWindowSchedule list view."""

    pk = ToggleColumn()
    maintenance_window = tables.Column(linkify=True)
    actions = ButtonsColumn(models.MaintenanceWindowSchedule, pk_field="pk")

    class Meta(BaseTable.Meta):
        """Meta attributes."""

        model = models.MaintenanceWindowSchedule
        fields = (
            "pk",
            "maintenance_window",
            "start_day_of_week",
            "start_time",
            "end_day_of_week",
            "end_time",
            "timezone",
            "actions",
        )
        default_columns = fields


class DeviceMaintenanceWindowAssignmentTable(BaseTable):
    """Table for DeviceMaintenanceWindowAssignment list view."""

    pk = ToggleColumn()
    device = tables.Column(linkify=True, order_by=("device__name",))
    maintenance_window = tables.Column(linkify=True, order_by=("maintenance_window__name",))
    actions = ButtonsColumn(models.DeviceMaintenanceWindowAssignment, pk_field="pk")

    class Meta(BaseTable.Meta):
        """Meta attributes."""

        model = models.DeviceMaintenanceWindowAssignment
        fields = ("pk", "device", "maintenance_window", "actions")
        default_columns = fields


class DeviceAssignedMaintenanceWindowTable(BaseTable):
    """Read-only table for MaintenanceWindow assignments on a Device detail view."""

    maintenance_window = tables.Column(linkify=True, order_by=("maintenance_window__name",))
    window_type = tables.Column(
        accessor="maintenance_window.window_type",
        order_by=("maintenance_window__window_type",),
        verbose_name="Type",
    )
    is_active = BooleanColumn(
        accessor="maintenance_window.is_active",
        order_by=("maintenance_window__is_active",),
        verbose_name="Active",
    )
    schedules = tables.Column(empty_values=(), orderable=False, verbose_name="Schedules")

    class Meta(BaseTable.Meta):
        """Meta attributes."""

        model = models.DeviceMaintenanceWindowAssignment
        fields = ("maintenance_window", "window_type", "is_active", "schedules")
        default_columns = fields

    @staticmethod
    def render_window_type(record):
        """Render the MaintenanceWindow type label."""
        return record.maintenance_window.get_window_type_display()

    @staticmethod
    def render_schedules(record):
        """Render assigned MaintenanceWindow schedules as concrete UTC intervals."""
        schedules = record.maintenance_window.schedules.all()
        if not schedules:
            return "No schedules"
        return format_html_join("", "<div>{}</div>", ((_format_schedule(schedule),) for schedule in schedules))


class CoverageDeviceTable(BaseTable):
    """Read-only device table for coverage reports."""

    name = tables.Column(linkify=True)
    status = tables.Column(linkify=True)
    role = tables.Column(linkify=True)
    location = tables.Column(linkify=True)

    class Meta(BaseTable.Meta):
        """Meta attributes."""

        model = Device
        fields = ("name", "status", "role", "location")
        default_columns = fields


class CoverageMaintenanceWindowTable(BaseTable):
    """Read-only MaintenanceWindow table for coverage reports."""

    name = tables.Column(linkify=True)
    is_active = BooleanColumn()

    class Meta(BaseTable.Meta):
        """Meta attributes."""

        model = models.MaintenanceWindow
        fields = ("name", "window_type", "is_active", "schedule_count", "assigned_device_count")
        default_columns = fields


class CoverageScheduleTable(BaseTable):
    """Read-only MaintenanceWindowSchedule table for coverage reports."""

    maintenance_window = tables.Column(linkify=True)

    class Meta(BaseTable.Meta):
        """Meta attributes."""

        model = models.MaintenanceWindowSchedule
        fields = ("maintenance_window", "start_day_of_week", "start_time", "end_day_of_week", "end_time", "timezone")
        default_columns = fields


class MaintenanceWindowSchedulesPanel(ObjectsTablePanel):
    """Detail panel listing schedules assigned to a MaintenanceWindow."""

    label = "Schedules"
    table_class = MaintenanceWindowScheduleTable
    table_attribute = "schedules"
    related_field_name = "maintenance_window"
    exclude_columns = ["maintenance_window"]
    add_button_route = None


class MaintenanceWindowAssignedDevicesPanel(ObjectsTablePanel):
    """Detail panel listing devices assigned to a MaintenanceWindow."""

    label = "Assigned Devices"
    table_class = DeviceMaintenanceWindowAssignmentTable
    table_attribute = "device_assignments"
    related_field_name = "maintenance_window"
    exclude_columns = ["maintenance_window"]
    add_button_route = None


class DeviceMaintenanceWindowsPanel(ObjectsTablePanel):
    """Detail panel listing MaintenanceWindows assigned to a Device."""

    label = "Maintenance Windows"
    table_class = DeviceAssignedMaintenanceWindowTable
    table_attribute = "maintenance_window_assignments"
    table_title = "Assigned Windows"
    related_field_name = "device"
    select_related_fields = ["maintenance_window"]
    prefetch_related_fields = ["maintenance_window__schedules"]
    add_button_route = None
    enable_bulk_actions = False


def _format_schedule(schedule):
    start = f"{schedule.start_time:%H:%M}"
    end = f"{schedule.end_time:%H:%M}"
    start_day = schedule.get_start_day_of_week_display()
    end_day = schedule.get_end_day_of_week_display()
    if schedule.start_day_of_week == schedule.end_day_of_week:
        return f"{start_day} {start}-{end} UTC"
    return f"{start_day} {start} - {end_day} {end} UTC"
