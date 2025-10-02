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

        full_datetime = now + timedelta(days=2)
        self.full_event = Events.objects.create(
            title="Full Tennis Match",
            description="A full event.",
            host=self.host_user,
            date=full_datetime.date(),
            start=full_datetime.time(),
            end=(full_datetime + timedelta(hours=1)).time(),
            timestamp=full_datetime + timedelta(hours=1),
            max_attendees=1,
            category='tennis',
            skill_level='advanced'
        )
        self.full_event.attendees.add(self.attendee_user)

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
        self.assertTrue(self.full_event.is_full)

    def test_spots_available_property(self):
        """Test the spots_available property on the Event model."""
        self.assertEqual(self.upcoming_event.spots_available, 10)
        self.assertEqual(self.full_event.spots_available, 0)

    def test_event_attendance_percentage_property(self):
        """Test the attendance_percentage property on the Event model."""
        self.upcoming_event.attendees.add(self.host_user) # Host is an attendee
        self.assertEqual(self.upcoming_event.attendance_percentage, 10) # 1 of 10
        self.assertEqual(self.full_event.attendance_percentage, 100) # 1 of 1

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
        self.assertEqual(response.json()['status'], 'left') # The new status is "left" (i.e., the button text)

        # Verify in database
        self.upcoming_event.refresh_from_db()
        self.assertIn(self.attendee_user, self.upcoming_event.attendees.all())
        self.assertEqual(self.upcoming_event.number_attending, 1)

        # --- Test Leaving ---
        response = self.client.post(join_url)

        # Check response
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()['success'])
        self.assertEqual(response.json()['status'], 'joined') # The new status is "joined"

        # Verify in database
        self.upcoming_event.refresh_from_db()
        self.assertNotIn(self.attendee_user, self.upcoming_event.attendees.all())
        self.assertEqual(self.upcoming_event.number_attending, 0)

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
