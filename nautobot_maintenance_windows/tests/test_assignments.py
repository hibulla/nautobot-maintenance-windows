"""Tests for device assignment behavior."""

from datetime import time

from nautobot.apps.testing import TestCase

from nautobot_maintenance_windows import tables
from nautobot_maintenance_windows.models import DeviceMaintenanceWindowAssignment
from nautobot_maintenance_windows.tests.utils import create_schedule, create_test_device, create_window


class DeviceMaintenanceWindowAssignmentTest(TestCase):
    """Test explicit many-to-many assignment model."""

    def test_device_can_have_many_windows(self):
        device = create_test_device()
        first = create_window(name="First")
        second = create_window(name="Second")

        DeviceMaintenanceWindowAssignment.objects.create(device=device, maintenance_window=first)
        DeviceMaintenanceWindowAssignment.objects.create(device=device, maintenance_window=second)

        self.assertEqual(device.maintenance_window_assignments.count(), 2)
        self.assertEqual(first.device_assignments.count(), 1)

    def test_device_detail_assignment_table_renders_schedule_intervals(self):
        device = create_test_device()
        window = create_window(name="Scheduled")
        create_schedule(window, start_day_of_week=0, start_time=time(1, 0), end_day_of_week=0, end_time=time(2, 30))
        create_schedule(window, start_day_of_week=5, start_time=time(23, 0), end_day_of_week=6, end_time=time(1, 0))
        assignment = DeviceMaintenanceWindowAssignment.objects.create(device=device, maintenance_window=window)

        rendered = tables.DeviceAssignedMaintenanceWindowTable.render_schedules(assignment)

        self.assertIn("Monday 01:00-02:30 UTC", rendered)
        self.assertIn("Saturday 23:00 - Sunday 01:00 UTC", rendered)
