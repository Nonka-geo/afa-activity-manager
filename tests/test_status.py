from decimal import Decimal

from django.test import TestCase

from apps.activities.models import Activity, SchoolYear
from apps.activities.status import ActivityStatus, calculate_status


class ActivityStatusTests(TestCase):
    def test_status_boundaries(self):
        cases = (
            (4, 5, 10, ActivityStatus.AT_RISK),
            (5, 5, 10, ActivityStatus.CONFIRMED),
            (7, 5, 10, ActivityStatus.CONFIRMED),
            (10, 5, 10, ActivityStatus.FULL),
            (11, 5, 10, ActivityStatus.WAITING_LIST),
        )

        for registration_count, minimum, maximum, expected in cases:
            with self.subTest(registration_count=registration_count):
                self.assertEqual(
                    calculate_status(registration_count, minimum, maximum),
                    expected,
                )

    def test_equal_thresholds(self):
        self.assertEqual(calculate_status(4, 5, 5), ActivityStatus.AT_RISK)
        self.assertEqual(calculate_status(5, 5, 5), ActivityStatus.FULL)
        self.assertEqual(calculate_status(6, 5, 5), ActivityStatus.WAITING_LIST)

    def test_invalid_status_inputs_raise(self):
        invalid_cases = (
            (-1, 1, 2),
            (1, -1, 2),
            (1, 1, -1),
            (1, 3, 2),
        )

        for values in invalid_cases:
            with self.subTest(values=values):
                with self.assertRaises(ValueError):
                    calculate_status(*values)

    def test_activity_status_is_derived_from_current_values(self):
        school_year = SchoolYear.objects.create(name="2027-2028")
        activity = Activity.objects.create(
            name="Art Club",
            schedule="Tuesday 15:30",
            provider="AFA Arts",
            age_group="Grades 1-3",
            space="Room 2",
            price=Decimal("25.00"),
            minimum_participants=5,
            maximum_participants=10,
            registration_count=4,
            school_year=school_year,
        )

        self.assertEqual(activity.status, ActivityStatus.AT_RISK)
        activity.registration_count = 10
        self.assertEqual(activity.status, ActivityStatus.FULL)
        activity.registration_count = 5
        activity.minimum_participants = 6
        self.assertEqual(activity.status, ActivityStatus.AT_RISK)

    def test_status_is_not_an_editable_model_field(self):
        field_names = {field.name for field in Activity._meta.get_fields()}

        self.assertNotIn("status", field_names)

    def test_activity_views_render_derived_status(self):
        school_year = SchoolYear.objects.create(name="2028-2029", is_active=True)
        activity = Activity.objects.create(
            name="Science Club",
            schedule="Wednesday 15:30",
            provider="AFA Science",
            age_group="Grades 4-6",
            space="Room 3",
            price=Decimal("30.00"),
            minimum_participants=5,
            maximum_participants=10,
            registration_count=5,
            school_year=school_year,
        )

        from django.contrib.auth.models import Group, User

        viewer = User.objects.create_user(username="status-viewer", password="pass")
        viewer.groups.add(Group.objects.get(name="Viewer"))
        self.client.force_login(viewer)

        list_response = self.client.get("/activities/")
        detail_response = self.client.get(f"/activities/{activity.pk}/")

        self.assertContains(list_response, "Confirmed")
        self.assertContains(detail_response, "Confirmed")