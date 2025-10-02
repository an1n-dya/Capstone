from django import forms
from django.forms import ModelForm
from django.contrib.auth.forms import UserCreationForm
from .models import Events, User, EventComment
from datetime import datetime, date, timedelta
import pytz

class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    
    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        if commit:
            user.save()
        return user

class UserProfileForm(ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'bio', 'favorite_sports', 'profile_picture']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'bio': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'favorite_sports': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., Soccer, Basketball, Tennis'
            }),
            'profile_picture': forms.FileInput(attrs={'class': 'form-control'}),
        }

class EventForm(ModelForm):
    class Meta:
        model = Events
        fields = ['title', 'description', 'date', 'start', 'end', 'category', 
                  'skill_level', 'max_attendees', 'location', 'image']
        
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Give your event a catchy title'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Describe what participants can expect, what to bring, etc.'
            }),
            'date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'start': forms.TimeInput(attrs={
                'class': 'form-control',
                'type': 'time'
            }),
            'end': forms.TimeInput(attrs={
                'class': 'form-control',
                'type': 'time'
            }),
            'category': forms.Select(attrs={'class': 'form-control'}),
            'skill_level': forms.Select(attrs={'class': 'form-control'}),
            'max_attendees': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 2,
                'max': 100
            }),
            'location': forms.TextInput(attrs={
                'class': 'form-control',
                'id': 'autocomplete',
                'placeholder': 'Start typing to search for a location...'
            }),
            'image': forms.FileInput(attrs={'class': 'form-control'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Set minimum date to today for new events
        if not self.instance.pk:
            today = date.today()
            self.fields['date'].widget.attrs['min'] = today.strftime('%Y-%m-%d')
    
    def clean(self):
        cleaned_data = super().clean()
        event_date = cleaned_data.get('date')
        start_time = cleaned_data.get('start')
        end_time = cleaned_data.get('end')
        
        # Validate date is in the future
        if event_date:
            if event_date < date.today():
                raise forms.ValidationError("Event date must be in the past.")
        
        # Validate end time is after start time
        if start_time and end_time:
            if end_time <= start_time:
                raise forms.ValidationError("End time must be after start time.")
            
            # Validate minimum duration (1 hour)
            start_dt = datetime.combine(date.today(), start_time)
            end_dt = datetime.combine(date.today(), end_time)
            duration = (end_dt - start_dt).total_seconds() / 3600
            
            if duration < 1:
                raise forms.ValidationError("Event must be at least 1 hour long.")
            
            if duration > 8:
                raise forms.ValidationError("Event cannot be longer than 8 hours.")
        
        return cleaned_data

class EventFilterForm(forms.Form):
    category = forms.ChoiceField(
        choices=[('', 'All Sports')] + list(Events._meta.get_field('category').choices),
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    skill_level = forms.ChoiceField(
        choices=[('', 'All Levels')] + list(Events._meta.get_field('skill_level').choices),
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    date_from = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        })
    )
    date_to = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        })
    )
    search = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Search by title or location...'
        })
    )

class CommentForm(ModelForm):
    class Meta:
        model = EventComment
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'Add a comment...'
            })
        }
