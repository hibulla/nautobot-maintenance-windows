"""Initial database schema for nautobot_maintenance_windows."""

import uuid

import django.core.serializers.json
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ("dcim", "__first__"),
    ]

    operations = [
        migrations.CreateModel(
            name="MaintenanceWindow",
            fields=[
                (
                    "id",
                    models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, unique=True),
                ),
                ("created", models.DateTimeField(auto_now_add=True, null=True)),
                ("last_updated", models.DateTimeField(auto_now=True, null=True)),
                (
                    "_custom_field_data",
                    models.JSONField(blank=True, default=dict, encoder=django.core.serializers.json.DjangoJSONEncoder),
                ),
                ("name", models.CharField(max_length=255, unique=True)),
                ("description", models.TextField(blank=True)),
                ("is_active", models.BooleanField(default=True)),
                (
                    "window_type",
                    models.CharField(
                        choices=[("MAINTENANCE", "Maintenance"), ("EXCLUSION", "Exclusion")],
                        default="MAINTENANCE",
                        max_length=32,
                    ),
                ),
            ],
            options={
                "verbose_name": "Maintenance Window",
                "verbose_name_plural": "Maintenance Windows",
                "ordering": ["name"],
            },
        ),
        migrations.CreateModel(
            name="DeviceMaintenanceWindowAssignment",
            fields=[
                (
                    "id",
                    models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, unique=True),
                ),
                (
                    "device",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="maintenance_window_assignments",
                        to="dcim.device",
                    ),
                ),
                (
                    "maintenance_window",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="device_assignments",
                        to="nautobot_maintenance_windows.maintenancewindow",
                    ),
                ),
            ],
            options={
                "verbose_name": "Device Maintenance Window Assignment",
                "verbose_name_plural": "Device Maintenance Window Assignments",
                "ordering": ["device__name", "maintenance_window__name"],
                "unique_together": {("device", "maintenance_window")},
            },
        ),
        migrations.CreateModel(
            name="MaintenanceWindowSchedule",
            fields=[
                (
                    "id",
                    models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, unique=True),
                ),
                (
                    "start_day_of_week",
                    models.PositiveSmallIntegerField(
                        choices=[
                            (0, "Monday"),
                            (1, "Tuesday"),
                            (2, "Wednesday"),
                            (3, "Thursday"),
                            (4, "Friday"),
                            (5, "Saturday"),
                            (6, "Sunday"),
                        ],
                    ),
                ),
                ("start_time", models.TimeField(help_text="UTC time only.")),
                (
                    "end_day_of_week",
                    models.PositiveSmallIntegerField(
                        choices=[
                            (0, "Monday"),
                            (1, "Tuesday"),
                            (2, "Wednesday"),
                            (3, "Thursday"),
                            (4, "Friday"),
                            (5, "Saturday"),
                            (6, "Sunday"),
                        ],
                    ),
                ),
                ("end_time", models.TimeField(help_text="UTC time only.")),
                ("timezone", models.CharField(default="UTC", editable=False, max_length=3)),
                (
                    "maintenance_window",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="schedules",
                        to="nautobot_maintenance_windows.maintenancewindow",
                    ),
                ),
            ],
            options={
                "verbose_name": "Maintenance Window Schedule",
                "verbose_name_plural": "Maintenance Window Schedules",
                "ordering": ["maintenance_window__name", "start_day_of_week", "start_time"],
                "unique_together": {
                    ("maintenance_window", "start_day_of_week", "start_time", "end_day_of_week", "end_time")
                },
            },
        ),
        migrations.AddField(
            model_name="maintenancewindow",
            name="devices",
            field=models.ManyToManyField(
                blank=True,
                related_name="maintenance_windows",
                through="nautobot_maintenance_windows.DeviceMaintenanceWindowAssignment",
                to="dcim.device",
            ),
        ),
        migrations.AddConstraint(
            model_name="maintenancewindowschedule",
            constraint=models.CheckConstraint(
                check=models.Q(("start_day_of_week__gte", 0), ("start_day_of_week__lte", 6)),
                name="maintenance_windows_start_day_0_6",
            ),
        ),
        migrations.AddConstraint(
            model_name="maintenancewindowschedule",
            constraint=models.CheckConstraint(
                check=models.Q(("end_day_of_week__gte", 0), ("end_day_of_week__lte", 6)),
                name="maintenance_windows_end_day_0_6",
            ),
        ),
        migrations.AddConstraint(
            model_name="maintenancewindowschedule",
            constraint=models.CheckConstraint(check=models.Q(("timezone", "UTC")), name="maintenance_windows_timezone_utc"),
        ),
        migrations.AddConstraint(
            model_name="maintenancewindowschedule",
            constraint=models.CheckConstraint(
                check=~models.Q(
                    start_day_of_week=models.F("end_day_of_week"),
                    start_time=models.F("end_time"),
                ),
                name="maintenance_windows_start_end_not_equal",
            ),
        ),
    ]
