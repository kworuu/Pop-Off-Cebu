from django import forms

from .models import Profile


class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = (
            "full_name",
            "business_or_stage_name",
            "district",
            "contact_number",
            "bio",
            "portfolio_url",
            "profile_image",
        )
        labels = {
            "business_or_stage_name": "Business or stage name",
            "portfolio_url": "Portfolio link",
        }
        widgets = {
            "bio": forms.Textarea(attrs={"rows": 4}),
        }
