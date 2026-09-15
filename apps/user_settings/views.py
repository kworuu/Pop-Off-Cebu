from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib import messages
from apps.profiles.forms import ProfileForm
from .models import UserSettings

@login_required
def settings_view(request):
    user = request.user
    profile = user.profile
    settings_obj, _ = UserSettings.objects.get_or_create(user=user)

    if request.method == "POST":
        action = request.POST.get("action")

        if action == "profile":
            form = ProfileForm(request.POST, request.FILES, instance=profile)
            if form.is_valid():
                form.save()
                messages.success(request, "Profile details updated successfully.")
                return redirect("user_settings:settings")
        
        elif action == "security":
            pwd_form = PasswordChangeForm(user, request.POST)
            if pwd_form.is_valid():
                updated_user = pwd_form.save()
                update_session_auth_hash(request, updated_user)
                messages.success(request, "Password updated successfully.")
                return redirect("user_settings:settings")
            else:
                messages.error(request, "Please fix the password errors below.")

        elif action == "preferences":
            settings_obj.email_notifications = request.POST.get("email_notifications") == "on"
            settings_obj.public_profile = request.POST.get("public_profile") == "on"
            settings_obj.save()
            messages.success(request, "Preferences saved.")
            return redirect("user_settings:settings")

    profile_form = ProfileForm(instance=profile)
    pwd_form = PasswordChangeForm(user)

    return render(request, "user_settings/settings.html", {
        "profile_form": profile_form,
        "pwd_form": pwd_form,
        "user_settings": settings_obj,
    })