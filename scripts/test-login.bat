@echo off
echo Testing Login Endpoint...
echo.
echo Enter your email:
set /p email=
echo Enter your password:
set /p password=
echo.

curl -X POST http://localhost:8000/api/auth/login/ ^
  -H "Content-Type: application/json" ^
  -d "{\"email\":\"%email%\",\"password\":\"%password%\"}"

echo.
echo.
