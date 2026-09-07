from django.conf import settings
from django.test import SimpleTestCase


class BootstrapSmokeTest(SimpleTestCase):
    def test_project_configuration_loads(self):
        self.assertTrue(settings.configured)
        self.assertIn("apps.accounts", settings.INSTALLED_APPS)
        self.assertIn("apps.activities", settings.INSTALLED_APPS)
        self.assertEqual(settings.DATABASES["default"]["ENGINE"], "django.db.backends.sqlite3")
