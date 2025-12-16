@echo off
REM fLOKr - Setup Script for Real Data Migration (Windows)

echo ==========================================
echo fLOKr - Real Data Setup
echo ==========================================
echo.

REM Check if we're in the backend directory
if not exist "manage.py" (
    echo Error: This script must be run from the backend directory
    exit /b 1
)

echo Installing dependencies...
pip install faker >nul 2>&1
echo Done: Dependencies installed
echo.

REM Create migrations
echo Creating database migrations...
python manage.py makemigrations
echo Done: Migrations created
echo.

REM Apply migrations
echo Applying migrations...
python manage.py migrate
echo Done: Migrations applied
echo.

REM Seed the database
echo ==========================================
echo Seeding realistic data...
echo ==========================================
echo.
python manage.py seed_realistic_data

echo.
echo ==========================================
echo Setup Complete!
echo ==========================================
echo.
echo Your database now contains:
echo   * 5 Community Hubs
echo   * 50 Realistic Users (newcomers, members, stewards, partners)
echo   * 100+ Inventory Items across all categories
echo   * 50+ Reservations (active, pending, overdue, returned)
echo   * 8 Achievement Badges
echo   * Badge Awards
echo   * 10+ Mentorship Connections with Messages
echo   * 20+ Events (past and upcoming)
echo   * 15+ Hub Announcements
echo   * 30+ Feedback Entries
echo.
echo Next steps:
echo   1. Start the backend server: python manage.py runserver
echo   2. Start the frontend: cd ..\frontend ^&^& npm run dev
echo   3. Visit http://localhost:3000
echo.
echo Happy testing!
pause
