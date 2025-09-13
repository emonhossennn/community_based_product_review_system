@echo off
echo ============================================
echo Community Product Review Analytics Demo
echo ============================================
echo.
echo Starting the complete analytics platform...
echo This will set up:
echo - PostgreSQL database
echo - Django REST API backend
echo - React analytics dashboard
echo - Sample data with 500+ reviews
echo.

echo Checking Docker...
docker --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Error: Docker is not installed or not running
    echo Please install Docker Desktop and try again
    pause
    exit /b 1
)

echo Starting containers...
docker-compose up -d

echo.
echo ============================================
echo Demo is starting up...
echo ============================================
echo.
echo Frontend Dashboard: http://localhost:3000
echo Backend API:        http://localhost:8000/api
echo Admin Panel:        http://localhost:8000/admin
echo.
echo Admin Credentials:
echo Username: admin
echo Password: admin123
echo.
echo The system will be ready in 2-3 minutes.
echo Sample data is being generated automatically.
echo.
echo To stop the demo: docker-compose down
echo ============================================

pause
