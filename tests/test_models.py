from decimal import Decimal

from django.core.exceptions import ValidationError
from django.db import models
from django.test import TestCase

from apps.activities.models import Activity, SchoolYear


class ActivityModelTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.school_year = SchoolYear.objects.create(name="2026-2027", is_active=True)

    def activity_data(self, **overrides):
        data = {
            "name": "Art Club",
            "schedule": "Tuesday 15:30",
            "provider": "AFA Arts",
            "age_group": "Grades 1-3",
            "space": "Room 2",
            "price": Decimal("25.00"),
            "minimum_participants": 5,
            "maximum_participants": 15,
            "school_year": self.school_year,
        }
        data.update(overrides)
        return data

    def test_school_year_name_is_unique(self):
        with self.assertRaises(ValidationError):
            duplicate = SchoolYear(name="2026-2027")
            duplicate.full_clean()

    def test_activity_has_required_fields_and_registration_default(self):
        activity = Activity.objects.create(**self.activity_data())

        self.assertEqual(activity.registration_count, 0)
        self.assertFalse(activity.is_archived)
        self.assertEqual(activity.school_year, self.school_year)

    def test_school_year_can_have_multiple_activities(self):
        Activity.objects.create(**self.activity_data(name="Art Club A"))
        Activity.objects.create(**self.activity_data(name="Art Club B"))

        self.assertEqual(self.school_year.activities.count(), 2)

    def test_group_code_is_generated_and_unique(self):
        first = Activity.objects.create(**self.activity_data(name="First"))
        second = Activity.objects.create(**self.activity_data(name="Second"))

        self.assertIsNotNone(first.group_code)
        self.assertNotEqual(first.group_code, second.group_code)

    def test_group_code_does_not_change_when_activity_is_updated(self):
        activity = Activity.objects.create(**self.activity_data())
        original_code = activity.group_code

        activity.name = "Updated Art Club"
        activity.registration_count = 8
        activity.is_archived = True
        activity.save()
        activity.refresh_from_db()

        self.assertEqual(activity.group_code, original_code)

    def test_archived_state_persists(self):
        activity = Activity.objects.create(**self.activity_data(is_archived=True))

        self.assertTrue(activity.is_archived)

    def test_negative_values_are_rejected(self):
        invalid_values = (
            {"price": Decimal("-1.00")},
            {"minimum_participants": -1},
            {"maximum_participants": -1},
            {"registration_count": -1},
        )

        for invalid_value in invalid_values:
            with self.subTest(invalid_value=invalid_value):
                activity = Activity(**self.activity_data(**invalid_value))
                with self.assertRaises(ValidationError):
                    activity.full_clean()

    def test_minimum_cannot_exceed_maximum(self):
        activity = Activity(**self.activity_data(minimum_participants=16))

        with self.assertRaises(ValidationError):
            activity.full_clean()

    def test_school_year_is_required(self):
        activity = Activity(**self.activity_data(school_year=None))

        with self.assertRaises(ValidationError):
            activity.full_clean()

    def test_activity_has_no_child_or_family_relationship(self):
        relation_names = {
            field.name
            for field in Activity._meta.get_fields()
            if isinstance(field, (models.ForeignKey, models.OneToOneField, models.ManyToManyField))
        }

        self.assertEqual(relation_names, {"school_year"})