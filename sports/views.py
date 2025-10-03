from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse, HttpResponseRedirect
from django.urls import reverse
from django.db import IntegrityError
from django.db.models import Q, Count
from django.core.paginator import Paginator
from django.utils import timezone
from django.views.decorators.http import require_http_methods
from django.contrib.humanize.templatetags.humanize import naturaltime
from django.conf import settings
from datetime import datetime

from .models import User, Events, EventComment
from .forms import (
    EventForm, UserProfileForm, CustomUserCreationForm,
    EventFilterForm, CommentForm
)

def _get_profile_picture_url(user):
    """
    Helper function to get a user's profile picture URL or the default.
    """
    if user.profile_picture:
        return user.profile_picture.url
    return settings.STATIC_URL + 'sports/images/default_avatar.png'


def index(request):
    """Display the homepage with upcoming events."""
    # Get filter form
    filter_form = EventFilterForm(request.GET)
    
    # Base queryset for upcoming events
    now = timezone.now()
    events = Events.objects.filter( 
        timestamp__gte=now,
        is_cancelled=False
    ).select_related('host').prefetch_related('attendees')
    
    # Apply filters if form is valid
    if filter_form.is_valid():
        if filter_form.cleaned_data['category']:
            events = events.filter(category=filter_form.cleaned_data['category'])
        if filter_form.cleaned_data['skill_level']:
            events = events.filter(skill_level=filter_form.cleaned_data['skill_level'])
        if filter_form.cleaned_data['date_from']:
            events = events.filter(date__gte=filter_form.cleaned_data['date_from'])
        if filter_form.cleaned_data['date_to']:
            events = events.filter(date__lte=filter_form.cleaned_data['date_to'])
        if filter_form.cleaned_data['search']:
            search_term = filter_form.cleaned_data['search']
            events = events.filter(
                Q(title__icontains=search_term) | 
                Q(description__icontains=search_term)
            )
    
    # Pagination
    paginator = Paginator(events, 9)  # Show 9 events per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'filter_form': filter_form,
        'total_events': paginator.count,
    }
    
    return render(request, "sports/index.html", context)

def event_detail(request, event_id):
    """Display detailed view of a single event."""
    event = get_object_or_404(Events, pk=event_id)
    comments = event.comments.all()
    comment_form = CommentForm()
    
    is_attending = False
    can_join = False
    
    if request.user.is_authenticated:
        is_attending = request.user in event.attendees.all()
        can_join = event.can_join(request.user)
    
    context = {
        'event': event,
        'comments': comments,
        'comment_form': comment_form,
        'is_attending': is_attending,
        'can_join': can_join,
    }
    
    return render(request, "sports/event_detail.html", context)

@login_required
def create_event(request):
    """Create a new event."""
    if request.method == "POST":
        form = EventForm(request.POST, request.FILES)
        
        if form.is_valid():
            # Create event but don't save yet
            event = form.save(commit=False)
            event.host = request.user
            
            # Set timestamp for event end
            event_date = form.cleaned_data['date']
            end_time = form.cleaned_data['end']
            event_end = datetime.combine(event_date, end_time)
            event.timestamp = timezone.make_aware(event_end)
            
            event.save()
            
            # Add host as first attendee
            event.attendees.add(request.user)
            
            messages.success(request, "Event created successfully!")
            return redirect('event_detail', event_id=event.id)
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = EventForm()
    
    return render(request, "sports/create_event.html", {'form': form})

@login_required
def edit_event(request, event_id):
    """Edit an existing event."""
    event = get_object_or_404(Events, pk=event_id)

    if event.is_past:
        messages.error(request, "You cannot edit a past event.")
        return redirect('event_detail', event_id=event.id)
    
    # Check if user is the host
    if request.user != event.host:
        messages.error(request, "You can only edit your own events.")
        return redirect('event_detail', event_id=event.id)
    
    # Prevent editing if other users have already joined
    if event.number_attending > 1:
        messages.warning(request, "You cannot edit an event after other users have joined. Please cancel and create a new event if changes are needed.")
        return redirect('event_detail', event_id=event.id)

    if request.method == "POST":
        form = EventForm(request.POST, request.FILES, instance=event)
        
        if form.is_valid():
            # Update timestamp
            event_date = form.cleaned_data['date']
            end_time = form.cleaned_data['end']
            event_end = datetime.combine(event_date, end_time)
            event.timestamp = timezone.make_aware(event_end)
            
            form.save()
            messages.success(request, "Event updated successfully!")
            return redirect('event_detail', event_id=event.id)
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = EventForm(instance=event)
    
    return render(request, "sports/edit_event.html", {
        'form': form,
        'event': event
    })

@login_required
@require_http_methods(["POST"])
def toggle_attendance(request, event_id):
    """Toggle user's attendance for an event."""
    event = get_object_or_404(Events, pk=event_id)
    user = request.user
    
    if user == event.host:
        return JsonResponse({
            'success': False,
            'message': 'Host cannot leave their own event'
        })
    
    if event.is_past:
        return JsonResponse({
            'success': False,
            'message': 'You cannot join or leave a past event.'
        }, status=400)

    if event.is_cancelled:
        return JsonResponse({
            'success': False,
            'message': 'This event has been cancelled.'
        }, status=400)

    if user in event.attendees.all():
        event.attendees.remove(user)
        message = "You've left the event"
        button_text = "Join Event"
        attending = False
    else:
        if event.is_full:
            return JsonResponse({
                'success': False,
                'message': 'Event is full',
                'attending': False,
            })
        event.attendees.add(user)
        message = "You've joined the event"
        button_text = "Leave Event"
        attending = True
    
    # Prepare attendee list for the response
    attendees = event.attendees.all().order_by('username')[:10]
    attendees_list = [{
        'username': attendee.username,
        'profile_url': reverse('user_profile', args=[attendee.username]),
        'profile_picture_url': _get_profile_picture_url(attendee),
        'is_host': attendee == event.host
    } for attendee in attendees]

    return JsonResponse({
        'success': True,
        'message': message,
        'attending': attending,
        'attendees_count': event.number_attending,
        'spots_available': event.spots_available,
        'max_attendees': event.max_attendees,
        'button_text': button_text,
        'attendees_list': attendees_list,
    })

@login_required
@require_http_methods(["POST"])
def cancel_event(request, event_id):
    """Cancel an event."""
    event = get_object_or_404(Events, pk=event_id)

    if event.is_past:
        return JsonResponse({
            'success': False,
            'message': 'You cannot cancel a past event.'
        })
    
    if request.user != event.host:
        return JsonResponse({
            'success': False,
            'message': 'Only the host can cancel this event'
        })
    
    event.is_cancelled = True
    event.save()
    
    return JsonResponse({
        'success': True,
        'message': 'Event cancelled successfully'
    })

@login_required
def user_profile(request, username=None):
    """Display user profile."""
    if username:
        user = get_object_or_404(User, username=username)
    else:
        user = request.user
    
    # Get user's hosted events
    hosted_events = Events.objects.filter(
        host=user
    ).order_by('-date')[:5]
    
    # Get user's attended events
    attended_events = user.attending.all().order_by('-date')[:5]
    
    context = {
        'profile_user': user,
        'hosted_events': hosted_events,
        'attended_events': attended_events,
        'is_own_profile': user == request.user,
    }
    
    return render(request, "sports/profile.html", context)

@login_required
def edit_profile(request):
    """Edit user profile."""
    if request.method == "POST":
        form = UserProfileForm(request.POST, request.FILES, instance=request.user)
        
        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated successfully!")
            return redirect('profile')
    else:
        form = UserProfileForm(instance=request.user)
    
    return render(request, "sports/edit_profile.html", {'form': form})

@login_required
def my_events(request):
    """Display user's events (hosted and attending)."""
    # Hosted events
    hosted = Events.objects.filter(host=request.user).order_by('-date')
    
    # Attending events
    attending = request.user.attending.exclude(host=request.user).order_by('-date')
    
    context = {
        'hosted_events': hosted,
        'attending_events': attending,
    }
    
    return render(request, "sports/my_events.html", context)

def past_events(request):
    """Display past events."""
    now = timezone.now()
    events = Events.objects.filter( 
        timestamp__lt=now
    ).select_related('host').prefetch_related('attendees').order_by('-date')
    
    paginator = Paginator(events, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, "sports/past_events.html", {'page_obj': page_obj})

@login_required
@require_http_methods(["POST"])
def add_comment(request, event_id):
    """Add a comment to an event."""
    event = get_object_or_404(Events, pk=event_id)
    
    form = CommentForm(request.POST)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.event = event
        comment.author = request.user
        comment.save()
        
        # Prepare data for AJAX response
        return JsonResponse({
            'success': True,
            'comment': {
                'author': comment.author.username,
                'author_pic_url': _get_profile_picture_url(comment.author),
                'author_profile_url': reverse('user_profile', args=[comment.author.username]),
                'content': comment.content,
                # Use a cross-platform compatible way to format time.
                # The '%-I' format code is not supported on Windows.
                'created_at': comment.created_at.strftime("%b. %d, %Y, ") + comment.created_at.strftime("%I:%M %p").lstrip('0').replace("AM", "a.m.").replace("PM", "p.m."),
                'naturaltime': naturaltime(comment.created_at)
            }
        })
    
    return JsonResponse({
        'success': False, 
        'message': 'Invalid comment content.'
    }, status=400)

# Authentication views
def login_view(request):
    """User login."""
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            
            # Handle "Remember me"
            remember_me = request.POST.get('remember')
            if not remember_me:
                request.session.set_expiry(0) # Expire on browser close

            next_url = request.GET.get('next', 'index')
            messages.success(request, f"Welcome back, {user.username}!")
            return redirect(next_url)
        else:
            messages.error(request, "Invalid username or password.")
            return render(request, "sports/login.html")
    
    return render(request, "sports/login.html")

def logout_view(request):
    """User logout."""
    logout(request)
    messages.success(request, "You have been logged out successfully.")
    return redirect('index')

def register(request):
    """User registration."""
    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)
        
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Registration successful! Welcome to Playfield!")
            return redirect('index')
    else:
        form = CustomUserCreationForm()
    
    return render(request, "sports/register.html", {'form': form})
