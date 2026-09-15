from django import forms

from .models import Profile


class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ("full_name", "bio", "profile_image")
        widgets = {
            "bio": forms.Textarea(attrs={"rows": 4}),
        }
