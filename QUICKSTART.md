# Quick Start Guide

## Fast Setup (5 minutes)

### 1. Install Dependencies

```bash
# Activate virtual environment (if not already activated)
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install packages
pip install -r requirements.txt
```

### 2. Setup Database

```bash
python manage.py makemigrations
python manage.py migrate
```

### 3. Create Superuser (Optional)

```bash
python manage.py createsuperuser
```

### 4. Start Services

You need **3 terminal windows**:

**Terminal 1 - Django Server:**
```bash
python manage.py runserver
```

**Terminal 2 - Redis (if not running as service):**
```bash
# Windows (Docker):
docker run -d -p 6379:6379 redis

# macOS:
brew services start redis

# Linux:
sudo systemctl start redis
```

**Terminal 3 - Celery Worker:**
```bash
celery -A event_management worker --loglevel=info
```

### 5. Test the API

Open your browser or use a tool like Postman:

**Get JWT Token:**
```bash
POST http://localhost:8000/api/token/
{
  "username": "your_username",
  "password": "your_password"
}
```

**List Events:**
```bash
GET http://localhost:8000/api/events/
```

**Create Event (with token):**
```bash
POST http://localhost:8000/api/events/
Authorization: Bearer YOUR_ACCESS_TOKEN
{
  "title": "My Event",
  "description": "Event description",
  "location": "New York",
  "start_time": "2024-12-31T10:00:00Z",
  "end_time": "2024-12-31T12:00:00Z",
  "is_public": true
}
```

## Common Issues

### Redis Connection Error
- Make sure Redis is running
- Check: `redis-cli ping` should return `PONG`
- Verify `CELERY_BROKER_URL` in settings

### Celery Not Sending Emails
- Ensure Celery worker is running
- Check worker logs for errors
- Verify email settings in `.env`

### Permission Denied Errors
- Check you're sending the Bearer token
- Verify user is authenticated
- For edit/delete: ensure you're the organizer

## API Endpoints Summary

| Method | Endpoint | Auth Required | Description |
|--------|----------|---------------|-------------|
| POST | `/api/token/` | No | Get JWT token |
| POST | `/api/events/` | Yes | Create event |
| GET | `/api/events/` | No | List events |
| GET | `/api/events/{id}/` | No | Event details |
| PATCH | `/api/events/{id}/` | Yes | Update event (organizer) |
| DELETE | `/api/events/{id}/` | Yes | Delete event (organizer) |
| POST | `/api/events/{id}/rsvp/` | Yes | RSVP to event |
| PATCH | `/api/events/{id}/rsvp/{user_id}/` | Yes | Update RSVP |
| POST | `/api/events/{id}/reviews/` | Yes | Add review |
| GET | `/api/events/{id}/reviews/` | No | List reviews |

## Next Steps

- Read the full [README.md](README.md) for detailed documentation
- Run tests: `python manage.py test events`
- Explore the Django admin: `http://localhost:8000/admin/`

