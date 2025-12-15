@echo off
REM Checkpoint 1 verification script for Windows

echo ==================================
echo fLOKr Checkpoint 1 Verification
echo ==================================
echo.

REM Navigate to backend directory
cd backend

REM Check if in backend directory
if not exist "manage.py" (
    echo Error: Could not find backend directory
    exit /b 1
)

echo Step 1: Checking database connectivity...
python manage.py check --database default
if errorlevel 1 (
    echo Database check failed
    exit /b 1
)
echo Database OK
echo.

echo Step 2: Running migrations...
python manage.py migrate --no-input
if errorlevel 1 (
    echo Migrations failed
    exit /b 1
)
echo Migrations OK
echo.

echo Step 3: Setting up periodic tasks...
python manage.py setup_periodic_tasks
echo Periodic tasks OK
echo.

echo Step 4: Running system check...
python manage.py check_system
echo.

echo Step 5: Running tests...
python manage.py test users.tests_notifications reservations.tests_tasks --verbosity=2
if errorlevel 1 (
    echo Tests failed
    exit /b 1
)
echo Tests passed
echo.

echo ==================================
echo Checkpoint 1 Complete!
echo ==================================
echo.
echo Next steps:
echo 1. Start Celery worker: celery -A flokr worker -l info --pool=solo
echo 2. Start Celery beat: celery -A flokr beat -l info --scheduler django_celery_beat.schedulers:DatabaseScheduler
echo 3. Start Django: python manage.py runserver
echo.

cd ..
