from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib.auth.views import redirect_to_login
from django.contrib.messages.views import SuccessMessageMixin
from django.shortcuts import get_object_or_404, redirect, render
from django.views.generic import CreateView, DetailView, ListView, UpdateView

from .forms import ActivityForm
from .models import Activity


class ActivityPermissionMixin(LoginRequiredMixin, PermissionRequiredMixin):
    raise_exception = True

    def handle_no_permission(self):
        if not self.request.user.is_authenticated:
            return redirect_to_login(
                self.request.get_full_path(),
                self.get_login_url(),
                self.get_redirect_field_name(),
            )
        return super().handle_no_permission()


class ActiveActivityListView(ActivityPermissionMixin, ListView):
    model = Activity
    permission_required = "activities.view_activity"
    template_name = "activities/activity_list.html"
    context_object_name = "activities"

    def get_queryset(self):
        return Activity.objects.filter(is_archived=False).select_related("school_year")


class ArchivedActivityListView(ActivityPermissionMixin, ListView):
    model = Activity
    permission_required = "activities.view_activity"
    template_name = "activities/archived_activity_list.html"
    context_object_name = "activities"

    def get_queryset(self):
        return Activity.objects.filter(is_archived=True).select_related("school_year")


class ActivityDetailView(ActivityPermissionMixin, DetailView):
    model = Activity
    permission_required = "activities.view_activity"
    template_name = "activities/activity_detail.html"
    context_object_name = "activity"


class ActivityCreateView(ActivityPermissionMixin, SuccessMessageMixin, CreateView):
    model = Activity
    form_class = ActivityForm
    permission_required = "activities.add_activity"
    template_name = "activities/activity_form.html"
    success_message = "Activity created."

    def get_success_url(self):
        return self.object.get_absolute_url()


class ActivityUpdateView(ActivityPermissionMixin, SuccessMessageMixin, UpdateView):
    model = Activity
    form_class = ActivityForm
    permission_required = "activities.change_activity"
    template_name = "activities/activity_form.html"
    success_message = "Activity updated."

    def get_success_url(self):
        return self.object.get_absolute_url()


def archive_activity(request, pk):
    if not request.user.is_authenticated:
        from django.contrib.auth.views import redirect_to_login

        return redirect_to_login(request.get_full_path())
    if not request.user.has_perm("activities.change_activity"):
        from django.core.exceptions import PermissionDenied

        raise PermissionDenied
    if request.method != "POST":
        return render(
            request,
            "activities/archive_confirm.html",
            {"activity": get_object_or_404(Activity, pk=pk)},
        )
    activity = get_object_or_404(Activity, pk=pk, is_archived=False)
    activity.is_archived = True
    activity.save(update_fields=["is_archived"])
    return redirect("activities:archived_list")