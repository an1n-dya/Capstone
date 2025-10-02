from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator
from datetime import datetime
import pytz

class User(AbstractUser):
    bio = models.TextField(max_length=500, blank=True)
    favorite_sports = models.CharField(max_length=200, blank=True)
    profile_picture = models.ImageField(upload_to='profile_pics/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.username}"
    
    def serialize(self):
        return {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "bio": self.bio,
            "favorite_sports": self.favorite_sports,
        }
    
    def get_hosted_events_count(self):
        return self.events_hosted.count()
    
    def get_attended_events_count(self):
        return self.attending.count()

SPORTS = (
    ("soccer", "Soccer"),
    ("basketball", "Basketball"),
    ("tennis", "Tennis"),
    ("volleyball", "Volleyball"),
    ("baseball", "Baseball"),
    ("football", "Football"),
    ("softball", "Softball"),
    ("golf", "Golf"),
    ("ultimate_frisbee", "Ultimate Frisbee"),
    ("cycling", "Cycling"),
    ("running", "Running"),
    ("swimming", "Swimming"),
    ("badminton", "Badminton"),
    ("table_tennis", "Table Tennis"),
    ("cricket", "Cricket"),
    ("rugby", "Rugby"),
    ("hockey", "Hockey"),
    ("chess", "Chess"),
    ("other", "Other")
)

SKILL_LEVELS = (
    ("beginner", "Beginner"),
    ("intermediate", "Intermediate"),
    ("advanced", "Advanced"),
    ("all", "All Levels")
)

class Events(models.Model):
    title = models.CharField(max_length=100, null=False, blank=False)
    description = models.TextField(max_length=500, null=False, blank=False)
    host = models.ForeignKey(User, on_delete=models.CASCADE, related_name="events_hosted")
    attendees = models.ManyToManyField(User, related_name="attending", blank=True)
    date = models.DateField(blank=False)
    start = models.TimeField(blank=False)
    end = models.TimeField(blank=False)
    timestamp = models.DateTimeField(blank=True)
    category = models.CharField(max_length=64, choices=SPORTS, null=False, blank=False)
    skill_level = models.CharField(max_length=20, choices=SKILL_LEVELS, default="all")
    max_attendees = models.IntegerField(
        default=10,
        validators=[MinValueValidator(2), MaxValueValidator(100)]
    )
    image = models.ImageField(upload_to="events/", null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_cancelled = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['date', 'start']
        verbose_name = "Event"
        verbose_name_plural = "Events"
    
    def __str__(self):
        return f"{self.title} - {self.date}"
    
    @property
    def number_attending(self):
        return self.attendees.count()
    
    @property
    def spots_available(self):
        return self.max_attendees - self.number_attending
    
    @property
    def is_full(self):
        return self.number_attending >= self.max_attendees
    
    @property
    def is_past(self):
        return self.timestamp < timezone.now()
    
    @property
    def is_upcoming(self):
        return not self.is_past and not self.is_cancelled
    
    def can_join(self, user):
        """Check if a user can join this event."""
        if self.is_past or self.is_cancelled or self.is_full:
            return False
        if user == self.host or user in self.attendees.all():
            return False
        return True
    
    def serialize(self):
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "host": self.host.username,
            "host_id": self.host.id,
            "attendees": [user.username for user in self.attendees.all()],
            "date": self.date.strftime("%B %d, %Y"),
            "date_raw": self.date.strftime("%Y-%m-%d"),
            "start": self.start.strftime("%I:%M %p"),
            "end": self.end.strftime("%I:%M %p"),
            "category": self.category,
            "category_display": self.get_category_display(),
            "skill_level": self.skill_level,
            "skill_level_display": self.get_skill_level_display(),
            "number_attending": self.number_attending,
            "max_attendees": self.max_attendees,
            "spots_available": self.spots_available,
            "is_full": self.is_full,
            "image": self.image.url if self.image else None,
            "is_past": self.is_past,
            "created_at": self.created_at.strftime("%B %d, %Y"),
        }

class EventComment(models.Model):
    event = models.ForeignKey(Events, on_delete=models.CASCADE, related_name="comments")
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField(max_length=300)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Comment by {self.author.username} on {self.event.title}"
