"""Views for MaintenanceWindow."""

from django.db.models import Count
from nautobot.apps.ui import ObjectDetailContent, ObjectFieldsPanel, SectionChoices
from nautobot.apps.views import NautobotUIViewSet

from nautobot_maintenance_windows import filters, forms, models, tables
from nautobot_maintenance_windows.api import serializers


class MaintenanceWindowUIViewSet(NautobotUIViewSet):
    """ViewSet for MaintenanceWindow CRUD views."""

    bulk_update_form_class = forms.MaintenanceWindowBulkEditForm
    filterset_class = filters.MaintenanceWindowFilterSet
    filterset_form_class = forms.MaintenanceWindowFilterForm
    form_class = forms.MaintenanceWindowForm
    lookup_field = "pk"
    queryset = models.MaintenanceWindow.objects.annotate(
        device_count=Count("device_assignments", distinct=True),
        schedule_count=Count("schedules", distinct=True),
    )
    serializer_class = serializers.MaintenanceWindowSerializer
    table_class = tables.MaintenanceWindowTable

    object_detail_content = ObjectDetailContent(
        panels=[
            ObjectFieldsPanel(
                weight=100,
                section=SectionChoices.LEFT_HALF,
                fields=["name", "description", "is_active", "window_type", "created", "last_updated"],
            ),
            tables.MaintenanceWindowSchedulesPanel(weight=200, section=SectionChoices.RIGHT_HALF),
            tables.MaintenanceWindowAssignedDevicesPanel(weight=300, section=SectionChoices.FULL_WIDTH),
        ],
    )
