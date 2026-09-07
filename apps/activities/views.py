from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib.auth.views import redirect_to_login
from django.contrib.messages.views import SuccessMessageMixin
from django.db import transaction
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.views.generic import CreateView, DetailView, ListView, UpdateView

from .forms import ActivityForm, RegistrationUpdateForm
from .models import Activity, ActivitySnapshot, SchoolYear
from .status import ActivityStatus


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
        active_year = SchoolYear.objects.filter(is_active=True).first()
        if active_year is None:
            return Activity.objects.none()

        queryset = Activity.objects.filter(
            school_year=active_year,
            is_archived=False,
        ).select_related("school_year")
        query = self.request.GET.get("q", "").strip()
        if query:
            queryset = queryset.filter(
                Q(name__icontains=query)
                | Q(schedule__icontains=query)
                | Q(provider__icontains=query)
                | Q(age_group__icontains=query)
                | Q(space__icontains=query)
            )

        for field_name in ("schedule", "provider", "space", "age_group"):
            value = self.request.GET.get(field_name, "").strip()
            if value:
                queryset = queryset.filter(**{f"{field_name}__iexact": value})

        school_year = self.request.GET.get("school_year", "").strip()
        if school_year and school_year.lower() != active_year.name.lower():
            return Activity.objects.none()

        status = self.request.GET.get("status", "").strip()
        if status:
            valid_statuses = {str(status_value) for status_value in ActivityStatus}
            if status not in valid_statuses:
                return Activity.objects.none()
            queryset = [activity for activity in queryset if str(activity.status) == status]
        return queryset


class ArchivedActivityListView(ActivityPermissionMixin, ListView):
    model = Activity
    permission_required = "activities.view_activity"
    template_name = "activities/archived_activity_list.html"
    context_object_name = "activities"

    def get_queryset(self):
        return Activity.objects.filter(is_archived=True).select_related("school_year")


class DashboardView(ActivityPermissionMixin, ListView):
    model = Activity
    permission_required = "activities.view_activity"
    template_name = "activities/dashboard.html"
    context_object_name = "activities"

    def get_queryset(self):
        active_year = SchoolYear.objects.filter(is_active=True).first()
        if active_year is None:
            return Activity.objects.none()
        return Activity.objects.filter(
            school_year=active_year,
            is_archived=False,
        ).select_related("school_year")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        active_year = SchoolYear.objects.filter(is_active=True).first()
        activities = list(context["activities"])
        status_counts = {status: 0 for status in ActivityStatus}
        for activity in activities:
            status_counts[activity.status] += 1
        context.update(
            {
                "active_school_year": active_year,
                "total_activities": len(activities),
                "at_risk_count": status_counts[ActivityStatus.AT_RISK],
                "confirmed_count": status_counts[ActivityStatus.CONFIRMED],
                "full_count": status_counts[ActivityStatus.FULL],
                "waiting_list_count": status_counts[ActivityStatus.WAITING_LIST],
                "attention_activities": [
                    activity
                    for activity in activities
                    if activity.status == ActivityStatus.AT_RISK
                ],
            }
        )
        return context


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


class RegistrationUpdateView(ActivityPermissionMixin, UpdateView):
    model = Activity
    form_class = RegistrationUpdateForm
    permission_required = "activities.change_activity"
    template_name = "activities/registration_form.html"

    def form_valid(self, form):
        with transaction.atomic():
            activity = Activity.objects.select_for_update().get(pk=self.object.pk)
            previous_values = (
                activity.registration_count,
                activity.minimum_participants,
                activity.maximum_participants,
            )
            activity.registration_count = form.cleaned_data["registration_count"]
            activity.minimum_participants = form.cleaned_data["minimum_participants"]
            activity.maximum_participants = form.cleaned_data["maximum_participants"]
            current_values = (
                activity.registration_count,
                activity.minimum_participants,
                activity.maximum_participants,
            )
            if current_values != previous_values:
                activity.full_clean()
                activity.save(
                    update_fields=[
                        "registration_count",
                        "minimum_participants",
                        "maximum_participants",
                    ]
                )
                ActivitySnapshot.objects.create(
                    activity=activity,
                    actor=self.request.user,
                    registration_count=activity.registration_count,
                    status=str(activity.status),
                )
            self.object = activity
        return super().form_valid(form)

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