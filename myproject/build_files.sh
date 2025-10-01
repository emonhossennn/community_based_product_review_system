#!/bin/bash

# Build the project
echo "Building the project..."
python3.9 -m pip install -r requirements-vercel.txt

# Collect static files
echo "Collecting static files..."
python3.9 manage.py collectstatic --noinput --clear
