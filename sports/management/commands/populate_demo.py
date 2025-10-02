from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import datetime, timedelta
import random

from sports.models import User, Events, EventComment


class Command(BaseCommand):
    help = 'Populate database with demo data for Sports Meets'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing demo data before populating',
        )

    def handle(self, *args, **options):
        if options['clear']:
            self.stdout.write("Clearing existing demo data...")
            EventComment.objects.all().delete()
            Events.objects.all().delete()
            User.objects.filter(is_superuser=False).delete()
            self.stdout.write(self.style.SUCCESS('✓ Cleared existing data'))

        self.stdout.write("\n" + "="*50)
        self.stdout.write("Creating Demo Users...")
        self.stdout.write("="*50)

        # Create demo users with profiles
        demo_users = [
            {
                'username': 'sarah_runner',
                'email': 'sarah@example.com',
                'password': 'demo1234',
                'first_name': 'Sarah',
                'last_name': 'Johnson',
                'bio': 'Marathon runner and fitness enthusiast. Love organizing community runs!',
                'favorite_sports': 'Running, Cycling, Swimming'
            },
            {
                'username': 'mike_baller',
                'email': 'mike@example.com',
                'password': 'demo1234',
                'first_name': 'Mike',
                'last_name': 'Davis',
                'bio': 'Basketball player since high school. Always up for a pickup game!',
                'favorite_sports': 'Basketball, Volleyball, Baseball'
            },
            {
                'username': 'emma_tennis',
                'email': 'emma@example.com',
                'password': 'demo1234',
                'first_name': 'Emma',
                'last_name': 'Wilson',
                'bio': 'Tennis coach and player. Looking to connect with other racquet sports fans.',
                'favorite_sports': 'Tennis, Badminton, Table Tennis'
            },
            {
                'username': 'alex_soccer',
                'email': 'alex@example.com',
                'password': 'demo1234',
                'first_name': 'Alex',
                'last_name': 'Martinez',
                'bio': 'Soccer fanatic! Play every weekend and love teaching beginners.',
                'favorite_sports': 'Soccer, Football, Rugby'
            },
            {
                'username': 'lisa_fitness',
                'email': 'lisa@example.com',
                'password': 'demo1234',
                'first_name': 'Lisa',
                'last_name': 'Chen',
                'bio': 'Personal trainer and group fitness instructor. Health is wealth!',
                'favorite_sports': 'Cycling, Running, Volleyball'
            },
            {
                'username': 'david_swimmer',
                'email': 'david@example.com',
                'password': 'demo1234',
                'first_name': 'David',
                'last_name': 'Brown',
                'bio': 'Former college swimmer. Now I swim for fun and fitness.',
                'favorite_sports': 'Swimming, Water Polo'
            },
            {
                'username': 'rachel_yoga',
                'email': 'rachel@example.com',
                'password': 'demo1234',
                'first_name': 'Rachel',
                'last_name': 'Taylor',
                'bio': 'Yoga instructor with a passion for outdoor activities and hiking.',
                'favorite_sports': 'Yoga, Hiking, Cycling'
            },
            {
                'username': 'james_cricket',
                'email': 'james@example.com',
                'password': 'demo1234',
                'first_name': 'James',
                'last_name': 'Patel',
                'bio': 'Cricket enthusiast organizing weekend matches. All skill levels welcome!',
                'favorite_sports': 'Cricket, Baseball, Golf'
            }
        ]

        users = []
        for user_data in demo_users:
            user, created = User.objects.get_or_create(
                username=user_data['username'],
                defaults={
                    'email': user_data['email'],
                    'first_name': user_data['first_name'],
                    'last_name': user_data['last_name'],
                    'bio': user_data['bio'],
                    'favorite_sports': user_data['favorite_sports']
                }
            )
            if created:
                user.set_password(user_data['password'])
                user.save()
                self.stdout.write(self.style.SUCCESS(f"✓ Created user: {user.username} ({user.get_full_name()})"))
            else:
                self.stdout.write(self.style.WARNING(f"○ User already exists: {user.username}"))
            users.append(user)

        self.stdout.write(f"\nTotal users: {len(users)}")

        self.stdout.write("\n" + "="*50)
        self.stdout.write("Creating Demo Events...")
        self.stdout.write("="*50)

        # Event templates
        event_templates = [
            # Soccer events
            {
                'title': 'Weekend Soccer Match',
                'description': 'Friendly 5v5 soccer game at Central Park. Bring your own water and shin guards. All skill levels welcome!',
                'category': 'soccer',
                'skill_level': 'all',
                'max_attendees': 10,
                'duration_hours': 2
            },
            {
                'title': 'Competitive Soccer League',
                'description': 'Weekly competitive soccer matches. Looking for experienced players to join our league.',
                'category': 'soccer',
                'skill_level': 'advanced',
                'max_attendees': 12,
                'duration_hours': 2
            },
            # Basketball events
            {
                'title': 'Pickup Basketball Game',
                'description': 'Casual basketball at the community center. Full court game, first come first served.',
                'category': 'basketball',
                'skill_level': 'intermediate',
                'max_attendees': 10,
                'duration_hours': 2
            },
            {
                'title': 'Sunday Morning Hoops',
                'description': 'Early morning basketball for early birds! Great way to start your Sunday.',
                'category': 'basketball',
                'skill_level': 'all',
                'max_attendees': 8,
                'duration_hours': 1.5
            },
            # Tennis events
            {
                'title': 'Doubles Tennis Tournament',
                'description': 'Friendly doubles tournament. Partners will be randomly assigned. Prizes for winners!',
                'category': 'tennis',
                'skill_level': 'intermediate',
                'max_attendees': 8,
                'duration_hours': 3
            },
            {
                'title': 'Beginner Tennis Clinic',
                'description': 'Learn the basics of tennis with coach Emma. Racquets provided if needed.',
                'category': 'tennis',
                'skill_level': 'beginner',
                'max_attendees': 6,
                'duration_hours': 2
            },
            # Running events
            {
                'title': '5K Morning Run',
                'description': 'Join us for a refreshing morning 5K run through the park trails. All paces welcome!',
                'category': 'running',
                'skill_level': 'all',
                'max_attendees': 20,
                'duration_hours': 1
            },
            {
                'title': 'Trail Running Adventure',
                'description': '10K trail run for experienced runners. Beautiful scenery and challenging terrain.',
                'category': 'running',
                'skill_level': 'advanced',
                'max_attendees': 15,
                'duration_hours': 1.5
            },
            # Cycling events
            {
                'title': 'Saturday Cycling Group',
                'description': '20-mile leisure ride along the river path. Moderate pace, stops for photos.',
                'category': 'cycling',
                'skill_level': 'intermediate',
                'max_attendees': 12,
                'duration_hours': 2
            },
            {
                'title': 'Beginner Cycling Club',
                'description': 'New to cycling? Join our supportive group for an easy 10-mile ride.',
                'category': 'cycling',
                'skill_level': 'beginner',
                'max_attendees': 10,
                'duration_hours': 1.5
            },
            # Swimming events
            {
                'title': 'Open Water Swimming',
                'description': 'Lake swimming session for experienced swimmers. Safety kayak provided.',
                'category': 'swimming',
                'skill_level': 'advanced',
                'max_attendees': 8,
                'duration_hours': 1
            },
            {
                'title': 'Masters Swim Practice',
                'description': 'Coached swimming practice at the community pool. Focus on technique and endurance.',
                'category': 'swimming',
                'skill_level': 'intermediate',
                'max_attendees': 12,
                'duration_hours': 1
            },
            # Volleyball events
            {
                'title': 'Beach Volleyball Fun',
                'description': 'Casual beach volleyball games. Bring sunscreen and good vibes!',
                'category': 'volleyball',
                'skill_level': 'all',
                'max_attendees': 8,
                'duration_hours': 2
            },
            # Cricket events
            {
                'title': 'Cricket Match - T20 Format',
                'description': 'Twenty20 cricket match. All equipment provided. Beginners welcome!',
                'category': 'cricket',
                'skill_level': 'all',
                'max_attendees': 16,
                'duration_hours': 3
            },
            # Ultimate Frisbee
            {
                'title': 'Ultimate Frisbee Pickup',
                'description': 'Fun and competitive Ultimate Frisbee game. New players encouraged!',
                'category': 'ultimate_frisbee',
                'skill_level': 'all',
                'max_attendees': 14,
                'duration_hours': 2
            },
            # Golf
            {
                'title': 'Golf Club Meetup',
                'description': '9 holes of golf followed by lunch at the clubhouse. Handicap 15-25 preferred.',
                'category': 'golf',
                'skill_level': 'intermediate',
                'max_attendees': 4,
                'duration_hours': 3
            },
            # Baseball
            {
                'title': 'Softball Sunday League',
                'description': 'Weekly softball games. Looking for players to fill our roster!',
                'category': 'softball',
                'skill_level': 'all',
                'max_attendees': 15,
                'duration_hours': 2
            },
            # Table Tennis
            {
                'title': 'Ping Pong Tournament',
                'description': 'Indoor table tennis tournament. Single elimination format. All levels welcome!',
                'category': 'table_tennis',
                'skill_level': 'all',
                'max_attendees': 8,
                'duration_hours': 2
            },
        ]

        # Time slots for events
        time_slots = [
            (8, 0),   # 8:00 AM
            (10, 0),  # 10:00 AM
            (14, 0),  # 2:00 PM
            (17, 0),  # 5:00 PM
            (18, 30), # 6:30 PM
        ]

        created_events = []

        # Create upcoming events (next 4 weeks)
        for week in range(4):
            for day in range(7):
                # Create 2-3 events per day
                num_events = random.randint(2, 3)
                
                for _ in range(num_events):
                    template = random.choice(event_templates)
                    host = random.choice(users)
                    
                    # Calculate event date
                    event_date = timezone.now().date() + timedelta(weeks=week, days=day)
                    
                    # Skip if date is in the past
                    if event_date < timezone.now().date():
                        continue
                    
                    # Choose random time slot
                    hour, minute = random.choice(time_slots)
                    start_time = datetime.strptime(f"{hour}:{minute}", "%H:%M").time()
                    
                    # Calculate end time
                    duration = template['duration_hours']
                    end_datetime = datetime.combine(event_date, start_time) + timedelta(hours=duration)
                    end_time = end_datetime.time()
                    
                    # Create timestamp
                    event_timestamp = timezone.make_aware(
                        datetime.combine(event_date, end_time)
                    )
                    
                    # Create event
                    event = Events.objects.create(
                        title=template['title'],
                        description=template['description'],
                        host=host,
                        date=event_date,
                        start=start_time,
                        end=end_time,
                        timestamp=event_timestamp,
                        category=template['category'],
                        skill_level=template['skill_level'],
                        max_attendees=template['max_attendees']
                    )
                    
                    # Add host as attendee
                    event.attendees.add(host)
                    
                    # Add random attendees (30-70% capacity)
                    num_attendees = random.randint(
                        int(template['max_attendees'] * 0.3),
                        int(template['max_attendees'] * 0.7)
                    )
                    
                    available_users = [u for u in users if u != host]
                    attendees = random.sample(available_users, min(num_attendees, len(available_users)))
                    
                    for attendee in attendees:
                        event.attendees.add(attendee)
                    
                    created_events.append(event)

        self.stdout.write(self.style.SUCCESS(f"✓ Created {len(created_events)} upcoming events"))

        # Create some past events
        self.stdout.write("\nCreating past events...")
        past_event_count = 0
        for i in range(15):
            template = random.choice(event_templates)
            host = random.choice(users)
            
            # Past date (1-30 days ago)
            days_ago = random.randint(1, 30)
            event_date = timezone.now().date() - timedelta(days=days_ago)
            
            # Random time
            hour, minute = random.choice(time_slots)
            start_time = datetime.strptime(f"{hour}:{minute}", "%H:%M").time()
            
            duration = template['duration_hours']
            end_datetime = datetime.combine(event_date, start_time) + timedelta(hours=duration)
            end_time = end_datetime.time()
            
            event_timestamp = timezone.make_aware(
                datetime.combine(event_date, end_time)
            )
            
            event = Events.objects.create(
                title=template['title'],
                description=template['description'],
                host=host,
                date=event_date,
                start=start_time,
                end=end_time,
                timestamp=event_timestamp,
                category=template['category'],
                skill_level=template['skill_level'],
                max_attendees=template['max_attendees']
            )
            
            # Add attendees to past events
            event.attendees.add(host)
            num_attendees = random.randint(
                int(template['max_attendees'] * 0.5),
                template['max_attendees']
            )
            
            available_users = [u for u in users if u != host]
            attendees = random.sample(available_users, min(num_attendees, len(available_users)))
            
            for attendee in attendees:
                event.attendees.add(attendee)
            
            past_event_count += 1

        self.stdout.write(self.style.SUCCESS(f"✓ Created {past_event_count} past events"))

        self.stdout.write("\n" + "="*50)
        self.stdout.write("Creating Comments...")
        self.stdout.write("="*50)

        # Add comments to some events
        comment_templates = [
            "Looking forward to this!",
            "Count me in! This is going to be great.",
            "What should I bring?",
            "Is parking available nearby?",
            "Can't wait! See you all there.",
            "First time joining, excited to meet everyone!",
            "Will there be water stations?",
            "Great event! Thanks for organizing.",
            "What's the skill level needed?",
            "Is there a rain backup plan?",
            "Bringing a friend, hope that's okay!",
            "Thanks for putting this together!",
            "Perfect timing for me!",
            "I'll be there early to help set up.",
            "This is exactly what I was looking for!"
        ]

        comment_count = 0
        # Add comments to upcoming events
        for event in random.sample(created_events, min(30, len(created_events))):
            num_comments = random.randint(1, 5)
            
            for _ in range(num_comments):
                commenter = random.choice(users)
                comment_text = random.choice(comment_templates)
                
                EventComment.objects.create(
                    event=event,
                    author=commenter,
                    content=comment_text
                )
                comment_count += 1

        self.stdout.write(self.style.SUCCESS(f"✓ Created {comment_count} comments"))

        self.stdout.write("\n" + "="*50)
        self.stdout.write(self.style.SUCCESS("Demo Data Creation Complete!"))
        self.stdout.write("="*50)
        self.stdout.write(f"""
Summary:
- Users created: {len(users)}
- Upcoming events: {len(created_events)}
- Past events: {past_event_count}
- Comments: {comment_count}

Demo Login Credentials:
Username: sarah_runner (or any other demo username)
Password: demo1234

All demo users have the same password: demo1234
        """)
