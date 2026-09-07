from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from django.shortcuts import render


EDITOR_PERMISSION = "auth.access_editor_endpoint"


@login_required
def home(request):
    return render(request, "accounts/home.html")


@login_required
def editor_check(request):
    if not request.user.has_perm(EDITOR_PERMISSION):
        return HttpResponseForbidden("Admin/Editor access required.")
    return render(request, "accounts/editor_check.html")
