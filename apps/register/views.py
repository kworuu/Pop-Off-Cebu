from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib import messages
from .forms import CustomUserRegisterForm

def register_view(request):
    if request.user.is_authenticated:
        return redirect("home:home")

    if request.method == "POST":
        form = CustomUserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data["password"])
            user.save()

            login(request, user)
            messages.success(request, f"Welcome to Pop-off Cebu, {user.username}!")
            return redirect("home:home")
        else:
            messages.error(request, "Please correct the registration errors below.")
    else:
        form = CustomUserRegisterForm()

    return render(request, "register/register.html", {"form": form})