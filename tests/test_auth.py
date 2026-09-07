from django.contrib.auth.models import Group, User
from django.test import TestCase
from django.urls import reverse


class AuthenticationAndRolesTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.editor_group = Group.objects.get(name="Admin/Editor")
        cls.viewer_group = Group.objects.get(name="Viewer")
        cls.editor = User.objects.create_user(username="editor", password="editor-pass")
        cls.viewer = User.objects.create_user(username="viewer", password="viewer-pass")
        cls.editor.groups.add(cls.editor_group)
        cls.viewer.groups.add(cls.viewer_group)

    def test_login_page_is_available_to_anonymous_users(self):
        response = self.client.get(reverse("accounts:login"))

        self.assertEqual(response.status_code, 200)

    def test_valid_login_redirects_to_authenticated_home(self):
        response = self.client.post(
            reverse("accounts:login"),
            {"username": "viewer", "password": "viewer-pass"},
        )

        self.assertRedirects(response, reverse("accounts:home"))

    def test_invalid_login_does_not_authenticate_user(self):
        response = self.client.post(
            reverse("accounts:login"),
            {"username": "viewer", "password": "wrong-pass"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertNotIn("_auth_user_id", self.client.session)

    def test_logout_ends_session(self):
        self.client.force_login(self.viewer)

        response = self.client.post(reverse("accounts:logout"))

        self.assertRedirects(response, reverse("accounts:login"))
        home_response = self.client.get(reverse("accounts:home"))
        self.assertRedirects(
            home_response,
            f"{reverse('accounts:login')}?next={reverse('accounts:home')}",
        )

    def test_anonymous_user_is_redirected_from_authenticated_home(self):
        response = self.client.get(reverse("accounts:home"))

        self.assertRedirects(
            response,
            f"{reverse('accounts:login')}?next={reverse('accounts:home')}",
        )

    def test_viewer_can_access_authenticated_home(self):
        self.client.force_login(self.viewer)

        response = self.client.get(reverse("accounts:home"))

        self.assertEqual(response.status_code, 200)

    def test_editor_can_access_authenticated_home_and_editor_check(self):
        self.client.force_login(self.editor)

        home_response = self.client.get(reverse("accounts:home"))
        editor_response = self.client.get(reverse("accounts:editor_check"))

        self.assertEqual(home_response.status_code, 200)
        self.assertEqual(editor_response.status_code, 200)

    def test_viewer_is_denied_editor_check(self):
        self.client.force_login(self.viewer)

        response = self.client.get(reverse("accounts:editor_check"))

        self.assertEqual(response.status_code, 403)

    def test_required_groups_and_assignments_exist(self):
        self.assertEqual(
            set(Group.objects.values_list("name", flat=True)),
            {"Admin/Editor", "Viewer"},
        )
        self.assertTrue(self.editor.groups.filter(name="Admin/Editor").exists())
        self.assertTrue(self.viewer.groups.filter(name="Viewer").exists())
