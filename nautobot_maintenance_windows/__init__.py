"""App declaration for nautobot_maintenance_windows."""

from importlib import metadata

from nautobot.apps import NautobotAppConfig

try:
    __version__ = metadata.version(__name__)
except metadata.PackageNotFoundError:
    __version__ = "0.1.0"


class NautobotMaintenanceWindowsConfig(NautobotAppConfig):
    """App configuration for the nautobot_maintenance_windows app."""

    name = "nautobot_maintenance_windows"
    verbose_name = "Maintenance Windows"
    version = __version__
    author = "Hibulla.com"
    description = "Manage UTC maintenance and exclusion windows for network devices."
    base_url = "maintenance-windows"
    min_version = "3.1.0"
    max_version = "4.0.0"
    required_settings = []
    default_settings = {}
    searchable_models = ["maintenancewindow"]


config = NautobotMaintenanceWindowsConfig  # pylint: disable=invalid-name
