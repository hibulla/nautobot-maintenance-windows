"""Tests for Maintenance Window coverage reporting."""

from nautobot.apps.testing import TestCase

from nautobot_maintenance_windows.choices import MaintenanceWindowTypeChoices
from nautobot_maintenance_windows.models import DeviceMaintenanceWindowAssignment
from nautobot_maintenance_windows.services.coverage import get_coverage_report
from nautobot_maintenance_windows.tests.utils import create_schedule, create_test_device, create_window


class CoverageReportTest(TestCase):
    """Test coverage report categories."""

    def test_coverage_report_identifies_data_gaps(self):
        uncovered_device = create_test_device(name="uncovered-device")
        exclusion_only_device = create_test_device(name="exclusion-only-device")
        inactive_device = create_test_device(name="inactive-device")

        exclusion = create_window(name="Exclusion Only", window_type=MaintenanceWindowTypeChoices.EXCLUSION)
        inactive = create_window(name="Inactive Assigned")
        inactive.is_active = False
        inactive.save()
        unscheduled = create_window(name="No Schedule")
        no_impact = create_window(name="No Impact")
        schedule_without_impact = create_schedule(no_impact)

        DeviceMaintenanceWindowAssignment.objects.create(device=exclusion_only_device, maintenance_window=exclusion)
        DeviceMaintenanceWindowAssignment.objects.create(device=inactive_device, maintenance_window=inactive)

        report = get_coverage_report()

        self.assertIn(uncovered_device, report.devices_without_windows)
        self.assertIn(inactive_device, report.devices_without_windows)
        self.assertIn(exclusion_only_device, report.devices_only_exclusion)
        self.assertIn(unscheduled, report.windows_without_schedules)
        self.assertIn(inactive, report.inactive_assigned_windows)
        self.assertIn(schedule_without_impact, report.schedules_without_device_impact)
        self.assertEqual(report.summary["devices_only_exclusion"], 1)
