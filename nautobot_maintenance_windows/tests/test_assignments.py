"""Tests for device assignment behavior."""

from nautobot.apps.testing import TestCase

from nautobot_maintenance_windows.models import DeviceMaintenanceWindowAssignment
from nautobot_maintenance_windows.tests.utils import create_test_device, create_window


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
