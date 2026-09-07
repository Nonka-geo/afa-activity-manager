from django.urls import include, path


urlpatterns = [
	path("accounts/", include("apps.accounts.urls")),
	path("activities/", include("apps.activities.urls")),
]
