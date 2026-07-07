"""Template extensions for nautobot_maintenance_windows."""

from nautobot.apps.ui import SectionChoices, TemplateExtension

from nautobot_maintenance_windows import tables


class DeviceMaintenanceWindowContent(TemplateExtension):
    """Add MaintenanceWindow assignments to Nautobot Device detail views."""

    model = "dcim.device"
    object_detail_panels = (
        tables.DeviceMaintenanceWindowsPanel(
            weight=900,
            section=SectionChoices.FULL_WIDTH,
            required_permissions=["nautobot_maintenance_windows.view_devicemaintenancewindowassignment"],
        ),
    )


template_extensions = [DeviceMaintenanceWindowContent]
