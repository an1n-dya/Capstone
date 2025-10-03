from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils import timezone
from datetime import timedelta

from sports.models import Events, EventComment

User = get_user_model()

class SportsAppTests(TestCase):
    """
    Test suite for the sports app.
    """

    def setUp(self):
        """
        Set up data for the tests.
        """
        # Create users
        self.host_user = User.objects.create_user(username='host', password='password123')
        self.attendee_user = User.objects.create_user(username='attendee', password='password123')

        # Create events
        now = timezone.now()
        upcoming_datetime = now + timedelta(days=7)
        self.upcoming_event = Events.objects.create(
            title="Upcoming Soccer Game",
            description="A friendly game of soccer.",
            host=self.host_user,
            date=upcoming_datetime.date(),
            start=upcoming_datetime.time(),
            end=(upcoming_datetime + timedelta(hours=2)).time(),
            timestamp=upcoming_datetime + timedelta(hours=2),
            max_attendees=10,
            category='soccer',
            skill_level='intermediate'
        )
        self.upcoming_event.attendees.add(self.host_user)

        past_datetime = now - timedelta(days=1)
        self.past_event = Events.objects.create(
            title="Past Basketball Game",
            description="A game that already happened.",
            host=self.host_user,
            date=past_datetime.date(),
            start=past_datetime.time(),
            end=(past_datetime + timedelta(hours=2)).time(),
            timestamp=past_datetime + timedelta(hours=2),
            max_attendees=5,
            category='basketball',
            skill_level='beginner'
        )
        self.past_event.attendees.add(self.host_user)

        full_datetime = now + timedelta(days=2)
        self.full_event = Events.objects.create(
            title="Full Tennis Match",
            description="A full event.",
            host=self.host_user,
            date=full_datetime.date(),
            start=full_datetime.time(),
            end=(full_datetime + timedelta(hours=1)).time(),
            timestamp=full_datetime + timedelta(hours=1),
            max_attendees=2,
            category='tennis',
            skill_level='advanced'
        )
        self.full_event.attendees.add(self.host_user, self.attendee_user) # 2 attendees

    def test_user_model_creation(self):
        """Test that a user can be created successfully."""
        self.assertEqual(User.objects.count(), 2)
        self.assertEqual(self.host_user.username, 'host')

    def test_event_model_creation(self):
        """Test that an event can be created successfully."""
        self.assertEqual(Events.objects.count(), 3)
        self.assertEqual(self.upcoming_event.title, "Upcoming Soccer Game")
        self.assertEqual(self.upcoming_event.host, self.host_user)

    def test_event_is_past_property(self):
        """Test the is_past property on the Event model."""
        self.assertFalse(self.upcoming_event.is_past)
        self.assertTrue(self.past_event.is_past)

    def test_event_is_full_property(self):
        """Test the is_full property on the Event model."""
        self.assertFalse(self.upcoming_event.is_full)
        # self.full_event is set up to be full
        self.assertTrue(self.full_event.is_full) # Host + attendee = 2

    def test_spots_available_property(self):
        """Test the spots_available property on the Event model."""
        self.assertEqual(self.upcoming_event.spots_available, 9) # 10 max - 1 host
        self.assertEqual(self.full_event.spots_available, 0)

    def test_event_attendance_percentage_property(self):
        """Test the attendance_percentage property on the Event model."""
        self.assertEqual(self.upcoming_event.attendance_percentage, 10) # 1 of 10
        self.assertEqual(self.full_event.attendance_percentage, 100) # 2 of 2

    def test_index_view(self):
        """Test that the index view loads and displays upcoming events."""
        response = self.client.get(reverse('index'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Upcoming Soccer Game")
        self.assertNotContains(response, "Past Basketball Game")

    def test_past_events_view(self):
        """Test that the past_events view loads and displays past events."""
        response = self.client.get(reverse('past_events'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Past Basketball Game")
        self.assertNotContains(response, "Upcoming Soccer Game")

    def test_event_detail_view(self):
        """Test that the event detail view loads correctly."""
        response = self.client.get(reverse('event_detail', args=[self.upcoming_event.id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Upcoming Soccer Game")

    def test_create_event_view_requires_login(self):
        """Test that an unauthenticated user is redirected from the create event page."""
        response = self.client.get(reverse('create_event'))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, f"{reverse('login')}?next={reverse('create_event')}")

    def test_successful_event_creation(self):
        """Test that a logged-in user can successfully create an event."""
        self.client.login(username='host', password='password123')
        event_count_before = Events.objects.count()
        event_data = {
            'title': 'New Frisbee Game',
            'description': 'A new game for everyone.',
            'date': (timezone.now() + timedelta(days=10)).strftime('%Y-%m-%d'),
            'start': '10:00',
            'end': '12:00',
            'category': 'ultimate_frisbee',
            'skill_level': 'all',
            'max_attendees': 20
        }
        response = self.client.post(reverse('create_event'), event_data)
        
        # Check that the event was created and we were redirected
        self.assertEqual(Events.objects.count(), event_count_before + 1)
        new_event = Events.objects.get(title='New Frisbee Game')
        self.assertRedirects(response, reverse('event_detail', args=[new_event.id]))

        # Check that the host is automatically an attendee
        self.assertIn(self.host_user, new_event.attendees.all())

    def test_join_and_leave_event(self):
        """Test that a logged-in user can join and then leave an event."""
        # Log in the attendee
        self.client.login(username='attendee', password='password123')

        # --- Test Joining ---
        join_url = reverse('toggle_attendance', args=[self.upcoming_event.id])
        response = self.client.post(join_url)
        
        # Check response
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()['success'])
        self.assertEqual(response.json()['button_text'], 'Leave Event')

        # Verify in database
        self.upcoming_event.refresh_from_db()
        self.assertIn(self.attendee_user, self.upcoming_event.attendees.all())
        self.assertEqual(self.upcoming_event.number_attending, 2) # Host + attendee

        # --- Test Leaving ---
        response = self.client.post(join_url)

        # Check response
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()['success'])
        self.assertEqual(response.json()['button_text'], 'Join Event')

        # Verify in database
        self.upcoming_event.refresh_from_db()
        self.assertNotIn(self.attendee_user, self.upcoming_event.attendees.all())
        self.assertEqual(self.upcoming_event.number_attending, 1) # Just the host remains

    def test_post_comment(self):
        """Test that a logged-in user can post a comment on an event."""
        self.client.login(username='attendee', password='password123')
        comment_url = reverse('add_comment', args=[self.upcoming_event.id])
        comment_text = "Looking forward to this game!"

        response = self.client.post(comment_url, {'content': comment_text})

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()['success'])
        self.assertTrue(EventComment.objects.filter(
            event=self.upcoming_event, 
            author=self.attendee_user,
            content=comment_text
        ).exists())

    def test_host_can_cancel_event(self):
        """Test that the host of an event can cancel it."""
        self.client.login(username='host', password='password123')
        cancel_url = reverse('cancel_event', args=[self.upcoming_event.id])
        response = self.client.post(cancel_url)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()['success'])
        self.upcoming_event.refresh_from_db()
        self.assertTrue(self.upcoming_event.is_cancelled)

    def test_non_host_cannot_edit_event(self):
        """Test that a user who is not the host cannot edit an event."""
        # Log in as a regular attendee
        self.client.login(username='attendee', password='password123')
        edit_url = reverse('edit_event', args=[self.upcoming_event.id])
        
        # Try to POST data to edit the event
        response = self.client.post(edit_url, {'title': 'Changed Title'})
        self.assertRedirects(response, reverse('event_detail', args=[self.upcoming_event.id]))
        self.upcoming_event.refresh_from_db()
        self.assertNotEqual(self.upcoming_event.title, 'Changed Title')

    def test_cannot_join_full_event(self):
        """Test that a user cannot join an event that is already full."""
        # Create a new user to try and join
        joiner_user = User.objects.create_user(username='joiner', password='password123')
        self.client.login(username='joiner', password='password123')

        # Try to join the full event
        join_url = reverse('toggle_attendance', args=[self.full_event.id])
        response = self.client.post(join_url)

        # Check response
        self.assertEqual(response.status_code, 400)
        self.assertFalse(response.json()['success'])
        self.assertEqual(response.json()['message'], 'Event is full')

        # Verify user is not added to attendees
        self.full_event.refresh_from_db()
        self.assertNotIn(joiner_user, self.full_event.attendees.all())

    def test_host_cannot_leave_event(self):
        """Test that the host of an event cannot leave it."""
        self.upcoming_event.attendees.add(self.host_user) # Ensure host is an attendee
        self.client.login(username='host', password='password123')
        leave_url = reverse('toggle_attendance', args=[self.upcoming_event.id])
        response = self.client.post(leave_url)

        # Check response
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.json()['success'])
        self.assertEqual(response.json()['message'], 'Host cannot leave their own event')

    def test_non_host_cannot_cancel_event(self):
        """Test that a user who is not the host cannot cancel an event."""
        self.client.login(username='attendee', password='password123')
        cancel_url = reverse('cancel_event', args=[self.upcoming_event.id])
        response = self.client.post(cancel_url)

        # Check response
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.json()['success'])
        self.assertEqual(response.json()['message'], 'Only the host can cancel this event')

        # Verify event is not cancelled
        self.upcoming_event.refresh_from_db()
        self.assertFalse(self.upcoming_event.is_cancelled)

    def test_invalid_event_creation(self):
        """Test that creating an event with invalid data (e.g., end time before start time) fails."""
        self.client.login(username='host', password='password123')
        event_count_before = Events.objects.count()
        invalid_event_data = {
            'title': 'Invalid Event',
            'description': 'This should not be created.',
            'date': (timezone.now() + timedelta(days=5)).strftime('%Y-%m-%d'),
            'start': '14:00',
            'end': '13:00',  # End time is before start time
            'category': 'other',
            'skill_level': 'all',
            'max_attendees': 5
        }
        response = self.client.post(reverse('create_event'), invalid_event_data)

        # Check that we are re-rendered the form page with an error
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "End time must be after start time.")
        self.assertEqual(Events.objects.count(), event_count_before)

    def test_event_filtering_on_index(self):
        """Test that the event filtering on the index page works correctly."""
        # There is 1 'soccer' event and 1 'basketball' event upcoming (in setUp)
        response = self.client.get(reverse('index'), {'category': 'soccer'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Upcoming Soccer Game")
        self.assertNotContains(response, "Full Tennis Match") # Different category

        response = self.client.get(reverse('index'), {'category': 'basketball'})
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, "Upcoming Soccer Game")

    def test_cannot_edit_event_with_other_attendees(self):
        """Test that a host cannot edit an event once other users have joined."""
        # Have another user join the event
        self.upcoming_event.attendees.add(self.attendee_user) # Host is already attending from setUp
        self.assertEqual(self.upcoming_event.number_attending, 2)

        # Log in as the host and try to edit
        self.client.login(username='host', password='password123')
        edit_url = reverse('edit_event', args=[self.upcoming_event.id])
        response = self.client.get(edit_url) # A GET request is enough to test the redirect

        # Check for redirect and warning message
        self.assertRedirects(response, reverse('event_detail', args=[self.upcoming_event.id]))
        
        # To check the message, we need to follow the redirect
        response_followed = self.client.get(edit_url, follow=True)
        self.assertContains(response_followed, "You cannot edit an event after other users have joined.")

    def test_cannot_join_cancelled_event(self):
        """Test that a user cannot join an event that has been cancelled."""
        # Cancel the event first
        self.upcoming_event.is_cancelled = True
        self.upcoming_event.save()

        # Log in and try to join
        self.client.login(username='attendee', password='password123')
        join_url = reverse('toggle_attendance', args=[self.upcoming_event.id])
        response = self.client.post(join_url)

        # Check for failure response
        self.assertEqual(response.status_code, 400)
        self.assertFalse(response.json()['success'])
        self.assertEqual(response.json()['message'], 'This event has been cancelled.')

    def test_my_events_view_displays_correct_events(self):
        """Test that the 'My Events' page correctly separates hosted and attended events."""
        # The attendee_user is already attending full_event from setUp
        # The host_user is hosting all events
        
        # Log in as the host
        self.client.login(username='host', password='password123')
        response = self.client.get(reverse('my_events'))
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Upcoming Soccer Game") # Hosted
        self.assertContains(response, "Past Basketball Game") # Hosted
        self.assertContains(response, "Full Tennis Match") # Hosted
        self.assertContains(response, "Hosted Events")
        self.assertNotContains(response, "Events I'm Attending") # Host is not attending any other events

    def test_event_creation_duration_validation(self):
        """Test that creating an event with a duration less than 1 hour fails."""
        self.client.login(username='host', password='password123')
        invalid_duration_data = {
            'title': 'Too Short Event',
            'description': 'This event is too short.',
            'date': (timezone.now() + timedelta(days=5)).strftime('%Y-%m-%d'),
            'start': '14:00',
            'end': '14:30',  # Only 30 minutes long
            'category': 'other',
            'skill_level': 'all',
            'max_attendees': 5
        }
        response = self.client.post(reverse('create_event'), invalid_duration_data)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Event must be at least 1 hour long.")

    def test_user_can_edit_own_profile(self):
        """Test that a logged-in user can successfully edit their own profile."""
        self.client.login(username='attendee', password='password123')
        profile_data = {'first_name': 'John', 'last_name': 'Doe', 'bio': 'A new bio.'}
        response = self.client.post(reverse('edit_profile'), profile_data)

        # Check for redirect to profile page
        self.assertRedirects(response, reverse('profile'))

        # Verify the data was saved
        self.attendee_user.refresh_from_db()
        self.assertEqual(self.attendee_user.first_name, 'John')
        self.assertEqual(self.attendee_user.bio, 'A new bio.')
