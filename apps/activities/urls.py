from django.urls import path

from . import views


app_name = "activities"

urlpatterns = [
    path("", views.ActiveActivityListView.as_view(), name="list"),
    path("archived/", views.ArchivedActivityListView.as_view(), name="archived_list"),
    path("create/", views.ActivityCreateView.as_view(), name="create"),
    path("<int:pk>/", views.ActivityDetailView.as_view(), name="detail"),
    path("<int:pk>/edit/", views.ActivityUpdateView.as_view(), name="edit"),
    path("<int:pk>/registrations/", views.RegistrationUpdateView.as_view(), name="registrations"),
    path("<int:pk>/archive/", views.archive_activity, name="archive"),
]