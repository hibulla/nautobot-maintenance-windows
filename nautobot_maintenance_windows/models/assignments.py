"""Device to MaintenanceWindow assignment model."""

from django.db import models
from nautobot.apps.models import BaseModel


class DeviceMaintenanceWindowAssignment(BaseModel):
    """Extension record linking a Device to a global MaintenanceWindow."""

    is_metadata_associable_model = False

    device = models.ForeignKey(
        to="dcim.Device",
        on_delete=models.CASCADE,
        related_name="maintenance_window_assignments",
    )
    maintenance_window = models.ForeignKey(
        to="nautobot_maintenance_windows.MaintenanceWindow",
        on_delete=models.CASCADE,
        related_name="device_assignments",
    )

    class Meta:
        """Meta attributes."""

        ordering = ["device__name", "maintenance_window__name"]
        unique_together = ("device", "maintenance_window")
        verbose_name = "Device Maintenance Window Assignment"
        verbose_name_plural = "Device Maintenance Window Assignments"

    def __str__(self):
        """Stringify instance."""
        return f"{self.device}: {self.maintenance_window}"
