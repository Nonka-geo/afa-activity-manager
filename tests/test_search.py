from decimal import Decimal

from django.contrib.auth.models import Group, User
from django.test import TestCase
from django.urls import reverse

from apps.activities.models import Activity, ActivitySnapshot, SchoolYear


class ActivitySearchTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.active_year = SchoolYear.objects.create(name="2026-2027", is_active=True)
        cls.other_year = SchoolYear.objects.create(name="2027-2028", is_active=False)
        cls.viewer = User.objects.create_user(username="search-viewer", password="pass")
        cls.editor = User.objects.create_user(username="search-editor", password="pass")
        cls.viewer.groups.add(Group.objects.get(name="Viewer"))
        cls.editor.groups.add(Group.objects.get(name="Admin/Editor"))

    def create_activity(self, name, **overrides):
        data = {
            "name": name,
            "schedule": "Tuesday 15:30",
            "provider": "AFA Arts",
            "age_group": "Grades 1-3",
            "space": "Room 2",
            "price": Decimal("25.00"),
            "minimum_participants": 5,
            "maximum_participants": 10,
            "registration_count": 5,
            "school_year": self.active_year,
        }
        data.update(overrides)
        return Activity.objects.create(**data)

    def get_names(self, query=""):
        response = self.client.get(f"{reverse('activities:list')}{query}")
        return {activity.name for activity in response.context["activities"]}

    def test_viewer_and_editor_can_search_and_filter(self):
        self.create_activity("Painting", provider="Studio North")
        for user in (self.viewer, self.editor):
            with self.subTest(user=user.username):
                self.client.force_login(user)
                self.assertEqual(self.client.get(reverse("activities:list")).status_code, 200)
                self.assertEqual(self.get_names("?provider=Studio+North"), {"Painting"})

    def test_search_matches_all_supported_text_fields_case_insensitively(self):
        self.create_activity(
            "Ceramics",
            schedule="Thursday 16:00",
            provider="Studio South",
            age_group="Grades 4-6",
            space="Arts Hall",
        )
        self.client.force_login(self.viewer)

        for query in ("ceramics", "THURSDAY", "studio south", "grades 4-6", "ARTS HALL"):
            with self.subTest(query=query):
                self.assertEqual(self.get_names(f"?q={query.replace(' ', '+')}"), {"Ceramics"})

    def test_each_filter_and_combined_filters_use_and_semantics(self):
        self.create_activity("Painting", provider="Studio North")
        self.create_activity("Dance", provider="Studio South")
        self.client.force_login(self.viewer)

        self.assertEqual(self.get_names("?schedule=Tuesday+15:30"), {"Painting", "Dance"})
        self.assertEqual(self.get_names("?provider=Studio+North&space=Room+2"), {"Painting"})
        self.assertEqual(self.get_names("?age_group=Grades+1-3&provider=Studio+South"), {"Dance"})
        self.assertEqual(self.get_names("?school_year=2026-2027"), {"Painting", "Dance"})

    def test_status_filters_use_derived_status(self):
        self.create_activity("Risk", registration_count=2)
        self.create_activity("Full", registration_count=10)
        self.client.force_login(self.viewer)

        self.assertEqual(self.get_names("?status=At+Risk"), {"Risk"})
        self.assertEqual(self.get_names("?status=Full"), {"Full"})
        self.assertEqual(self.get_names("?status=Confirmed"), set())
        self.assertEqual(self.get_names("?status=Waiting+List"), set())

    def test_archived_and_other_year_activities_are_excluded(self):
        self.create_activity("Active")
        self.create_activity("Archived", is_archived=True)
        self.create_activity("Other Year", school_year=self.other_year)
        self.client.force_login(self.viewer)

        self.assertEqual(self.get_names(), {"Active"})
        self.assertEqual(self.get_names("?school_year=2027-2028"), set())

    def test_invalid_filters_return_empty_results_without_error(self):
        self.create_activity("Active")
        self.client.force_login(self.viewer)

        self.assertEqual(self.get_names("?status=Unknown"), set())
        self.assertEqual(self.get_names("?provider=Unknown"), set())
        self.assertEqual(self.get_names("?school_year=unknown"), set())

    def test_no_active_year_returns_explicit_empty_state(self):
        self.active_year.is_active = False
        self.active_year.save(update_fields=["is_active"])
        self.client.force_login(self.viewer)

        response = self.client.get(reverse("activities:list"))

        self.assertEqual(list(response.context["activities"]), [])
        self.assertContains(response, "No active activities.")

    def test_multiple_active_years_return_empty_results(self):
        SchoolYear.objects.create(name="2028-2029", is_active=True)
        self.create_activity("Ambiguous")
        self.client.force_login(self.viewer)

        response = self.client.get(reverse("activities:list"))

        self.assertEqual(list(response.context["activities"]), [])
        self.assertContains(response, "No active activities.")

    def test_search_is_read_only(self):
        self.create_activity("Read Only")
        self.client.force_login(self.viewer)
        before_activity_count = Activity.objects.count()
        before_snapshot_count = ActivitySnapshot.objects.count()

        self.client.get(f"{reverse('activities:list')}?q=read")

        self.assertEqual(Activity.objects.count(), before_activity_count)
        self.assertEqual(ActivitySnapshot.objects.count(), before_snapshot_count)