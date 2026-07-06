"""Tests for Maintenance Window jobs."""

from datetime import datetime, time, timezone

from nautobot.apps.testing import TransactionTestCase, create_job_result_and_run_job
from nautobot.extras.choices import JobResultStatusChoices

from nautobot_maintenance_windows.choices import MaintenanceWindowTypeChoices
from nautobot_maintenance_windows.jobs import jobs as jobs_module
from nautobot_maintenance_windows.models import DeviceMaintenanceWindowAssignment
from nautobot_maintenance_windows.tests.utils import (
    create_schedule,
    create_test_device,
    create_window,
    get_test_job_model,
)

JOB_MODULE = "nautobot_maintenance_windows.jobs.jobs"


class MaintenanceWindowJobsTest(TransactionTestCase):
    """Test plugin-provided Nautobot jobs."""

    databases = ("default", "job_logs")

    user_permissions = (
        "dcim.view_device",
        "nautobot_maintenance_windows.view_maintenancewindow",
        "nautobot_maintenance_windows.view_maintenancewindowschedule",
        "nautobot_maintenance_windows.add_devicemaintenancewindowassignment",
        "nautobot_maintenance_windows.delete_devicemaintenancewindowassignment",
    )

    def setUp(self):
        """Create job models and test records."""
        super().setUp()
        for job_class in jobs_module.jobs:
            get_test_job_model(job_class)
        self.device = create_test_device(name="job-device")
        self.exclusion = create_window(name="Job Exclusion", window_type=MaintenanceWindowTypeChoices.EXCLUSION)
        create_schedule(self.exclusion, start_day_of_week=0, start_time=time(9, 0), end_day_of_week=0, end_time=time(10, 0))

    def test_change_validation_job_blocks_on_exclusion(self):
        DeviceMaintenanceWindowAssignment.objects.create(device=self.device, maintenance_window=self.exclusion)

        job_result = create_job_result_and_run_job(
            JOB_MODULE,
            "ChangeValidationJob",
            username=self.user.username,
            devices=[self.device.pk],
            proposed_start=datetime(2026, 7, 6, 9, 15, tzinfo=timezone.utc).isoformat(),
            proposed_end=datetime(2026, 7, 6, 9, 45, tzinfo=timezone.utc).isoformat(),
        )

        self.assertJobResultStatus(job_result)
        log_messages = list(job_result.job_log_entries.values_list("message", flat=True))
        self.assertTrue(any("result=BLOCKED" in message for message in log_messages))

    def test_bulk_assignment_job_assigns_window(self):
        job_result = create_job_result_and_run_job(
            JOB_MODULE,
            "BulkMaintenanceWindowAssignmentJob",
            username=self.user.username,
            devices=[self.device.pk],
            maintenance_windows=[self.exclusion.pk],
            assign=True,
        )

        self.assertJobResultStatus(job_result)
        self.assertTrue(
            DeviceMaintenanceWindowAssignment.objects.filter(
                device=self.device,
                maintenance_window=self.exclusion,
            ).exists()
        )

    def test_audit_coverage_job_runs_successfully(self):
        job_result = create_job_result_and_run_job(
            JOB_MODULE,
            "AuditMaintenanceWindowCoverageJob",
            username=self.user.username,
        )

        self.assertJobResultStatus(job_result)
        log_messages = list(job_result.job_log_entries.values_list("message", flat=True))
        self.assertTrue(any("Coverage summary" in message for message in log_messages))


class MaintenanceWindowJobPermissionTest(TransactionTestCase):
    """Test security-sensitive job permission failures."""

    databases = ("default", "job_logs")

    user_permissions = (
        "dcim.view_device",
        "nautobot_maintenance_windows.view_maintenancewindow",
    )

    def setUp(self):
        """Create job models and test records."""
        super().setUp()
        for job_class in jobs_module.jobs:
            get_test_job_model(job_class)
        self.device = create_test_device(name="restricted-job-device")
        self.exclusion = create_window(name="Restricted Job Exclusion", window_type=MaintenanceWindowTypeChoices.EXCLUSION)
        create_schedule(self.exclusion, start_day_of_week=0, start_time=time(9, 0), end_day_of_week=0, end_time=time(10, 0))

    def test_device_eligibility_job_rejects_without_schedule_permission(self):
        job_result = create_job_result_and_run_job(
            JOB_MODULE,
            "DeviceMaintenanceEligibilityJob",
            username=self.user.username,
            devices=[self.device.pk],
        )

        self.assertJobResultStatus(job_result, JobResultStatusChoices.STATUS_FAILURE)

    def test_change_validation_job_rejects_without_schedule_permission(self):
        job_result = create_job_result_and_run_job(
            JOB_MODULE,
            "ChangeValidationJob",
            username=self.user.username,
            devices=[self.device.pk],
            proposed_start=datetime(2026, 7, 6, 9, 15, tzinfo=timezone.utc).isoformat(),
            proposed_end=datetime(2026, 7, 6, 9, 45, tzinfo=timezone.utc).isoformat(),
        )

        self.assertJobResultStatus(job_result, JobResultStatusChoices.STATUS_FAILURE)

    def test_bulk_assignment_job_rejects_without_assign_permission(self):
        job_result = create_job_result_and_run_job(
            JOB_MODULE,
            "BulkMaintenanceWindowAssignmentJob",
            username=self.user.username,
            devices=[self.device.pk],
            maintenance_windows=[self.exclusion.pk],
            assign=True,
        )

        self.assertJobResultStatus(job_result, JobResultStatusChoices.STATUS_FAILURE)

    def test_bulk_assignment_job_rejects_without_unassign_permission(self):
        job_result = create_job_result_and_run_job(
            JOB_MODULE,
            "BulkMaintenanceWindowAssignmentJob",
            username=self.user.username,
            devices=[self.device.pk],
            maintenance_windows=[self.exclusion.pk],
            assign=False,
        )

        self.assertJobResultStatus(job_result, JobResultStatusChoices.STATUS_FAILURE)
