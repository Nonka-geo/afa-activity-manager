from decimal import Decimal

from django.contrib.auth.models import Group, User
from django.test import TestCase
from django.urls import reverse

from apps.activities.models import Activity, ActivitySnapshot, SchoolYear


class DashboardTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.active_year = SchoolYear.objects.create(name="2026-2027", is_active=True)
        cls.other_year = SchoolYear.objects.create(name="2027-2028", is_active=False)
        cls.viewer = User.objects.create_user(username="dashboard-viewer", password="pass")
        cls.editor = User.objects.create_user(username="dashboard-editor", password="pass")
        cls.viewer.groups.add(Group.objects.get(name="Viewer"))
        cls.editor.groups.add(Group.objects.get(name="Admin/Editor"))

    def create_activity(self, name, registrations, **overrides):
        data = {
            "name": name,
            "schedule": "Tuesday 15:30",
            "provider": "AFA Arts",
            "age_group": "Grades 1-3",
            "space": "Room 2",
            "price": Decimal("25.00"),
            "minimum_participants": 5,
            "maximum_participants": 10,
            "registration_count": registrations,
            "school_year": self.active_year,
        }
        data.update(overrides)
        return Activity.objects.create(**data)

    def test_viewer_and_editor_can_access_dashboard(self):
        for user in (self.viewer, self.editor):
            with self.subTest(user=user.username):
                self.client.force_login(user)
                self.assertEqual(self.client.get(reverse("activities:dashboard")).status_code, 200)

    def test_anonymous_user_is_redirected(self):
        response = self.client.get(reverse("activities:dashboard"))

        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse("accounts:login"), response["Location"])

    def test_dashboard_scopes_to_active_year_and_non_archived_activities(self):
        included = self.create_activity("Included", 5)
        self.create_activity("Archived", 5, is_archived=True)
        self.create_activity("Other year", 5, school_year=self.other_year)
        self.client.force_login(self.viewer)

        response = self.client.get(reverse("activities:dashboard"))

        self.assertEqual(response.context["total_activities"], 1)
        self.assertEqual(list(response.context["activities"]), [included])
        self.assertNotContains(response, "Archived")
        self.assertNotContains(response, "Other year")

    def test_dashboard_counts_all_statuses_and_attention(self):
        self.create_activity("At Risk Club", 4)
        self.create_activity("Confirmed Club", 5)
        self.create_activity("Full Club", 10)
        self.create_activity("Waiting Club", 11)
        self.client.force_login(self.viewer)

        response = self.client.get(reverse("activities:dashboard"))

        self.assertEqual(response.context["total_activities"], 4)
        self.assertEqual(response.context["at_risk_count"], 1)
        self.assertEqual(response.context["confirmed_count"], 1)
        self.assertEqual(response.context["full_count"], 1)
        self.assertEqual(response.context["waiting_list_count"], 1)
        self.assertContains(response, "At Risk Club")

    def test_no_active_school_year_has_empty_state_and_zero_counts(self):
        self.active_year.is_active = False
        self.active_year.save(update_fields=["is_active"])
        self.create_activity("Unscoped", 5)
        self.client.force_login(self.viewer)

        response = self.client.get(reverse("activities:dashboard"))

        self.assertIsNone(response.context["active_school_year"])
        self.assertEqual(response.context["total_activities"], 0)
        self.assertEqual(response.context["at_risk_count"], 0)
        self.assertEqual(response.context["confirmed_count"], 0)
        self.assertEqual(response.context["full_count"], 0)
        self.assertEqual(response.context["waiting_list_count"], 0)
        self.assertContains(response, "No active school year is configured.")

    def test_multiple_active_school_years_have_empty_state_and_zero_counts(self):
        SchoolYear.objects.create(name="2028-2029", is_active=True)
        self.create_activity("Ambiguous", 5)
        self.client.force_login(self.viewer)

        response = self.client.get(reverse("activities:dashboard"))

        self.assertIsNone(response.context["active_school_year"])
        self.assertEqual(response.context["total_activities"], 0)
        self.assertContains(response, "No active school year is configured.")

    def test_dashboard_is_read_only(self):
        self.create_activity("Read Only", 5)
        self.client.force_login(self.viewer)
        before_activity_count = Activity.objects.count()
        before_snapshot_count = ActivitySnapshot.objects.count()

        response = self.client.get(reverse("activities:dashboard"))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(Activity.objects.count(), before_activity_count)
        self.assertEqual(ActivitySnapshot.objects.count(), before_snapshot_count)
