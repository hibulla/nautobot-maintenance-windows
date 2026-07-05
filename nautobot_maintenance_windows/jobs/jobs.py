"""Nautobot jobs for Maintenance Window evaluation and assignment."""

from django.db import IntegrityError, transaction
from django.utils.dateparse import parse_datetime
from nautobot.apps.jobs import register_jobs
from nautobot.dcim.models import Device
from nautobot.extras.jobs import BooleanVar, Job, MultiObjectVar, StringVar

from nautobot_maintenance_windows import models
from nautobot_maintenance_windows.services.evaluator import (
    evaluate_devices,
    require_utc_datetime,
    validate_change_window,
)


class DeviceMaintenanceEligibilityJob(Job):
    """Report current maintenance/exclusion state for selected devices."""

    devices = MultiObjectVar(model=Device, description="Devices to evaluate.")

    class Meta:
        """Meta attributes."""

        name = "Device Maintenance Eligibility"
        description = "Evaluate current UTC maintenance state for selected devices."
        has_sensitive_variables = False

    def run(self, *, devices):
        """Evaluate selected devices."""
        evaluations = evaluate_devices(devices)
        results = []
        for evaluation in evaluations:
            matched = [_match_to_dict(match) for match in evaluation.matched_windows]
            self.logger.info(
                "device=%s state=%s evaluated_at=%s matched_windows=%s",
                evaluation.device,
                evaluation.state,
                evaluation.evaluated_at.isoformat(),
                len(matched),
            )
            results.append(
                {
                    "device": str(evaluation.device),
                    "state": evaluation.state,
                    "matched_windows": matched,
                    "evaluated_at": evaluation.evaluated_at.isoformat(),
                }
            )
        return {"devices": results}


class ChangeValidationJob(Job):
    """Validate a proposed change interval against device exclusion windows."""

    devices = MultiObjectVar(model=Device, description="Devices included in the proposed change.")
    proposed_start = StringVar(description="Proposed change start in UTC, ISO-8601 format.")
    proposed_end = StringVar(description="Proposed change end in UTC, ISO-8601 format.")

    class Meta:
        """Meta attributes."""

        name = "Change Validation"
        description = "Return BLOCKED if any assigned exclusion window overlaps a proposed UTC change interval."
        has_sensitive_variables = False

    def run(self, *, devices, proposed_start, proposed_end):
        """Validate the proposed change interval."""
        try:
            start = _parse_utc_datetime(proposed_start, "proposed_start")
            end = _parse_utc_datetime(proposed_end, "proposed_end")
            validation = validate_change_window(devices, start, end)
        except (TypeError, ValueError) as exc:
            self.logger.error(str(exc))
            raise

        self.logger.info(
            "result=%s proposed_start=%s proposed_end=%s exclusion_matches=%s maintenance_matches=%s",
            validation.result,
            validation.evaluated_start.isoformat(),
            validation.evaluated_end.isoformat(),
            len(validation.blocked_by),
            len(validation.maintenance_matches),
        )
        for match in validation.blocked_by:
            self.logger.warning(
                "blocked_device=%s blocked_by=%s schedule=%s",
                match.device,
                match.window,
                match.schedule,
            )
        for match in validation.maintenance_matches:
            self.logger.info(
                "maintenance_device=%s maintenance_overlap=%s schedule=%s",
                match.device,
                match.window,
                match.schedule,
            )

        return {
            "result": validation.result,
            "proposed_start": validation.evaluated_start.isoformat(),
            "proposed_end": validation.evaluated_end.isoformat(),
            "blocked_by": [_match_to_dict(match) for match in validation.blocked_by],
            "maintenance_matches": [_match_to_dict(match) for match in validation.maintenance_matches],
        }


class BulkMaintenanceWindowAssignmentJob(Job):
    """Assign or unassign maintenance windows from devices in bulk."""

    devices = MultiObjectVar(model=Device, description="Devices to update.")
    maintenance_windows = MultiObjectVar(
        model=models.MaintenanceWindow,
        description="Maintenance windows to assign or unassign.",
    )
    assign = BooleanVar(description="Assign when true; unassign when false.", default=True)

    class Meta:
        """Meta attributes."""

        name = "Bulk Maintenance Window Assignment"
        description = "Assign or unassign maintenance windows to devices in bulk."
        has_sensitive_variables = False

    def run(self, *, devices, maintenance_windows, assign):
        """Bulk assign or unassign selected windows."""
        created = 0
        removed = 0
        unchanged = 0
        errors = []

        for device in devices:
            for window in maintenance_windows:
                try:
                    with transaction.atomic():
                        if assign:
                            _assignment, was_created = models.DeviceMaintenanceWindowAssignment.objects.get_or_create(
                                device=device,
                                maintenance_window=window,
                            )
                            if was_created:
                                created += 1
                                self.logger.info("assigned device=%s maintenance_window=%s", device, window)
                            else:
                                unchanged += 1
                        else:
                            deleted, _ = models.DeviceMaintenanceWindowAssignment.objects.filter(
                                device=device,
                                maintenance_window=window,
                            ).delete()
                            if deleted:
                                removed += deleted
                                self.logger.info("unassigned device=%s maintenance_window=%s", device, window)
                            else:
                                unchanged += 1
                except IntegrityError as exc:
                    message = f"device={device} maintenance_window={window}: {exc}"
                    errors.append(message)
                    self.logger.error(message)

        summary = {"created": created, "removed": removed, "unchanged": unchanged, "errors": errors}
        if errors:
            self.logger.warning("Bulk assignment completed with errors: %s", summary)
        else:
            self.logger.info("Bulk assignment complete: %s", summary)
        return summary


def _match_to_dict(match):
    schedule = match.schedule
    data = {
        "maintenance_window": str(match.window),
        "window_type": match.window.window_type,
        "schedule": {
            "start_day_of_week": schedule.start_day_of_week,
            "start_time": schedule.start_time.isoformat(),
            "end_day_of_week": schedule.end_day_of_week,
            "end_time": schedule.end_time.isoformat(),
            "timezone": schedule.timezone,
        },
    }
    if match.device is not None:
        data["device"] = str(match.device)
    return data


def _parse_utc_datetime(value, field_name):
    parsed = parse_datetime(value) if isinstance(value, str) else value
    if parsed is None:
        raise ValueError(f"{field_name} must be a valid ISO-8601 datetime.")
    return require_utc_datetime(parsed, field_name)


jobs = [DeviceMaintenanceEligibilityJob, ChangeValidationJob, BulkMaintenanceWindowAssignmentJob]
register_jobs(*jobs)
