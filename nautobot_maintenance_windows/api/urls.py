"""API URL patterns for nautobot_maintenance_windows."""

from nautobot.apps.api import OrderedDefaultRouter

from nautobot_maintenance_windows.api import views

router = OrderedDefaultRouter()
router.register("maintenance-windows", views.MaintenanceWindowViewSet)
router.register("schedules", views.MaintenanceWindowScheduleViewSet)
router.register("device-assignments", views.DeviceMaintenanceWindowAssignmentViewSet)

app_name = "nautobot-maintenance-windows-api"
urlpatterns = router.urls
