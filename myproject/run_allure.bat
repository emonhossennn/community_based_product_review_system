@echo off
echo ========================================
echo Running Tests with Allure Reporting
echo ========================================
echo.

echo Installing Allure support...
pip install allure-pytest

echo.
echo Setting up database...
python manage.py makemigrations
python manage.py migrate

echo.
echo Running tests with Allure...
python test_with_allure.py

echo.
echo ========================================
echo Done! Check the allure-report folder
echo ========================================
pause