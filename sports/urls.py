from django.urls import path
from django.contrib.auth import views as auth_views
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
    
    # Password reset
    path('password-reset/', 
         auth_views.PasswordResetView.as_view(template_name='sports/password_reset.html'), 
         name='password_reset'),
    path('password-reset/done/', 
         auth_views.PasswordResetDoneView.as_view(template_name='sports/password_reset_done.html'), 
         name='password_reset_done'),
    path('reset/<uidb64>/<token>/', 
         auth_views.PasswordResetConfirmView.as_view(template_name='sports/password_reset_confirm.html'), 
         name='password_reset_confirm'),
    path('reset/done/', 
         auth_views.PasswordResetCompleteView.as_view(template_name='sports/password_reset_complete.html'), 
         name='password_reset_complete'),
    
    # API endpoints
    path("api/events/", views.api_events, name="api_events"),
    path("api/events/<int:event_id>/", views.api_event, name="api_event"),
]
