from django.urls import path
from . import views

urlpatterns = [
    # Main pages
    path("", views.index, name="index"),
    path("events/past/", views.past_events, name="past_events"),
    path("events/<int:event_id>/", views.event_detail, name="event_detail"),
    
    # Event management
    path("events/create/", views.create_event, name="create_event"),
    path("events/<int:event_id>/edit/", views.edit_event, name="edit_event"),
    path("events/<int:event_id>/cancel/", views.cancel_event, name="cancel_event"),
    path("events/<int:event_id>/toggle-attendance/", views.toggle_attendance, name="toggle_attendance"),
    path("events/<int:event_id>/comment/", views.add_comment, name="add_comment"),
    
    # User management
    path("profile/", views.user_profile, name="profile"),
    path("profile/edit/", views.edit_profile, name="edit_profile"),
    path("profile/<str:username>/", views.user_profile, name="user_profile"),
    path("my-events/", views.my_events, name="my_events"),
    
    # Authentication
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("register/", views.register, name="register"),
]
