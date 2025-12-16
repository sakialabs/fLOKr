@echo off
REM ===================================================================
REM Docker Migration & Seeding Script for fLOKr
REM ===================================================================

echo.
echo ========================================
echo   fLOKr - Docker Migration ^& Seeding
echo ========================================
echo.

REM Check if Docker is running
docker info >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Docker is not running. Please start Docker Desktop.
    exit /b 1
)

REM Check if containers are running
docker-compose ps | findstr "flokr_backend" >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Backend container is not running.
    echo Run: docker-compose up -d
    exit /b 1
)

echo [1/5] Installing Faker in Docker container...
docker-compose exec backend pip install Faker --quiet
if errorlevel 1 (
    echo [ERROR] Failed to install Faker
    exit /b 1
)
echo      ✓ Faker installed

echo.
echo [2/5] Creating new migrations...
docker-compose exec backend python manage.py makemigrations
if errorlevel 1 (
    echo [ERROR] Failed to create migrations
    exit /b 1
)
echo      ✓ Migrations created

echo.
echo [3/5] Running migrations...
docker-compose exec backend python manage.py migrate
if errorlevel 1 (
    echo [ERROR] Failed to run migrations
    exit /b 1
)
echo      ✓ Migrations applied

echo.
echo [4/5] Clearing old data and seeding realistic data...
docker-compose exec backend python manage.py seed_realistic_data --clear
if errorlevel 1 (
    echo [ERROR] Failed to seed data
    exit /b 1
)
echo      ✓ Database seeded

echo.
echo [5/5] Verifying data...
echo.
docker-compose exec backend python manage.py shell -c "from django.contrib.auth import get_user_model; from hubs.models import Hub, Event, Announcement; from inventory.models import InventoryItem; from reservations.models import Reservation; print(f'\n=== DATABASE SUMMARY ==='); print(f'Users: {get_user_model().objects.count()}'); print(f'Hubs: {Hub.objects.count()}'); print(f'Items: {InventoryItem.objects.count()}'); print(f'Reservations: {Reservation.objects.count()}'); print(f'Events: {Event.objects.count()}'); print(f'Announcements: {Announcement.objects.count()}'); print('========================\n')"

echo.
echo ========================================
echo   SUCCESS! Database is ready
echo ========================================
echo.
echo Next steps:
echo   1. Backend is running at: http://localhost:8000
echo   2. Start frontend: cd frontend ^&^& npm run dev
echo   3. Visit: http://localhost:3000
echo.
echo To view logs:
echo   docker-compose logs -f backend
echo.

pause
