"""Forms for nautobot_maintenance_windows."""

from django import forms
from nautobot.apps.forms import (
    BootstrapMixin,
    DynamicModelChoiceField,
    NautobotBulkEditForm,
    NautobotFilterForm,
    NautobotModelForm,
)
from nautobot.core.forms import BulkEditForm
from nautobot.dcim.models import Device

from nautobot_maintenance_windows import models
from nautobot_maintenance_windows.choices import DAY_OF_WEEK_CHOICES, MaintenanceWindowTypeChoices


class MaintenanceWindowForm(NautobotModelForm):
    """MaintenanceWindow create/edit form."""

    class Meta:
        """Meta attributes."""

        model = models.MaintenanceWindow
        fields = ["name", "description", "is_active", "window_type"]


class MaintenanceWindowBulkEditForm(NautobotBulkEditForm):
    """MaintenanceWindow bulk edit form."""

    pk = forms.ModelMultipleChoiceField(queryset=models.MaintenanceWindow.objects.all(), widget=forms.MultipleHiddenInput)
    description = forms.CharField(required=False, widget=forms.Textarea(attrs={"rows": 3}))
    is_active = forms.NullBooleanField(required=False)
    window_type = forms.ChoiceField(required=False, choices=MaintenanceWindowTypeChoices.choices)

    class Meta:
        """Meta attributes."""

        nullable_fields = ["description"]


class MaintenanceWindowFilterForm(NautobotFilterForm):
    """Filter form for MaintenanceWindow list views."""

    model = models.MaintenanceWindow
    field_order = ["q", "name", "window_type", "is_active", "device"]

    q = forms.CharField(required=False, label="Search")
    name = forms.CharField(required=False)
    window_type = forms.ChoiceField(required=False, choices=(("", "---------"),) + tuple(MaintenanceWindowTypeChoices.choices))
    is_active = forms.NullBooleanField(required=False, label="Active")
    device = DynamicModelChoiceField(queryset=Device.objects.all(), required=False)


class MaintenanceWindowScheduleForm(forms.ModelForm):
    """MaintenanceWindowSchedule create/edit form."""

    maintenance_window = DynamicModelChoiceField(queryset=models.MaintenanceWindow.objects.all())

    class Meta:
        """Meta attributes."""

        model = models.MaintenanceWindowSchedule
        fields = ["maintenance_window", "start_day_of_week", "start_time", "end_day_of_week", "end_time"]


class MaintenanceWindowScheduleBulkEditForm(BootstrapMixin, BulkEditForm):
    """MaintenanceWindowSchedule bulk edit form."""

    pk = forms.ModelMultipleChoiceField(
        queryset=models.MaintenanceWindowSchedule.objects.all(),
        widget=forms.MultipleHiddenInput,
    )
    start_day_of_week = forms.ChoiceField(required=False, choices=DAY_OF_WEEK_CHOICES)
    start_time = forms.TimeField(required=False)
    end_day_of_week = forms.ChoiceField(required=False, choices=DAY_OF_WEEK_CHOICES)
    end_time = forms.TimeField(required=False)


class MaintenanceWindowScheduleFilterForm(NautobotFilterForm):
    """Filter form for MaintenanceWindowSchedule list views."""

    model = models.MaintenanceWindowSchedule
    field_order = ["maintenance_window", "start_day_of_week", "end_day_of_week"]

    maintenance_window = DynamicModelChoiceField(queryset=models.MaintenanceWindow.objects.all(), required=False)
    start_day_of_week = forms.ChoiceField(required=False, choices=(("", "---------"),) + tuple(DAY_OF_WEEK_CHOICES))
    end_day_of_week = forms.ChoiceField(required=False, choices=(("", "---------"),) + tuple(DAY_OF_WEEK_CHOICES))


class DeviceMaintenanceWindowAssignmentForm(forms.ModelForm):
    """DeviceMaintenanceWindowAssignment create/edit form."""

    device = DynamicModelChoiceField(queryset=Device.objects.all())
    maintenance_window = DynamicModelChoiceField(queryset=models.MaintenanceWindow.objects.filter(is_active=True))

    class Meta:
        """Meta attributes."""

        model = models.DeviceMaintenanceWindowAssignment
        fields = ["device", "maintenance_window"]


class DeviceMaintenanceWindowAssignmentBulkEditForm(BootstrapMixin, BulkEditForm):
    """Bulk edit DeviceMaintenanceWindowAssignment records."""

    pk = forms.ModelMultipleChoiceField(
        queryset=models.DeviceMaintenanceWindowAssignment.objects.all(),
        widget=forms.MultipleHiddenInput,
    )
    maintenance_window = DynamicModelChoiceField(
        queryset=models.MaintenanceWindow.objects.filter(is_active=True),
        required=False,
    )


class DeviceMaintenanceWindowAssignmentFilterForm(NautobotFilterForm):
    """Filter form for DeviceMaintenanceWindowAssignment list views."""

    model = models.DeviceMaintenanceWindowAssignment
    field_order = ["device", "maintenance_window"]

    device = DynamicModelChoiceField(queryset=Device.objects.all(), required=False)
    maintenance_window = DynamicModelChoiceField(queryset=models.MaintenanceWindow.objects.all(), required=False)
