from django.shortcuts import render
from django.contrib.auth.decorators import login_required

@login_required
def profile_view(request):
    profile = request.user.profile
    role = request.user.role

    # Dynamic metrics per Pop-off Cebu user type
    stats_map = {
        "ORGANIZER": {"label": "Events Hosted", "value": 3},
        "VENDOR": {"label": "Active Stalls", "value": 8},
        "PERFORMER": {"label": "Gigs Booked", "value": 12},
        "ATTENDEE": {"label": "Bookmarked Bazaars", "value": 5},
    }
    stat = stats_map.get(role, {"label": "Platform Activities", "value": 0})

    return render(request, "profiles/profile.html", {
        "profile": profile,
        "stat": stat,
    })