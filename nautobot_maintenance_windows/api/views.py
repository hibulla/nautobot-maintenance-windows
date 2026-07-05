"""API views for nautobot_maintenance_windows."""

from django.db.models import Count
from nautobot.apps.api import NautobotModelViewSet

from nautobot_maintenance_windows import filters, models
from nautobot_maintenance_windows.api import serializers


class MaintenanceWindowViewSet(NautobotModelViewSet):
    """REST API viewset for MaintenanceWindow."""

    queryset = models.MaintenanceWindow.objects.annotate(
        device_count=Count("device_assignments", distinct=True),
        schedule_count=Count("schedules", distinct=True),
    )
    serializer_class = serializers.MaintenanceWindowSerializer
    filterset_class = filters.MaintenanceWindowFilterSet


class MaintenanceWindowScheduleViewSet(NautobotModelViewSet):
    """REST API viewset for MaintenanceWindowSchedule."""

    queryset = models.MaintenanceWindowSchedule.objects.select_related("maintenance_window")
    serializer_class = serializers.MaintenanceWindowScheduleSerializer
    filterset_class = filters.MaintenanceWindowScheduleFilterSet


class DeviceMaintenanceWindowAssignmentViewSet(NautobotModelViewSet):
    """REST API viewset for DeviceMaintenanceWindowAssignment."""

    queryset = models.DeviceMaintenanceWindowAssignment.objects.select_related("device", "maintenance_window")
    serializer_class = serializers.DeviceMaintenanceWindowAssignmentSerializer
    filterset_class = filters.DeviceMaintenanceWindowAssignmentFilterSet
