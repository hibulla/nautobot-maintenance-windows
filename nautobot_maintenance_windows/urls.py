"""Django urlpatterns declaration for nautobot_maintenance_windows app."""

from nautobot.apps.urls import NautobotUIViewSetRouter

from nautobot_maintenance_windows import views

app_name = "nautobot_maintenance_windows"
router = NautobotUIViewSetRouter()

router.register("maintenance-windows", views.MaintenanceWindowUIViewSet)
router.register("schedules", views.MaintenanceWindowScheduleUIViewSet)
router.register("device-assignments", views.DeviceMaintenanceWindowAssignmentUIViewSet)

urlpatterns = router.urls
