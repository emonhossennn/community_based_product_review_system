#!/bin/bash

echo "============================================"
echo "Community Product Review Analytics Demo"
echo "============================================"
echo
echo "Starting the complete analytics platform..."
echo "This will set up:"
echo "- PostgreSQL database"
echo "- Django REST API backend" 
echo "- React analytics dashboard"
echo "- Sample data with 500+ reviews"
echo

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "Error: Docker is not installed"
    echo "Please install Docker and try again"
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo "Error: Docker Compose is not installed"
    echo "Please install Docker Compose and try again"
    exit 1
fi

echo "Starting containers..."
docker-compose up -d

echo
echo "============================================"
echo "Demo is starting up..."
echo "============================================"
echo
echo "Frontend Dashboard: http://localhost:3000"
echo "Backend API:        http://localhost:8000/api"
echo "Admin Panel:        http://localhost:8000/admin"
echo
echo "Admin Credentials:"
echo "Username: admin"
echo "Password: admin123"
echo
echo "The system will be ready in 2-3 minutes."
echo "Sample data is being generated automatically."
echo
echo "To stop the demo: docker-compose down"
echo "============================================"

# Wait for services to be ready
echo
echo "Waiting for services to be ready..."
sleep 30

# Check if services are running
if curl -s http://localhost:8000/api/dashboard/ > /dev/null; then
    echo "✓ Backend API is ready!"
else
    echo "⚠ Backend is still starting up, please wait..."
fi

if curl -s http://localhost:3000 > /dev/null; then
    echo "✓ Frontend dashboard is ready!"
else
    echo "⚠ Frontend is still starting up, please wait..."
fi

echo
echo "Demo is ready! Open http://localhost:3000 in your browser"
