#!/usr/bin/env bash
# Exit on error
set -o errexit

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Collect static files into STATIC_ROOT for WhiteNoise
python manage.py collectstatic --no-input

# Apply database migrations
python manage.py migrate


python -c "
import os, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'smart_student_planner.settings')
django.setup()
from django.contrib.auth.models import User
try:
    u = User.objects.get(username='avilash')
    u.is_staff = True
    u.is_superuser = True
    u.save()
    print('>>> avilash is now an admin!')
except Exception as e:
    print('>>> Error:', e)
"
