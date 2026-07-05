"""Menu items."""

from nautobot.apps.ui import NavMenuAddButton, NavMenuGroup, NavMenuItem, NavMenuTab

maintenance_window_items = (
    NavMenuItem(
        link="plugins:nautobot_maintenance_windows:maintenancewindow_list",
        name="Maintenance Windows",
        permissions=["nautobot_maintenance_windows.view_maintenancewindow"],
        buttons=(
            NavMenuAddButton(
                link="plugins:nautobot_maintenance_windows:maintenancewindow_add",
                permissions=["nautobot_maintenance_windows.add_maintenancewindow"],
            ),
        ),
    ),
    NavMenuItem(
        link="plugins:nautobot_maintenance_windows:coverage",
        name="Coverage",
        permissions=["nautobot_maintenance_windows.view_maintenancewindow"],
    ),
    NavMenuItem(
        link="plugins:nautobot_maintenance_windows:maintenancewindowschedule_list",
        name="Schedules",
        permissions=["nautobot_maintenance_windows.view_maintenancewindowschedule"],
        buttons=(
            NavMenuAddButton(
                link="plugins:nautobot_maintenance_windows:maintenancewindowschedule_add",
                permissions=["nautobot_maintenance_windows.add_maintenancewindowschedule"],
            ),
        ),
    ),
    NavMenuItem(
        link="plugins:nautobot_maintenance_windows:devicemaintenancewindowassignment_list",
        name="Device Assignments",
        permissions=["nautobot_maintenance_windows.view_devicemaintenancewindowassignment"],
        buttons=(
            NavMenuAddButton(
                link="plugins:nautobot_maintenance_windows:devicemaintenancewindowassignment_add",
                permissions=["nautobot_maintenance_windows.add_devicemaintenancewindowassignment"],
            ),
        ),
    ),
)

menu_items = (
    NavMenuTab(
        name="Maintenance Windows",
        icon="mdi mdi-calendar-clock",
        groups=(
            NavMenuGroup(
                name="Maintenance Windows",
                items=maintenance_window_items,
            ),
        ),
    ),
)
