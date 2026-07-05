"""Filtering for nautobot_maintenance_windows."""

from nautobot.apps.filters import NaturalKeyOrPKMultipleChoiceFilter, NautobotFilterSet, SearchFilter
from nautobot.dcim.models import Device

from nautobot_maintenance_windows import models


class MaintenanceWindowFilterSet(NautobotFilterSet):
    """FilterSet for MaintenanceWindow."""

    q = SearchFilter(filter_predicates={"name": "icontains", "description": "icontains"})
    device = NaturalKeyOrPKMultipleChoiceFilter(
        field_name="device_assignments__device",
        queryset=Device.objects.all(),
        to_field_name="name",
    )

    class Meta:
        """Meta attributes."""

        model = models.MaintenanceWindow
        fields = "__all__"


class MaintenanceWindowScheduleFilterSet(NautobotFilterSet):
    """FilterSet for MaintenanceWindowSchedule."""

    maintenance_window = NaturalKeyOrPKMultipleChoiceFilter(
        field_name="maintenance_window",
        queryset=models.MaintenanceWindow.objects.all(),
        to_field_name="name",
    )

    class Meta:
        """Meta attributes."""

        model = models.MaintenanceWindowSchedule
        fields = "__all__"


class DeviceMaintenanceWindowAssignmentFilterSet(NautobotFilterSet):
    """FilterSet for DeviceMaintenanceWindowAssignment."""

    device = NaturalKeyOrPKMultipleChoiceFilter(field_name="device", queryset=Device.objects.all(), to_field_name="name")
    maintenance_window = NaturalKeyOrPKMultipleChoiceFilter(
        field_name="maintenance_window",
        queryset=models.MaintenanceWindow.objects.all(),
        to_field_name="name",
    )

    class Meta:
        """Meta attributes."""

        model = models.DeviceMaintenanceWindowAssignment
        fields = "__all__"
