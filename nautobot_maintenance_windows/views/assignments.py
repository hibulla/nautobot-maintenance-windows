"""Views for DeviceMaintenanceWindowAssignment."""

from nautobot.apps.views import NautobotUIViewSet

from nautobot_maintenance_windows import filters, forms, models, tables
from nautobot_maintenance_windows.api import serializers


class DeviceMaintenanceWindowAssignmentUIViewSet(NautobotUIViewSet):
    """ViewSet for DeviceMaintenanceWindowAssignment CRUD views."""

    bulk_update_form_class = forms.DeviceMaintenanceWindowAssignmentBulkEditForm
    filterset_class = filters.DeviceMaintenanceWindowAssignmentFilterSet
    filterset_form_class = forms.DeviceMaintenanceWindowAssignmentFilterForm
    form_class = forms.DeviceMaintenanceWindowAssignmentForm
    lookup_field = "pk"
    queryset = models.DeviceMaintenanceWindowAssignment.objects.select_related("device", "maintenance_window")
    serializer_class = serializers.DeviceMaintenanceWindowAssignmentSerializer
    table_class = tables.DeviceMaintenanceWindowAssignmentTable
