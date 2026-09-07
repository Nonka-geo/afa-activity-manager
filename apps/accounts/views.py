from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from django.shortcuts import render


ADMIN_EDITOR_GROUP = "Admin/Editor"


def is_admin_editor(user):
    return user.is_authenticated and user.groups.filter(name=ADMIN_EDITOR_GROUP).exists()


@login_required
def home(request):
    return render(request, "accounts/home.html")


@login_required
def editor_check(request):
    if not is_admin_editor(request.user):
        return HttpResponseForbidden("Admin/Editor access required.")
    return render(request, "accounts/editor_check.html")
