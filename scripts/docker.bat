@echo off
REM fLOKr Docker Management Script

set CMD=%1
if "%CMD%"=="" set CMD=help

if "%CMD%"=="start" goto start
if "%CMD%"=="stop" goto stop
if "%CMD%"=="restart" goto restart
if "%CMD%"=="logs" goto logs
if "%CMD%"=="shell" goto shell
if "%CMD%"=="bash" goto bash
if "%CMD%"=="test" goto test
if "%CMD%"=="migrate" goto migrate
if "%CMD%"=="clean" goto clean
if "%CMD%"=="status" goto status
goto help

:start
echo 🚀 Starting fLOKr...
docker-compose up -d --build
echo.
echo ✓ fLOKr is running!
echo   Backend:  http://localhost:8000
echo   API Docs: http://localhost:8000/api/docs/
echo   Admin:    http://localhost:8000/admin/ (admin@flokr.com / admin123)
goto end

:stop
echo 🛑 Stopping fLOKr...
docker-compose down
echo ✓ Stopped
goto end

:restart
echo 🔄 Restarting fLOKr...
docker-compose restart
echo ✓ Restarted
goto end

:logs
if "%2"=="" (
    docker-compose logs -f backend
) else (
    docker-compose logs -f %2
)
goto end

:shell
docker-compose exec backend python manage.py shell
goto end

:bash
docker-compose exec backend bash
goto end

:test
echo 🧪 Running tests...
docker-compose exec backend pytest -v %2 %3 %4 %5
goto end

:migrate
echo ⏳ Running migrations...
docker-compose exec backend python manage.py migrate
echo ✓ Migrations complete
goto end

:clean
echo 🧹 Cleaning up...
docker-compose down -v
echo ✓ Cleaned (volumes removed)
goto end

:status
docker-compose ps
goto end

:help
echo fLOKr Docker Manager
echo.
echo Usage: scripts\docker.bat [command]
echo.
echo Commands:
echo   start      Start all services
echo   stop       Stop all services
echo   restart    Restart all services
echo   logs       View logs (add service name: logs backend)
echo   shell      Open Django shell
echo   bash       Open bash in backend container
echo   test       Run tests (add path: test users/)
echo   migrate    Run database migrations
echo   clean      Stop and remove all containers and volumes
echo   status     Show container status
echo.
echo Examples:
echo   scripts\docker.bat start
echo   scripts\docker.bat logs backend
echo   scripts\docker.bat test users/

:end
