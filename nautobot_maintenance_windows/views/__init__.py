"""UI views for nautobot_maintenance_windows."""

from nautobot_maintenance_windows.views.assignments import DeviceMaintenanceWindowAssignmentUIViewSet
from nautobot_maintenance_windows.views.schedules import MaintenanceWindowScheduleUIViewSet
from nautobot_maintenance_windows.views.windows import MaintenanceWindowUIViewSet

__all__ = (
    "DeviceMaintenanceWindowAssignmentUIViewSet",
    "MaintenanceWindowScheduleUIViewSet",
    "MaintenanceWindowUIViewSet",
)
