# How to Run the Project

## 🚀 Quick Start (Windows)

### Step 1: Activate Virtual Environment

Open PowerShell or Command Prompt in the project folder and run:

```bash
venv\Scripts\activate
```

You should see `(venv)` at the beginning of your prompt.

### Step 2: Start the Server

**Option A - Use the batch file (Easiest):**
```bash
run_server.bat
```

**Option B - Manual command:**
```bash
python manage.py runserver
```

### Step 3: Access the API

Open your browser or API client:
- API Root: `http://localhost:8000/api/`
- Admin Panel: `http://localhost:8000/admin/`
- API Events: `http://localhost:8000/api/events/`

## 📝 Detailed Steps

### First Time Setup

1. **Navigate to project folder:**
   ```bash
   cd C:\Users\praya\Desktop\Event
   ```

2. **Activate virtual environment:**
   ```bash
   venv\Scripts\activate
   ```

3. **Install dependencies (if not already done):**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run migrations:**
   ```bash
   python manage.py migrate
   ```

5. **Create superuser (optional):**
   ```bash
   python manage.py createsuperuser
   ```

6. **Start server:**
   ```bash
   python manage.py runserver
   ```

## 🔑 Getting JWT Token

1. **Create a user** (via admin or Django shell):
   ```bash
   python manage.py shell
   >>> from django.contrib.auth.models import User
   >>> User.objects.create_user('testuser', 'test@example.com', 'testpass123')
   ```

2. **Get JWT token:**
   ```bash
   POST http://localhost:8000/api/token/
   {
     "username": "testuser",
     "password": "testpass123"
   }
   ```

3. **Use token in API requests:**
   ```
   Authorization: Bearer YOUR_ACCESS_TOKEN
   ```

## 🧪 Running Tests

```bash
python manage.py test events
```

## 🐛 Troubleshooting

### Error: "No module named 'django'"

**Solution:** Activate the virtual environment first:
```bash
venv\Scripts\activate
```

### Error: "Port 8000 already in use"

**Solution:** Use a different port:
```bash
python manage.py runserver 8080
```

### Error: "Database is locked"

**Solution:** Close any database connections and try again, or delete `db.sqlite3` and run migrations again.

### Server won't start

1. Make sure virtual environment is activated
2. Check all dependencies are installed: `pip install -r requirements.txt`
3. Run Django check: `python manage.py check`

## 📚 Next Steps

- Read [README.md](README.md) for full documentation
- Check [DEPLOYMENT.md](DEPLOYMENT.md) for production deployment
- See [QUICKSTART.md](QUICKSTART.md) for quick reference

## ⚙️ Development Server Commands

```bash
# Run migrations
python manage.py migrate

# Create migrations
python manage.py makemigrations

# Collect static files (for production)
python manage.py collectstatic

# Create superuser
python manage.py createsuperuser

# Run Django shell
python manage.py shell

# Check for issues
python manage.py check
```

## 🔄 Running Celery (For Email Notifications)

You need Redis running first:

1. **Start Redis:**
   ```bash
   # Using Docker (recommended)
   docker run -d -p 6379:6379 redis
   
   # Or install Redis locally
   ```

2. **Start Celery worker (in new terminal):**
   ```bash
   venv\Scripts\activate
   celery -A event_management worker --loglevel=info
   ```

Now email notifications will work asynchronously!

