"""Coverage dashboard views."""

from django.contrib.auth.mixins import PermissionRequiredMixin
from django.shortcuts import render
from django.views import View
from django_tables2 import RequestConfig

from nautobot_maintenance_windows import tables
from nautobot_maintenance_windows.services.coverage import get_coverage_report


class CoverageDashboardView(PermissionRequiredMixin, View):
    """Read-only coverage dashboard for Maintenance Window data quality."""

    permission_required = "nautobot_maintenance_windows.view_maintenancewindow"
    template_name = "nautobot_maintenance_windows/coverage.html"

    def get(self, request):
        """Render the dashboard."""
        report = get_coverage_report(request.user)
        table_map = {
            "devices_without_windows_table": tables.CoverageDeviceTable(report.devices_without_windows),
            "windows_without_schedules_table": tables.CoverageMaintenanceWindowTable(report.windows_without_schedules),
            "inactive_assigned_windows_table": tables.CoverageMaintenanceWindowTable(report.inactive_assigned_windows),
            "schedules_without_device_impact_table": tables.CoverageScheduleTable(report.schedules_without_device_impact),
            "devices_only_exclusion_table": tables.CoverageDeviceTable(report.devices_only_exclusion),
        }
        for table in table_map.values():
            RequestConfig(request, paginate={"per_page": 50}).configure(table)

        return render(
            request,
            self.template_name,
            {
                "report": report,
                "summary": report.summary,
                **table_map,
            },
        )
