@echo off
echo Checking if Django backend is running...
curl -s http://localhost:8000/api/auth/login/ > nul 2>&1
if %errorlevel% equ 0 (
    echo [OK] Backend is running on http://localhost:8000
) else (
    echo [ERROR] Backend is NOT running!
    echo.
    echo To start the backend, run:
    echo   cd backend
    echo   python manage.py runserver
)
