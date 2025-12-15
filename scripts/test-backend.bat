@echo off
echo ====================================
echo Testing fLOKr Backend API
echo ====================================
echo.

echo Testing if backend is running...
curl -s http://localhost:8000/api/auth/login/ > nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Backend is NOT running!
    echo.
    echo Start it with: cd backend ^&^& python manage.py runserver
    exit /b 1
)

echo [OK] Backend is running
echo.

echo Testing API endpoints...
echo.

echo 1. Testing login endpoint (should return 400 for empty request):
curl -X POST http://localhost:8000/api/auth/login/ -H "Content-Type: application/json" -d "{}"
echo.
echo.

echo 2. Testing register endpoint (should return 400 for empty request):
curl -X POST http://localhost:8000/api/auth/register/ -H "Content-Type: application/json" -d "{}"
echo.
echo.

echo ====================================
echo If you see JSON error responses above, the backend is working correctly!
echo ====================================
