from decimal import Decimal
from unittest.mock import patch

from django.contrib.auth.models import Group, User
from django.test import TestCase
from django.urls import reverse

from apps.activities.models import Activity, ActivitySnapshot, SchoolYear
from apps.activities.status import ActivityStatus


class RegistrationUpdateTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.school_year = SchoolYear.objects.create(name="2026-2027")
        cls.activity = Activity.objects.create(
            name="Art Club",
            schedule="Tuesday 15:30",
            provider="AFA Arts",
            age_group="Grades 1-3",
            space="Room 2",
            price=Decimal("25.00"),
            minimum_participants=5,
            maximum_participants=10,
            registration_count=4,
            school_year=cls.school_year,
        )
        cls.editor = User.objects.create_user(username="registration-editor", password="pass")
        cls.viewer = User.objects.create_user(username="registration-viewer", password="pass")
        cls.editor.groups.add(Group.objects.get(name="Admin/Editor"))
        cls.viewer.groups.add(Group.objects.get(name="Viewer"))

    def update_payload(self, **overrides):
        payload = {
            "registration_count": 5,
            "minimum_participants": 5,
            "maximum_participants": 10,
        }
        payload.update(overrides)
        return payload

    def test_editor_update_recalculates_status_and_creates_snapshot(self):
        self.client.force_login(self.editor)

        response = self.client.post(
            reverse("activities:registrations", args=[self.activity.pk]),
            self.update_payload(),
        )

        self.assertRedirects(response, reverse("activities:detail", args=[self.activity.pk]))
        self.activity.refresh_from_db()
        snapshot = ActivitySnapshot.objects.get()
        self.assertEqual(self.activity.registration_count, 5)
        self.assertEqual(self.activity.status, ActivityStatus.CONFIRMED)
        self.assertEqual(snapshot.activity, self.activity)
        self.assertEqual(snapshot.registration_count, 5)
        self.assertEqual(snapshot.status, ActivityStatus.CONFIRMED)
        self.assertEqual(snapshot.actor, self.editor)
        self.assertIsNotNone(snapshot.created_at)

    def test_viewer_cannot_update_registrations(self):
        self.client.force_login(self.viewer)

        response = self.client.post(
            reverse("activities:registrations", args=[self.activity.pk]),
            self.update_payload(registration_count=9),
        )

        self.assertEqual(response.status_code, 403)
        self.assertEqual(ActivitySnapshot.objects.count(), 0)

    def test_anonymous_user_is_redirected_from_registration_update(self):
        response = self.client.get(
            reverse("activities:registrations", args=[self.activity.pk])
        )

        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse("accounts:login"), response["Location"])

    def test_unchanged_update_does_not_create_snapshot(self):
        self.client.force_login(self.editor)

        response = self.client.post(
            reverse("activities:registrations", args=[self.activity.pk]),
            self.update_payload(registration_count=4),
        )

        self.assertRedirects(response, reverse("activities:detail", args=[self.activity.pk]))
        self.assertEqual(ActivitySnapshot.objects.count(), 0)

    def test_threshold_change_creates_snapshot_with_resulting_status(self):
        self.client.force_login(self.editor)

        self.client.post(
            reverse("activities:registrations", args=[self.activity.pk]),
            self.update_payload(registration_count=4, minimum_participants=4),
        )

        snapshot = ActivitySnapshot.objects.get()
        self.assertEqual(snapshot.status, ActivityStatus.CONFIRMED)

    def test_archived_activity_retains_snapshots(self):
        self.client.force_login(self.editor)
        self.client.post(
            reverse("activities:registrations", args=[self.activity.pk]),
            self.update_payload(),
        )
        self.activity.is_archived = True
        self.activity.save(update_fields=["is_archived"])

        self.assertEqual(self.activity.snapshots.count(), 1)

    def test_invalid_registration_count_is_rejected_without_writes(self):
        self.client.force_login(self.editor)

        response = self.client.post(
            reverse("activities:registrations", args=[self.activity.pk]),
            self.update_payload(registration_count=-1),
        )

        self.assertEqual(response.status_code, 200)
        self.activity.refresh_from_db()
        self.assertEqual(self.activity.registration_count, 4)
        self.assertEqual(ActivitySnapshot.objects.count(), 0)

    def test_invalid_thresholds_are_rejected_without_writes(self):
        self.client.force_login(self.editor)

        response = self.client.post(
            reverse("activities:registrations", args=[self.activity.pk]),
            self.update_payload(minimum_participants=11),
        )

        self.assertEqual(response.status_code, 200)
        self.activity.refresh_from_db()
        self.assertEqual(self.activity.minimum_participants, 5)
        self.assertEqual(ActivitySnapshot.objects.count(), 0)

    def test_snapshot_failure_rolls_back_activity_update(self):
        self.client.force_login(self.editor)

        with patch.object(ActivitySnapshot.objects, "create", side_effect=RuntimeError("fail")):
            with self.assertRaises(RuntimeError):
                self.client.post(
                    reverse("activities:registrations", args=[self.activity.pk]),
                    self.update_payload(),
                )

        self.activity.refresh_from_db()
        self.assertEqual(self.activity.registration_count, 4)
        self.assertEqual(ActivitySnapshot.objects.count(), 0)

    def test_snapshot_model_has_no_personal_data_relation(self):
        relation_names = {field.name for field in ActivitySnapshot._meta.get_fields()}

        self.assertEqual(
            relation_names.intersection({"child", "family", "participant"}),
            set(),
        )
