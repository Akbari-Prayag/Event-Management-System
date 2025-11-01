# Event Management System API

<div align="center">

**A comprehensive Django REST Framework API for managing events, RSVPs, and reviews**

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![Django](https://img.shields.io/badge/Django-4.2.7-green.svg)](https://www.djangoproject.com/)
[![DRF](https://img.shields.io/badge/DRF-3.14.0-red.svg)](https://www.django-rest-framework.org/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

**Built by [Akbari Prayag](https://github.com/Akbari-Prayag)**

</div>

---

## 📋 Overview

A robust and scalable Event Management System built with Django REST Framework. This API enables users to create events, manage RSVPs, leave reviews, and handle event invitations with comprehensive authentication and permission controls.

### Key Features

- ✅ **Event Management** - Create, read, update, and delete events with organizer permissions
- ✅ **RSVP System** - Users can RSVP to events with status options (Going, Maybe, Not Going)
- ✅ **Review System** - Rate and review events with ratings (1-5 stars)
- ✅ **JWT Authentication** - Secure API access using JSON Web Tokens
- ✅ **Custom Permissions** - Granular access control for private events and organizer actions
- ✅ **Pagination & Filtering** - Efficient data retrieval with search and filter capabilities
- ✅ **Async Email Notifications** - Background task processing with Celery for event updates
- ✅ **Comprehensive Testing** - Unit tests covering all major API endpoints
- ✅ **Production Ready** - Configured for deployment with WhiteNoise and Gunicorn

---

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- Git

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/Akbari-Prayag/Event-Management-System.git
   cd Event-Management-System
   ```

2. **Create and activate virtual environment**
   
   **Windows:**
   ```bash
   python -m venv venv
   venv\Scripts\activate
   ```
   
   **Linux/Mac:**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run migrations**
   ```bash
   python manage.py migrate
   ```

5. **Create superuser (optional)**
   ```bash
   python manage.py createsuperuser
   ```

6. **Start the development server**
   ```bash
   python manage.py runserver
   ```

7. **Access the API**
   - API Root: `http://localhost:8000/api/`
   - Admin Panel: `http://localhost:8000/admin/`
   - API Documentation: `http://localhost:8000/api/events/`

---

## 📚 API Endpoints

### Authentication

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/token/` | Get JWT access and refresh tokens |
| POST | `/api/token/refresh/` | Refresh access token |

### Events

| Method | Endpoint | Auth Required | Description |
|--------|----------|---------------|-------------|
| GET | `/api/events/` | No | List all public events (paginated) |
| GET | `/api/events/{id}/` | No | Get event details |
| POST | `/api/events/` | Yes | Create a new event |
| PUT/PATCH | `/api/events/{id}/` | Yes (Organizer) | Update event |
| DELETE | `/api/events/{id}/` | Yes (Organizer) | Delete event |

### RSVP

| Method | Endpoint | Auth Required | Description |
|--------|----------|---------------|-------------|
| POST | `/api/events/{id}/rsvp/` | Yes | RSVP to an event |
| PATCH | `/api/events/{id}/rsvp/{user_id}/` | Yes | Update RSVP status |

### Reviews

| Method | Endpoint | Auth Required | Description |
|--------|----------|---------------|-------------|
| GET | `/api/events/{id}/reviews/` | No | List all reviews for an event |
| POST | `/api/events/{id}/reviews/` | Yes | Add a review |

### Additional Features

- **Search**: `?search=keyword` - Search events by title, description, location
- **Filter**: `?location=city&organizer=id&is_public=true`
- **Ordering**: `?ordering=-created_at` - Sort by creation date, start time, etc.
- **Pagination**: Automatically paginated (20 items per page)

---

## 🔐 Authentication Example

```bash
# 1. Get JWT Token
curl -X POST http://localhost:8000/api/token/ \
  -H "Content-Type: application/json" \
  -d '{"username": "your_username", "password": "your_password"}'

# Response:
# {
#   "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
#   "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
# }

# 2. Use Token in Requests
curl -X GET http://localhost:8000/api/events/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

---

## 🧪 Testing

Run the test suite:

```bash
python manage.py test events
```

The test suite includes:
- Event CRUD operations
- Permission enforcement
- Private event access control
- RSVP functionality
- Review system
- Search and filtering

---

## 📁 Project Structure

```
Event-Management-System/
├── event_management/          # Django project settings
│   ├── settings.py          # Configuration and settings
│   ├── urls.py             # Main URL routing
│   ├── celery.py           # Celery task configuration
│   └── wsgi.py             # WSGI configuration
├── events/                  # Main application
│   ├── models.py           # Database models
│   ├── serializers.py     # DRF serializers
│   ├── views.py           # API views and ViewSets
│   ├── permissions.py     # Custom permission classes
│   ├── tasks.py           # Celery async tasks
│   ├── admin.py           # Django admin configuration
│   └── tests.py            # Unit tests
├── manage.py              # Django management script
├── requirements.txt       # Python dependencies
├── Procfile              # Deployment configuration
└── README.md            # This file
```

---

## 🛠 Tech Stack

- **Backend Framework**: Django 4.2.7
- **API Framework**: Django REST Framework 3.14.0
- **Authentication**: JWT (djangorestframework-simplejwt)
- **Task Queue**: Celery 5.3.4 with Redis
- **Database**: SQLite (development) / PostgreSQL (production)
- **Static Files**: WhiteNoise
- **Production Server**: Gunicorn

---

## 🔧 Configuration

### Environment Variables

Create a `.env` file (optional for development):

```env
SECRET_KEY=your-secret-key-here
DEBUG=True
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0
```

### Celery Setup (Optional)

For async email notifications:

1. **Install and start Redis**
   ```bash
   # Using Docker
   docker run -d -p 6379:6379 redis
   ```

2. **Start Celery worker**
   ```bash
   celery -A event_management worker --loglevel=info
   ```

---

## 🚢 Deployment

This project is configured for easy deployment on platforms like:

- **Railway** (Recommended) - [Deployment Guide](DEPLOYMENT.md)
- **Render** - [Deployment Guide](DEPLOYMENT.md)
- **Heroku** - [Deployment Guide](DEPLOYMENT.md)

See [DEPLOYMENT.md](DEPLOYMENT.md) for detailed deployment instructions.

---

## 📝 API Usage Examples

### Create an Event

```bash
curl -X POST http://localhost:8000/api/events/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Django Workshop",
    "description": "Learn Django REST Framework",
    "location": "Online",
    "start_time": "2024-12-31T10:00:00Z",
    "end_time": "2024-12-31T12:00:00Z",
    "is_public": true
  }'
```

### RSVP to an Event

```bash
curl -X POST http://localhost:8000/api/events/1/rsvp/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"status": "Going"}'
```

### Add a Review

```bash
curl -X POST http://localhost:8000/api/events/1/reviews/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "rating": 5,
    "comment": "Great event!"
  }'
```

---

## 📖 Documentation

- [Quick Start Guide](QUICKSTART.md) - Get up and running in 5 minutes
- [How to Run](HOW_TO_RUN.md) - Detailed setup instructions
- [Deployment Guide](DEPLOYMENT.md) - Production deployment instructions
- [Implementation Details](IMPLEMENTATION.md) - Technical documentation

---

## 🤝 Contributing

This is a portfolio project. For suggestions or improvements, feel free to open an issue or submit a pull request.

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 👨‍💻 Author

**Akbari Prayag**

- GitHub: [@Akbari-Prayag](https://github.com/Akbari-Prayag)
- Project Link: [Event Management System](https://github.com/Akbari-Prayag/Event-Management-System)

---

## ✨ Features Highlights

### Custom Permissions
- Only event organizers can edit or delete their events
- Private events are only accessible to invited users
- Granular permission system for secure API access

### Advanced Filtering
- Search events by title, description, location, or organizer
- Filter by location, organizer, and visibility status
- Sort by creation date, start time, or title

### Background Processing
- Asynchronous email notifications using Celery
- Non-blocking task execution
- Scalable architecture for production use

---

## 🎯 Project Goals

This project demonstrates:

- RESTful API design principles
- Django REST Framework best practices
- JWT authentication implementation
- Custom permission classes
- Database relationships and migrations
- Async task processing with Celery
- Comprehensive test coverage
- Production-ready deployment configuration

---

## 📞 Contact

For questions or inquiries, please reach out through GitHub or email.

**Happy Coding! 🚀**
