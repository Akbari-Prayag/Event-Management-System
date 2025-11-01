# Deployment Guide

## Important Note

**GitHub Pages is for static websites only** and cannot run Django applications. Django requires a Python server and database, which GitHub Pages doesn't provide.

For Django deployment, you need a platform that supports:
- Python runtime
- Database (PostgreSQL/MySQL recommended for production)
- Persistent file storage
- Background tasks (Celery/Redis)

## Recommended Deployment Platforms

### 1. Railway (Recommended - Free Tier Available)

Railway is the easiest and fastest way to deploy Django apps.

**Steps:**

1. **Create Railway account**: Visit [railway.app](https://railway.app)

2. **Install Railway CLI**:
   ```bash
   npm install -g @railway/cli
   ```

3. **Login**:
   ```bash
   railway login
   ```

4. **Initialize project**:
   ```bash
   railway init
   ```

5. **Add PostgreSQL database**:
   - In Railway dashboard, click "New" → "Database" → "PostgreSQL"
   - Railway will automatically add database connection variables

6. **Configure environment variables** in Railway dashboard:
   ```
   SECRET_KEY=your-secret-key
   DEBUG=False
   ALLOWED_HOSTS=*.railway.app,your-domain.com
   DATABASE_URL=railway-provides-this
   CELERY_BROKER_URL=redis://your-redis-url
   CELERY_RESULT_BACKEND=redis://your-redis-url
   ```

7. **Deploy**:
   ```bash
   railway up
   ```

### 2. Render (Free Tier Available)

1. **Sign up**: Visit [render.com](https://render.com)

2. **Connect GitHub repository**

3. **Create new Web Service**:
   - Connect your GitHub repo
   - Build command: `pip install -r requirements.txt && python manage.py migrate`
   - Start command: `gunicorn event_management.wsgi:application`

4. **Create PostgreSQL database** (separate service)

5. **Add Redis** (for Celery - separate service)

6. **Set environment variables** in Render dashboard

7. **Deploy** (automatic on git push)

### 3. Heroku (Paid, but has free alternatives)

1. **Install Heroku CLI**: [devcenter.heroku.com/articles/heroku-cli](https://devcenter.heroku.com/articles/heroku-cli)

2. **Login**:
   ```bash
   heroku login
   ```

3. **Create app**:
   ```bash
   heroku create your-app-name
   ```

4. **Add PostgreSQL**:
   ```bash
   heroku addons:create heroku-postgresql:hobby-dev
   ```

5. **Add Redis**:
   ```bash
   heroku addons:create heroku-redis:hobby-dev
   ```

6. **Set config vars**:
   ```bash
   heroku config:set SECRET_KEY=your-secret-key
   heroku config:set DEBUG=False
   ```

7. **Deploy**:
   ```bash
   git push heroku main
   ```

### 4. PythonAnywhere (Free Tier for Learning)

1. **Sign up**: [www.pythonanywhere.com](https://www.pythonanywhere.com)

2. **Upload files** via web interface or git

3. **Configure web app** in dashboard

4. **Set up database** and environment variables

5. **Reload** web app

## Pre-Deployment Checklist

### 1. Update settings.py for Production

Create `event_management/settings_production.py`:

```python
from .settings import *
import os

DEBUG = False
ALLOWED_HOSTS = ['your-domain.com', '*.railway.app']

# Use environment variable for secret key
SECRET_KEY = os.environ.get('SECRET_KEY')

# Database (PostgreSQL recommended)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('DB_NAME'),
        'USER': os.environ.get('DB_USER'),
        'PASSWORD': os.environ.get('DB_PASSWORD'),
        'HOST': os.environ.get('DB_HOST'),
        'PORT': os.environ.get('DB_PORT', '5432'),
    }
}

# Static files
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATIC_URL = '/static/'

# Media files (use cloud storage in production)
# Consider using AWS S3, Cloudinary, etc.

# Security settings
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
```

### 2. Add Gunicorn for Production Server

Add to `requirements.txt`:
```
gunicorn==21.2.0
psycopg2-binary==2.9.9  # For PostgreSQL
whitenoise==6.6.0  # For serving static files
```

### 3. Create Procfile (for Heroku/Railway)

Create `Procfile`:
```
web: gunicorn event_management.wsgi:application --bind 0.0.0.0:$PORT
worker: celery -A event_management worker --loglevel=info
```

### 4. Create runtime.txt (optional)

Create `runtime.txt`:
```
python-3.11.0
```

### 5. Update .gitignore

Ensure sensitive files are ignored:
```
.env
*.log
db.sqlite3
__pycache__/
*.pyc
```

## Deployment Steps for Railway (Example)

1. **Prepare project**:
   ```bash
   # Install production dependencies
   pip install gunicorn psycopg2-binary whitenoise
   pip freeze > requirements.txt
   ```

2. **Update settings** for production environment variables

3. **Create Procfile**:
   ```
   web: python manage.py migrate && gunicorn event_management.wsgi:application
   worker: celery -A event_management worker --loglevel=info
   ```

4. **Initialize Railway**:
   ```bash
   railway init
   ```

5. **Add services**:
   - PostgreSQL database
   - Redis instance

6. **Set environment variables**:
   ```bash
   railway variables set SECRET_KEY=your-secret-key
   railway variables set DEBUG=False
   ```

7. **Deploy**:
   ```bash
   railway up
   ```

## Setting up Celery in Production

For background tasks, you need:

1. **Redis instance** (provided by platform or external)
2. **Worker process** running:
   ```
   celery -A event_management worker --loglevel=info
   ```
3. **Monitor** (optional):
   ```
   celery -A event_management flower  # Web-based monitoring
   ```

## Static Files in Production

For production, use WhiteNoise or cloud storage:

### WhiteNoise (Simple)
```python
# settings.py
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  # Add this
    # ... other middleware
]

STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
```

Run:
```bash
python manage.py collectstatic
```

## Database Migrations in Production

Always run migrations as part of deployment:

```bash
python manage.py migrate
```

Or include in your deployment script/Procfile.

## Monitoring & Logs

- **Railway**: Built-in logs dashboard
- **Render**: Logs in dashboard
- **Heroku**: `heroku logs --tail`

## Troubleshooting

### Database Connection Issues
- Verify database credentials
- Check ALLOWED_HOSTS includes your domain
- Ensure database is accessible from your app

### Static Files Not Loading
- Run `collectstatic`
- Check STATIC_ROOT and STATIC_URL settings
- Verify WhiteNoise middleware is enabled

### Celery Not Working
- Verify Redis connection
- Check worker process is running
- Review Celery logs

### 500 Errors
- Check DEBUG=False in production
- Review server logs
- Verify all environment variables are set
- Check database migrations completed

## Quick Start Commands

```bash
# Install production dependencies
pip install gunicorn psycopg2-binary whitenoise

# Update requirements.txt
pip freeze > requirements.txt

# Collect static files
python manage.py collectstatic --noinput

# Run migrations
python manage.py migrate

# Test with Gunicorn locally
gunicorn event_management.wsgi:application
```

## GitHub Actions CI/CD (Optional)

You can automate deployment with GitHub Actions. Create `.github/workflows/deploy.yml`:

```yaml
name: Deploy to Railway

on:
  push:
    branches: [ main ]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - name: Install Railway CLI
        run: npm install -g @railway/cli
      - name: Deploy
        run: railway up
        env:
          RAILWAY_TOKEN: ${{ secrets.RAILWAY_TOKEN }}
```

## Conclusion

Since GitHub Pages only supports static sites, choose one of the platforms above for Django deployment. **Railway** or **Render** are recommended for beginners due to their free tiers and ease of use.

