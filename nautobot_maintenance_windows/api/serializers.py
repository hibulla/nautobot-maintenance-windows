"""API serializers for nautobot_maintenance_windows."""

from nautobot.apps.api import NautobotModelSerializer, ValidatedModelSerializer
from rest_framework import serializers

from nautobot_maintenance_windows import models


class MaintenanceWindowSerializer(NautobotModelSerializer):
    """Serialize MaintenanceWindow records."""

    device_count = serializers.IntegerField(read_only=True)
    schedule_count = serializers.IntegerField(read_only=True)

    class Meta:
        """Meta attributes."""

        model = models.MaintenanceWindow
        fields = [
            "id",
            "url",
            "display",
            "name",
            "description",
            "is_active",
            "window_type",
            "device_count",
            "schedule_count",
            "created",
            "last_updated",
        ]


class MaintenanceWindowScheduleSerializer(ValidatedModelSerializer):
    """Serialize MaintenanceWindowSchedule records."""

    class Meta:
        """Meta attributes."""

        model = models.MaintenanceWindowSchedule
        fields = [
            "id",
            "url",
            "display",
            "maintenance_window",
            "start_day_of_week",
            "start_time",
            "end_day_of_week",
            "end_time",
            "timezone",
        ]
        read_only_fields = ["timezone"]


class DeviceMaintenanceWindowAssignmentSerializer(ValidatedModelSerializer):
    """Serialize DeviceMaintenanceWindowAssignment records."""

    class Meta:
        """Meta attributes."""

        model = models.DeviceMaintenanceWindowAssignment
        fields = ["id", "url", "display", "device", "maintenance_window"]
