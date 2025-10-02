# Sports Meets - CS50w Capstone Project

## Overview

Sports Meets is a dynamic web application designed to connect sports enthusiasts in local communities. The platform addresses the common problem of finding and organizing casual sports events by providing a streamlined, user-friendly interface that eliminates the clutter and complexity found in general community event platforms.

The application allows users to create, discover, and join sports events in their area, fostering an active and engaged sports community. Unlike other community platforms that mix various types of events and content, Sports Meets focuses exclusively on sports activities, making it easier for athletes and sports enthusiasts to find exactly what they're looking for.

## Distinctiveness and Complexity

This project satisfies the distinctiveness and complexity requirements for the CS50W capstone project in several significant ways:

### Distinctiveness

Sports Meets is fundamentally different from the other projects in the CS50W course:

1. **Not a Social Network**: Unlike Project 4 (Network), Sports Meets is not focused on social interactions, posts, or following mechanisms. Instead, it's an event management platform specifically for organizing real-world sports activities.

2. **Not E-Commerce**: Unlike Project 2 (Commerce), this application doesn't involve buying, selling, or auctioning items. There are no financial transactions, bidding systems, or product listings.

3. **Not Email or Wiki**: The application serves a completely different purpose than Projects 3 (Mail) and 1 (Wiki), focusing on event coordination rather than communication or information management.

4. **Unique Domain Focus**: Sports Meets addresses the specific need of organizing in-person sports activities, a domain not covered in any course project.

### Complexity

The application demonstrates significant technical complexity through:

1. **Real-Time Event Management**: 
   - Events automatically transition from "upcoming" to "past" based on their timestamp
   - Dynamic status updates (full, cancelled, spots available) without page refresh
   - Timezone-aware datetime handling using pytz

2. **Multi-Model Relationships**:
   - Complex many-to-many relationships between Users and Events
   - Foreign key relationships for event hosting
   - Comment system with nested relationships

3. **Dynamic Filtering and Search**:
   - Multi-parameter event filtering (sport, skill level, date range)
   - Full-text search across multiple fields
   - Pagination with filter persistence

4. **Progressive Enhancement**:
   - JavaScript-powered interactions with fallback functionality
   - AJAX requests for seamless user experience
   - Real-time form validation

5. **Comprehensive User System**:
   - Extended user profiles with additional fields
   - Profile pictures and bio information
   - User statistics and event history

6. **Security Features**:
   - CSRF protection on all forms
   - User authentication requirements for sensitive actions
   - Input validation and sanitization

## Features

### Core Features

- **Event Creation**: Users can create detailed sports events with date, time, skill level, and participant limits
- **Event Discovery**: Browse upcoming events with advanced filtering options
- **Attendance Management**: Join or leave events with real-time capacity updates
- **User Profiles**: Customizable profiles showing hosted and attended events
- **Comments System**: Discussion threads for each event
- **Responsive Design**: Mobile-first approach ensuring usability across all devices

### Additional Features

- **Event Images**: Upload custom images for events
- **Skill Level Matching**: Filter events by skill requirements
- **Event History**: View past events and participation history
- **Event Cancellation**: Hosts can cancel events with notifications
- **Search Functionality**: Find events by title, or description
- **Pagination**: Efficient browsing of large event lists
- **Real-time Validation**: Immediate feedback on form inputs

## File Structure

```
capstone/
├── capstone/               # Main project directory
│   ├── settings.py        # Django settings with timezone, and so on
│   ├── urls.py            # Project-level URL routing
│   ├── wsgi.py            # WSGI configuration for deployment
│   └── asgi.py            # ASGI configuration for async support
│
├── sports/                # Main application directory
│   ├── models.py          # Database models (User, Events, EventComment)
│   ├── views.py           # View functions and business logic
│   ├── forms.py           # Django forms for user input
│   ├── urls.py            # Application-level URL patterns
│   ├── admin.py           # Admin interface configuration
│   ├── tests.py           # Application-specific tests
│   ├── apps.py            # Application configuration
│   │
│   ├── templatetags/      # Custom Django template tags
│   │   └── pagination_tags.py # Tags for handling pagination URLs
│   │
│   ├── management/        # Custom management commands
│   │   └── commands/
│   │       └── populate_demo.py # Script to populate DB with demo data
│   │
│   ├── static/sports/     # Static files
│   │   ├── styles.css     # Custom CSS styles
│   │   └── scripts.js     # JavaScript for dynamic functionality
│   │
│   ├── templates/sports/  # HTML templates
│   │   ├── layout.html    # Base template with navigation
│   │   ├── index.html     # Homepage with event listings
│   │   ├── event_detail.html  # Single event view
│   │   ├── create_event.html  # Event creation form
│   │   ├── edit_event.html    # Event editing form
│   │   ├── login.html     # User login page
│   │   ├── register.html  # User registration page
│   │   ├── profile.html   # User profile page
│   │   ├── edit_profile.html  # Profile editing page
│   │   ├── my_events.html     # User's events dashboard
│   │   └── past_events.html   # Historical events view
│   │
│   └── migrations/        # Database migrations
│
├── media/                 # User-uploaded files
│   ├── events/           # Event images
│   └── profile_pics/     # User profile pictures
│
├── requirements.txt       # Python dependencies
├── .env.template         # Environment variables template
├── .gitignore           # Git ignore file
└── manage.py            # Django management script
```

## Models

### User Model
- Extends Django's AbstractUser
- Additional fields: bio, favorite_sports, profile_picture
- Methods for getting event statistics

### Events Model
- Comprehensive event information including title, description, date, time
- Many-to-many relationship with attendees
- Foreign key relationship with host
- Dynamic properties for event status (is_full, is_past, spots_available)

### EventComment Model
- Comments linked to events and users
- Timestamps for creation and updates
- Ordered by most recent first

## Installation and Setup

1. **Create a virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**:
   ```bash
   cp .env.template .env
   # Edit .env file with your configuration
   ```

4. **Run migrations**:
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

5. **Create a superuser** (optional, for admin access):
   ```bash
   python manage.py createsuperuser
   ```

6. **Populate with Demo Data** (optional):
   To fill the database with sample users, events, and comments for demonstration purposes, run the following command. This is highly recommended for seeing the app's features in action.
   ```bash
   python manage.py populate_demo
   ```
   To clear old demo data before populating, use the `--clear` flag:
   ```bash
   python manage.py populate_demo --clear
   ```

7. **Run the development server**:
   ```bash
   python manage.py runserver
   ```

8. **Access the application**:
   - Open your browser and navigate to `http://localhost:8000`
   - Register a new account or log in with a demo account (e.g., username: `sarah_runner`, password: `demo1234`)

## Usage Guide

### Running Tests

The project includes a comprehensive test suite to ensure code quality and prevent regressions. To run the tests, execute the following command from the project root:

```bash
python manage.py test sports
```

This will discover and run all tests within the `sports` application, providing a summary of the results.


### Creating an Event
1. Login to your account
2. Click "Create Event" in the navigation
3. Fill in event details including sport type, and skill level.
4. Set participant limits and upload an optional image.
5. Submit the form to create your event.

### Joining an Event
1. Browse events on the homepage
2. Use filters to find events matching your interests
3. Click on an event to view details
4. Click "Join Event" if spots are available
5. Add comments to discuss with other participants

### Managing Your Events
1. Go to "My Events" to see your hosted and attending events
2. Edit or cancel events you're hosting
3. Leave events you're attending if plans change
4. View your event history and statistics

## Technologies Used

- **Backend**: Django 5.2.7 (Python web framework)
- **Frontend**: Bootstrap 5.3, JavaScript (ES6+)
- **Database**: SQLite (development), PostgreSQL-ready
- **Authentication**: Django's built-in authentication system
- **Styling**: Custom CSS with Bootstrap components
- **Icons**: Bootstrap Icons library

## Mobile Responsiveness

The application is fully responsive and optimized for mobile devices:
- Responsive navigation with hamburger menu
- Touch-friendly interface elements
- Optimized card layouts for small screens
- Mobile-optimized forms and buttons
- Adaptive image sizing

## Security Considerations

- CSRF protection on all forms
- Password hashing using Django's authentication
- Input validation and sanitization
- Secure session management
- Environment variable protection for sensitive data
- SQL injection prevention through Django ORM
