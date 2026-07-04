@echo off
REM Checkpoint verification script

echo ================================
echo 🎯 fLOKr Checkpoint Verification
echo ================================
echo.

cd backend
if not exist "manage.py" (
    echo ❌ Error: backend/manage.py not found
    exit /b 1
)

echo ⏳ Checking database...
python manage.py check --database default
if errorlevel 1 (echo ❌ Database check failed & exit /b 1)
echo ✓ Database OK
echo.

echo ⏳ Running migrations...
python manage.py migrate --no-input
if errorlevel 1 (echo ❌ Migrations failed & exit /b 1)
echo ✓ Migrations OK
echo.

echo ⏳ Setting up periodic tasks...
python manage.py setup_periodic_tasks
echo ✓ Periodic tasks OK
echo.

echo ⏳ Running system check...
python manage.py check_system
echo.

echo ⏳ Running tests...
python manage.py test users.tests_notifications reservations.tests_tasks --verbosity=2
if errorlevel 1 (echo ❌ Tests failed & exit /b 1)
echo ✓ Tests passed
echo.

echo ================================
echo ✅ Checkpoint Complete!
echo ================================
echo.
echo Next: Start services with scripts\docker.bat start
echo.

cd ..
