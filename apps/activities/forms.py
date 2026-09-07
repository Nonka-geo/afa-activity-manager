from django import forms

from .models import Activity


class ActivityForm(forms.ModelForm):
    class Meta:
        model = Activity
        fields = [
            "name",
            "schedule",
            "provider",
            "age_group",
            "space",
            "price",
            "minimum_participants",
            "maximum_participants",
            "registration_count",
            "school_year",
            "notes",
        ]


class RegistrationUpdateForm(forms.ModelForm):
    class Meta:
        model = Activity
        fields = [
            "registration_count",
            "minimum_participants",
            "maximum_participants",
        ]