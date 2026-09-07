from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib import messages
from .forms import CustomUserRegisterForm

def register_view(request):
    if request.method == "POST":
        form = CustomUserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f"Welcome to Pop-off Cebu, {user.username}!")
            return redirect("home")
    else:
        form = CustomUserRegisterForm()
    return render(request, "accounts/register.html", {"form": form})