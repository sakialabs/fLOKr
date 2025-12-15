@echo off
echo ====================================
echo Starting fLOKr Development Environment
echo ====================================
echo.

echo This will open 3 terminal windows:
echo 1. Django Backend (port 8000)
echo 2. Next.js Frontend (port 3000)
echo 3. Expo Mobile (port 19000)
echo.
echo Press any key to continue...
pause > nul

echo Starting Django backend...
start "Django Backend" cmd /k "cd backend && python manage.py runserver"
timeout /t 2 > nul

echo Starting Next.js frontend...
start "Next.js Frontend" cmd /k "cd frontend && npm run dev"
timeout /t 2 > nul

echo Starting Expo mobile...
start "Expo Mobile" cmd /k "cd mobile && npm start"

echo.
echo ====================================
echo All services starting!
echo ====================================
echo Backend:  http://localhost:8000
echo Frontend: http://localhost:3000
echo Mobile:   Scan QR code in Expo window
echo.
echo Close this window when done.
