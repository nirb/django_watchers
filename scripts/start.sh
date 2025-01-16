#!/bin/bash

# Navigate to the project directory
cd /Users/nirbejerano/development/django_watchers

# Activate the virtual environment
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run database migrations
python manage.py migrate

# Collect static files
python manage.py collectstatic --noinput

# Start the Django development server
python manage.py runserver