from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from .forms import UserSettingsForm
from .models import UserSettings


@login_required
def settings_view(request):
    settings_obj, _created = UserSettings.objects.get_or_create(user=request.user)

    if request.method == "POST":
        form = UserSettingsForm(request.POST, instance=settings_obj)
        if form.is_valid():
            form.save()
            messages.success(request, "Your settings have been saved.")
            return redirect("user_settings:settings")
    else:
        form = UserSettingsForm(instance=settings_obj)

    return render(request, "user_settings/settings.html", {"form": form})
