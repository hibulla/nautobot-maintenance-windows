"""Tests for UTC schedule evaluation."""

from datetime import datetime, time, timezone

from nautobot.apps.testing import TestCase

from nautobot_maintenance_windows.choices import (
    ChangeValidationResultChoices,
    MaintenanceStateChoices,
    MaintenanceWindowTypeChoices,
)
from nautobot_maintenance_windows.models import DeviceMaintenanceWindowAssignment
from nautobot_maintenance_windows.services.evaluator import (
    evaluate_device,
    schedule_contains,
    schedule_overlaps_interval,
    validate_change_window,
)
from nautobot_maintenance_windows.tests.utils import create_schedule, create_test_device, create_window


class ScheduleEvaluatorTest(TestCase):
    """Test UTC schedule matching behavior."""

    def test_cross_midnight_schedule_matches_after_midnight(self):
        window = create_window()
        schedule = create_schedule(window, start_day_of_week=0, start_time=time(23, 0), end_day_of_week=1, end_time=time(2, 0))
        self.assertTrue(schedule_contains(schedule, datetime(2026, 7, 7, 1, 30, tzinfo=timezone.utc)))
        self.assertFalse(schedule_contains(schedule, datetime(2026, 7, 7, 2, 0, tzinfo=timezone.utc)))

    def test_multi_day_schedule_matches_middle_day(self):
        window = create_window()
        schedule = create_schedule(window, start_day_of_week=0, start_time=time(8, 0), end_day_of_week=2, end_time=time(18, 0))
        self.assertTrue(schedule_contains(schedule, datetime(2026, 7, 7, 12, 0, tzinfo=timezone.utc)))

    def test_exclusion_takes_state_when_maintenance_also_matches(self):
        device = create_test_device()
        maintenance = create_window(name="Maintenance")
        exclusion = create_window(name="Exclusion", window_type=MaintenanceWindowTypeChoices.EXCLUSION)
        create_schedule(maintenance, start_day_of_week=0, start_time=time(8, 0), end_day_of_week=0, end_time=time(12, 0))
        create_schedule(exclusion, start_day_of_week=0, start_time=time(9, 0), end_day_of_week=0, end_time=time(10, 0))
        DeviceMaintenanceWindowAssignment.objects.create(device=device, maintenance_window=maintenance)
        DeviceMaintenanceWindowAssignment.objects.create(device=device, maintenance_window=exclusion)

        result = evaluate_device(device, datetime(2026, 7, 6, 9, 30, tzinfo=timezone.utc))

        self.assertEqual(result.state, MaintenanceStateChoices.IN_EXCLUSION)
        self.assertEqual(len(result.matched_windows), 2)

    def test_exclusion_overlap_blocks_change(self):
        device = create_test_device()
        exclusion = create_window(name="Blackout", window_type=MaintenanceWindowTypeChoices.EXCLUSION)
        create_schedule(exclusion, start_day_of_week=0, start_time=time(9, 0), end_day_of_week=0, end_time=time(10, 0))
        DeviceMaintenanceWindowAssignment.objects.create(device=device, maintenance_window=exclusion)

        result = validate_change_window(
            [device],
            datetime(2026, 7, 6, 9, 30, tzinfo=timezone.utc),
            datetime(2026, 7, 6, 11, 0, tzinfo=timezone.utc),
        )

        self.assertEqual(result.result, ChangeValidationResultChoices.BLOCKED)
        self.assertEqual(len(result.blocked_by), 1)

    def test_maintenance_overlap_is_allowed_with_information(self):
        device = create_test_device()
        maintenance = create_window(name="Green")
        schedule = create_schedule(maintenance, start_day_of_week=0, start_time=time(9, 0), end_day_of_week=0, end_time=time(10, 0))
        DeviceMaintenanceWindowAssignment.objects.create(device=device, maintenance_window=maintenance)

        self.assertTrue(
            schedule_overlaps_interval(
                schedule,
                datetime(2026, 7, 6, 8, 30, tzinfo=timezone.utc),
                datetime(2026, 7, 6, 9, 30, tzinfo=timezone.utc),
            )
        )
        result = validate_change_window(
            [device],
            datetime(2026, 7, 6, 8, 30, tzinfo=timezone.utc),
            datetime(2026, 7, 6, 9, 30, tzinfo=timezone.utc),
        )
        self.assertEqual(result.result, ChangeValidationResultChoices.ALLOWED)
        self.assertEqual(len(result.maintenance_matches), 1)
        self.assertEqual(result.maintenance_matches[0].device, device)

    def test_naive_change_datetime_is_rejected(self):
        device = create_test_device()

        with self.assertRaises(ValueError):
            validate_change_window(
                [device],
                datetime(2026, 7, 6, 8, 30),
                datetime(2026, 7, 6, 9, 30, tzinfo=timezone.utc),
            )
