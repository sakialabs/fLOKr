@echo off
echo Testing Registration Endpoint...
echo.

curl -X POST http://localhost:8000/api/auth/register/ ^
  -H "Content-Type: application/json" ^
  -d "{\"email\":\"test@example.com\",\"password\":\"TestPass123!\",\"password_confirm\":\"TestPass123!\",\"first_name\":\"Test\",\"last_name\":\"User\",\"role\":\"newcomer\"}"

echo.
echo.
echo If you see a success message with tokens above, the backend is working!
echo If you see an error about duplicate email, that's also OK - it means the endpoint works.
