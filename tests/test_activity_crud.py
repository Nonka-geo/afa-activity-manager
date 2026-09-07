from decimal import Decimal

from django.contrib.auth.models import Group, Permission, User
from django.test import TestCase
from django.urls import reverse

from apps.activities.models import Activity, SchoolYear


class ActivityCrudTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.school_year = SchoolYear.objects.create(name="2026-2027")
        cls.active_activity = Activity.objects.create(
            name="Art Club",
            schedule="Tuesday 15:30",
            provider="AFA Arts",
            age_group="Grades 1-3",
            space="Room 2",
            price=Decimal("25.00"),
            minimum_participants=5,
            maximum_participants=15,
            school_year=cls.school_year,
        )
        cls.archived_activity = Activity.objects.create(
            name="Archived Club",
            schedule="Wednesday 15:30",
            provider="AFA Arts",
            age_group="Grades 4-6",
            space="Room 3",
            price=Decimal("30.00"),
            minimum_participants=4,
            maximum_participants=12,
            school_year=cls.school_year,
            is_archived=True,
        )
        cls.editor = User.objects.create_user(username="editor", password="editor-pass")
        cls.viewer = User.objects.create_user(username="viewer", password="viewer-pass")
        cls.editor.groups.add(Group.objects.get(name="Admin/Editor"))
        cls.viewer.groups.add(Group.objects.get(name="Viewer"))

    def test_editor_can_read_active_and_archived_lists(self):
        self.client.force_login(self.editor)

        active_response = self.client.get(reverse("activities:list"))
        archived_response = self.client.get(reverse("activities:archived_list"))

        self.assertContains(active_response, "Art Club")
        self.assertNotContains(active_response, "Archived Club")
        self.assertContains(archived_response, "Archived Club")

    def test_viewer_can_read_lists_and_detail(self):
        self.client.force_login(self.viewer)

        self.assertEqual(self.client.get(reverse("activities:list")).status_code, 200)
        self.assertEqual(
            self.client.get(reverse("activities:archived_list")).status_code,
            200,
        )
        self.assertEqual(
            self.client.get(
                reverse("activities:detail", args=[self.archived_activity.pk])
            ).status_code,
            200,
        )

    def test_editor_can_create_activity(self):
        self.client.force_login(self.editor)

        response = self.client.post(
            reverse("activities:create"),
            {
                "name": "New Club",
                "schedule": "Thursday 15:30",
                "provider": "AFA Arts",
                "age_group": "Grades 1-3",
                "space": "Room 4",
                "price": "20.00",
                "minimum_participants": 3,
                "maximum_participants": 10,
                "registration_count": 0,
                "school_year": self.school_year.pk,
                "notes": "Synthetic test activity",
            },
        )

        created = Activity.objects.get(name="New Club")
        self.assertRedirects(response, reverse("activities:detail", args=[created.pk]))

    def test_editor_can_edit_without_changing_group_code(self):
        self.client.force_login(self.editor)
        original_code = self.active_activity.group_code

        response = self.client.post(
            reverse("activities:edit", args=[self.active_activity.pk]),
            {
                "name": "Updated Art Club",
                "schedule": "Friday 15:30",
                "provider": "Updated Provider",
                "age_group": "Grades 2-4",
                "space": "Room 5",
                "price": "35.00",
                "minimum_participants": 6,
                "maximum_participants": 16,
                "registration_count": 2,
                "school_year": self.school_year.pk,
                "notes": "Updated notes",
            },
        )

        self.assertRedirects(
            response,
            reverse("activities:detail", args=[self.active_activity.pk]),
        )
        self.active_activity.refresh_from_db()
        self.assertEqual(self.active_activity.group_code, original_code)
        self.assertEqual(self.active_activity.name, "Updated Art Club")

    def test_editor_can_archive_without_deleting(self):
        self.client.force_login(self.editor)

        response = self.client.post(
            reverse("activities:archive", args=[self.active_activity.pk])
        )

        self.assertRedirects(response, reverse("activities:archived_list"))
        self.active_activity.refresh_from_db()
        self.assertTrue(self.active_activity.is_archived)
        self.assertTrue(Activity.objects.filter(pk=self.active_activity.pk).exists())

    def test_viewer_cannot_write(self):
        self.client.force_login(self.viewer)

        for url in (
            reverse("activities:create"),
            reverse("activities:edit", args=[self.active_activity.pk]),
            reverse("activities:archive", args=[self.active_activity.pk]),
        ):
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertEqual(response.status_code, 403)

    def test_anonymous_users_are_redirected_from_activity_routes(self):
        urls = (
            reverse("activities:list"),
            reverse("activities:archived_list"),
            reverse("activities:detail", args=[self.active_activity.pk]),
            reverse("activities:create"),
            reverse("activities:edit", args=[self.active_activity.pk]),
            reverse("activities:archive", args=[self.active_activity.pk]),
        )

        for url in urls:
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertEqual(response.status_code, 302)
                self.assertIn(reverse("accounts:login"), response["Location"])

    def test_activity_permissions_are_assigned_to_expected_groups(self):
        editor = Group.objects.get(name="Admin/Editor")
        viewer = Group.objects.get(name="Viewer")

        self.assertTrue(editor.permissions.filter(codename="add_activity").exists())
        self.assertTrue(editor.permissions.filter(codename="change_activity").exists())
        self.assertTrue(editor.permissions.filter(codename="view_activity").exists())
        self.assertTrue(viewer.permissions.filter(codename="view_activity").exists())
        self.assertFalse(viewer.permissions.filter(codename="add_activity").exists())
        self.assertFalse(viewer.permissions.filter(codename="change_activity").exists())

    def test_invalid_activity_input_is_rejected(self):
        self.client.force_login(self.editor)

        response = self.client.post(
            reverse("activities:create"),
            {
                "name": "Invalid Club",
                "schedule": "Thursday 15:30",
                "provider": "AFA Arts",
                "age_group": "Grades 1-3",
                "space": "Room 4",
                "price": "20.00",
                "minimum_participants": 11,
                "maximum_participants": 10,
                "registration_count": 0,
                "school_year": self.school_year.pk,
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Maximum participants must be greater than or equal to minimum participants.")