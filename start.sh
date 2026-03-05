#!/bin/bash

# Run database migrations
python manage.py migrate

# Automatically create an admin user if it doesn't exist
python manage.py shell -c "from django.contrib.auth.models import User; User.objects.filter(username='admin').exists() or User.objects.create_superuser('admin', 'admin@example.com', 'admin')"

# Collect static files for WhiteNoise
python manage.py collectstatic --noinput

# Start Gunicorn server
gunicorn myshop.wsgi --log-file -
