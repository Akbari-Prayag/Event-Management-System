web: python manage.py migrate && gunicorn event_management.wsgi:application --bind 0.0.0.0:$PORT
worker: celery -A event_management worker --loglevel=info

