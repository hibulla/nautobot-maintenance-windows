"""Views for MaintenanceWindowSchedule."""

from nautobot.apps.views import NautobotUIViewSet

from nautobot_maintenance_windows import filters, forms, models, tables
from nautobot_maintenance_windows.api import serializers


class MaintenanceWindowScheduleUIViewSet(NautobotUIViewSet):
    """ViewSet for MaintenanceWindowSchedule CRUD views."""

    bulk_update_form_class = forms.MaintenanceWindowScheduleBulkEditForm
    filterset_class = filters.MaintenanceWindowScheduleFilterSet
    filterset_form_class = forms.MaintenanceWindowScheduleFilterForm
    form_class = forms.MaintenanceWindowScheduleForm
    lookup_field = "pk"
    queryset = models.MaintenanceWindowSchedule.objects.select_related("maintenance_window")
    serializer_class = serializers.MaintenanceWindowScheduleSerializer
    table_class = tables.MaintenanceWindowScheduleTable
