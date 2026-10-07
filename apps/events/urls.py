from django.urls import path

from . import views

app_name = "events"

urlpatterns = [
    path("", views.event_list, name="list"),
    path("mine/", views.my_events, name="mine"),
    path("new/", views.event_create, name="create"),
    path("<slug:slug>/", views.event_detail, name="detail"),
    path("<slug:slug>/edit/", views.event_edit, name="edit"),
    path("<slug:slug>/rsvp/", views.rsvp, name="rsvp"),
    path("<slug:slug>/announce/", views.post_announcement, name="announce"),
]
