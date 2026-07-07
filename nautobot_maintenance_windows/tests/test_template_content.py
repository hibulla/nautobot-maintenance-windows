"""Tests for Nautobot template extensions."""

from unittest import TestCase

from nautobot.apps.ui import SectionChoices

from nautobot_maintenance_windows import tables
from nautobot_maintenance_windows.template_content import DeviceMaintenanceWindowContent, template_extensions


class DeviceMaintenanceWindowContentTest(TestCase):
    """Test Device detail template extension registration."""

    def test_device_detail_panel_is_registered(self):
        """Device details include the Maintenance Windows panel."""
        self.assertIn(DeviceMaintenanceWindowContent, template_extensions)
        self.assertEqual(DeviceMaintenanceWindowContent.model, "dcim.device")

        panel = DeviceMaintenanceWindowContent.object_detail_panels[0]
        self.assertIsInstance(panel, tables.DeviceMaintenanceWindowsPanel)
        self.assertEqual(panel.section, SectionChoices.FULL_WIDTH)
