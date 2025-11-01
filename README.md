# Event Management System

A comprehensive Django REST Framework API for managing events, RSVPs, and reviews with JWT authentication, custom permissions, and asynchronous email notifications using Celery.

## Features

- **Event Management**: Create, read, update, and delete events
- **RSVP System**: Users can RSVP to events with status (Going, Maybe, Not Going)
- **Review System**: Users can leave reviews and ratings for events
- **JWT Authentication**: Secure API access using JSON Web Tokens
- **Custom Permissions**: 
  - Only organizers can edit/delete their events
  - Private events accessible only to invited users
- **Pagination**: All list endpoints are paginated
- **Filtering & Search**: Filter events by organizer, location, and search by title/description
- **Asynchronous Tasks**: Email notifications using Celery for:
  - New event creation
  - Event updates
  - RSVP notifications
  - Review notifications
- **Unit Tests**: Comprehensive test coverage for API endpoints

## Tech Stack

- **Backend**: Django 4.2.7, Django REST Framework 3.14.0
- **Authentication**: JWT (djangorestframework-simplejwt)
- **Task Queue**: Celery 5.3.4 with Redis
- **Database**: SQLite (default, can be configured for PostgreSQL/MySQL)
- **Filtering**: django-filter

## Project Structure

```
Event/
├── event_management/          # Django project settings
│   ├── __init__.py           # Celery initialization
│   ├── settings.py           # Django settings
│   ├── urls.py              # Main URL configuration
│   ├── wsgi.py              # WSGI config
│   └── celery.py            # Celery configuration
├── events/                   # Events app
│   ├── models.py            # UserProfile, Event, RSVP, Review models
│   ├── serializers.py       # DRF serializers
│   ├── views.py             # ViewSets and API endpoints
│   ├── permissions.py       # Custom permission classes
│   ├── tasks.py             # Celery async tasks
│   ├── signals.py           # Django signals (auto-create profiles)
│   ├── urls.py              # App URL routing
│   ├── admin.py             # Django admin configuration
│   └── tests.py             # Unit tests
├── manage.py                # Django management script
├── requirements.txt         # Python dependencies
└── README.md               # This file
```

## Quick Start (Windows)

**Activate virtual environment and run server:**

```bash
# Option 1: Use the batch file
run_server.bat

# Option 2: Manual activation
venv\Scripts\activate
python manage.py runserver
```

**For Linux/Mac:**
```bash
source venv/bin/activate
python manage.py runserver
```

## Installation & Setup

### Prerequisites

- Python 3.8 or higher
- Redis (for Celery task queue)
- Virtual environment (recommended)

### Step 1: Clone and Setup Virtual Environment

```bash
# Navigate to project directory
cd Event

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

### Step 2: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 3: Setup Environment Variables

Create a `.env` file in the project root (or use default values):

```env
SECRET_KEY=your-secret-key-here
DEBUG=True
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
DEFAULT_FROM_EMAIL=noreply@eventmanagement.com
```

**Note**: For Gmail, you'll need to create an App Password. For development, the console email backend is used by default.

### Step 4: Run Migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

### Step 5: Create Superuser (Optional)

```bash
python manage.py createsuperuser
```

### Step 6: Start Redis (Required for Celery)

**On Windows** (using WSL or Docker):
```bash
# Using Docker:
docker run -d -p 6379:6379 redis

# Or install Redis for Windows
```

**On macOS** (using Homebrew):
```bash
brew install redis
brew services start redis
```

**On Linux**:
```bash
sudo apt-get install redis-server
sudo systemctl start redis
```

### Step 7: Start Development Server

```bash
# Terminal 1: Django development server
python manage.py runserver

# Terminal 2: Celery worker (required for async email tasks)
celery -A event_management worker --loglevel=info

# Terminal 3: Celery beat (if you need scheduled tasks, optional)
celery -A event_management beat --loglevel=info
```

The API will be available at `http://localhost:8000/api/`

## API Endpoints

### Authentication

- **POST** `/api/token/` - Get JWT access and refresh tokens
  ```json
  {
    "username": "your_username",
    "password": "your_password"
  }
  ```

- **POST** `/api/token/refresh/` - Refresh access token
  ```json
  {
    "refresh": "your_refresh_token"
  }
  ```

### Events

- **POST** `/api/events/` - Create a new event (Authenticated)
  ```json
  {
    "title": "Tech Meetup",
    "description": "Monthly tech meetup",
    "location": "San Francisco, CA",
    "start_time": "2024-12-31T18:00:00Z",
    "end_time": "2024-12-31T20:00:00Z",
    "is_public": true
  }
  ```

- **GET** `/api/events/` - List all public events (Paginated)
  - Query params: `?search=keyword`, `?location=SF`, `?organizer=1`, `?ordering=-created_at`

- **GET** `/api/events/{id}/` - Get event details

- **PUT/PATCH** `/api/events/{id}/` - Update event (Organizer only)

- **DELETE** `/api/events/{id}/` - Delete event (Organizer only)

### RSVP

- **POST** `/api/events/{event_id}/rsvp/` - RSVP to an event
  ```json
  {
    "status": "Going"
  }
  ```
  Status options: "Going", "Maybe", "Not Going"

- **PATCH** `/api/events/{event_id}/rsvp/{user_id}/` - Update RSVP status
  ```json
  {
    "status": "Maybe"
  }
  ```

### Reviews

- **POST** `/api/events/{event_id}/reviews/` - Add a review
  ```json
  {
    "rating": 5,
    "comment": "Great event!"
  }
  ```
  Rating must be between 1 and 5.

- **GET** `/api/events/{event_id}/list_reviews/` - List all reviews for an event

### Invitations (Private Events)

- **POST** `/api/events/{event_id}/invite_user/` - Invite user to private event (Organizer only)
  ```json
  {
    "user_id": 2
  }
  ```

## API Usage Examples

### Using cURL

```bash
# Get JWT token
curl -X POST http://localhost:8000/api/token/ \
  -H "Content-Type: application/json" \
  -d '{"username": "user1", "password": "pass123"}'

# Create event (replace YOUR_ACCESS_TOKEN)
curl -X POST http://localhost:8000/api/events/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Django Workshop",
    "description": "Learn Django REST Framework",
    "location": "Online",
    "start_time": "2024-12-31T10:00:00Z",
    "end_time": "2024-12-31T12:00:00Z",
    "is_public": true
  }'

# RSVP to event
curl -X POST http://localhost:8000/api/events/1/rsvp/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"status": "Going"}'
```

### Using Python requests

```python
import requests

# Get token
response = requests.post('http://localhost:8000/api/token/', json={
    'username': 'user1',
    'password': 'pass123'
})
token = response.json()['access']

# Create event
headers = {'Authorization': f'Bearer {token}'}
event_data = {
    'title': 'Python Meetup',
    'description': 'Monthly Python meetup',
    'location': 'San Francisco',
    'start_time': '2024-12-31T18:00:00Z',
    'end_time': '2024-12-31T20:00:00Z',
    'is_public': True
}
response = requests.post('http://localhost:8000/api/events/', 
                        json=event_data, headers=headers)
print(response.json())
```

## Testing

Run the test suite:

```bash
python manage.py test events
```

The test suite includes:
- Event CRUD operations
- Permission tests (organizer-only actions)
- Private event access control
- RSVP functionality
- Review system
- Search and filtering

## Key Features Explained

### Custom Permissions

1. **IsOrganizerOrReadOnly**: Only event organizers can edit or delete their events
2. **IsPrivateEventAllowed**: Private events are only accessible to:
   - The organizer
   - Invited users
   - Users who have RSVP'd (indirect access)

### Pagination

All list endpoints return paginated results with 20 items per page. Response format:
```json
{
  "count": 100,
  "next": "http://localhost:8000/api/events/?page=2",
  "previous": null,
  "results": [...]
}
```

### Filtering & Search

- **Filter by**: `?organizer=1`, `?location=SF`, `?is_public=true`
- **Search**: `?search=python` (searches in title, description, location, organizer username)
- **Ordering**: `?ordering=-created_at` (newest first)

### Async Email Notifications

Celery tasks automatically send emails when:
- A new event is created (to invited users)
- An event is updated (to all RSVP'd users)
- Someone RSVPs (to the organizer)
- A review is posted (to the organizer)

## Database Models

### UserProfile
- Extends Django User model
- Fields: `full_name`, `bio`, `location`, `profile_picture`

### Event
- Fields: `title`, `description`, `organizer`, `location`, `start_time`, `end_time`, `is_public`
- Auto-created fields: `created_at`, `updated_at`

### RSVP
- Fields: `event`, `user`, `status` (Going/Maybe/Not Going)
- Unique constraint: One RSVP per user per event

### Review
- Fields: `event`, `user`, `rating` (1-5), `comment`
- Unique constraint: One review per user per event

### EventInvitation
- Tracks invitations for private events
- Fields: `event`, `user`, `invited_by`

## Production Considerations

1. **SECRET_KEY**: Change to a secure random key
2. **DEBUG**: Set to `False` in production
3. **ALLOWED_HOSTS**: Configure properly for your domain
4. **Database**: Use PostgreSQL or MySQL instead of SQLite
5. **Static Files**: Configure static file serving
6. **Email Backend**: Use proper SMTP or email service (SendGrid, AWS SES)
7. **CORS**: Configure allowed origins properly
8. **Security**: Use HTTPS, configure security middleware

## Troubleshooting

### Celery not working
- Ensure Redis is running: `redis-cli ping` should return `PONG`
- Check Celery worker logs for errors
- Verify CELERY_BROKER_URL in settings

### Email not sending
- Check EMAIL_* settings in `.env`
- For Gmail: Use App Password, not regular password
- Check Celery worker is running
- Verify console output (if using console backend)

### Permission denied errors
- Ensure you're authenticated (include Bearer token)
- Verify you're the organizer for edit/delete operations
- Check event is_public status for access

## License

This project is created for educational purposes as an assignment submission.

## Contributing

This is an assignment project. For learning purposes, feel free to fork and experiment!

## Contact

For questions or issues, please refer to the assignment guidelines or contact your instructor.

