#!/bin/bash
# fLOKr Docker Management Script

set -e

CMD=${1:-help}

case "$CMD" in
  start)
    echo "🚀 Starting fLOKr..."
    docker-compose up -d --build
    echo ""
    echo "✓ fLOKr is running!"
    echo "  Backend:  http://localhost:8000"
    echo "  API Docs: http://localhost:8000/api/docs/"
    echo "  Admin:    http://localhost:8000/admin/ (admin@flokr.com / admin123)"
    ;;
    
  stop)
    echo "🛑 Stopping fLOKr..."
    docker-compose down
    echo "✓ Stopped"
    ;;
    
  restart)
    echo "🔄 Restarting fLOKr..."
    docker-compose restart
    echo "✓ Restarted"
    ;;
    
  logs)
    docker-compose logs -f ${2:-backend}
    ;;
    
  shell)
    docker-compose exec backend python manage.py shell
    ;;
    
  bash)
    docker-compose exec backend bash
    ;;
    
  test)
    echo "🧪 Running tests..."
    docker-compose exec backend pytest -v ${@:2}
    ;;
    
  migrate)
    echo "⏳ Running migrations..."
    docker-compose exec backend python manage.py migrate
    echo "✓ Migrations complete"
    ;;
    
  clean)
    echo "🧹 Cleaning up..."
    docker-compose down -v
    echo "✓ Cleaned (volumes removed)"
    ;;
    
  status)
    docker-compose ps
    ;;
    
  *)
    echo "fLOKr Docker Manager"
    echo ""
    echo "Usage: ./scripts/docker.sh [command]"
    echo ""
    echo "Commands:"
    echo "  start      Start all services"
    echo "  stop       Stop all services"
    echo "  restart    Restart all services"
    echo "  logs       View logs (add service name: logs backend)"
    echo "  shell      Open Django shell"
    echo "  bash       Open bash in backend container"
    echo "  test       Run tests (add path: test users/)"
    echo "  migrate    Run database migrations"
    echo "  clean      Stop and remove all containers and volumes"
    echo "  status     Show container status"
    echo ""
    echo "Examples:"
    echo "  ./scripts/docker.sh start"
    echo "  ./scripts/docker.sh logs backend"
    echo "  ./scripts/docker.sh test users/"
    ;;
esac
