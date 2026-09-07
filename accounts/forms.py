from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User

class CustomUserRegisterForm(UserCreationForm):
    role = forms.ChoiceField(
        choices=User.Role.choices,
        widget=forms.Select(attrs={"class": "form-input"}),
        help_text="Select how you will participate in Pop-off Cebu"
    )

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("username", "email", "role")