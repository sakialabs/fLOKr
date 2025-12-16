#!/bin/bash
# ===================================================================
# Docker Migration & Seeding Script for fLOKr
# ===================================================================

set -e

echo ""
echo "========================================"
echo "  fLOKr - Docker Migration & Seeding"
echo "========================================"
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if Docker is running
if ! docker info >/dev/null 2>&1; then
    echo -e "${RED}[ERROR]${NC} Docker is not running. Please start Docker."
    exit 1
fi

# Check if containers are running
if ! docker-compose ps | grep -q "flokr_backend"; then
    echo -e "${RED}[ERROR]${NC} Backend container is not running."
    echo "Run: docker-compose up -d"
    exit 1
fi

echo "[1/5] Installing Faker in Docker container..."
docker-compose exec backend pip install Faker --quiet
echo -e "     ${GREEN}✓${NC} Faker installed"

echo ""
echo "[2/5] Creating new migrations..."
docker-compose exec backend python manage.py makemigrations
echo -e "     ${GREEN}✓${NC} Migrations created"

echo ""
echo "[3/5] Running migrations..."
docker-compose exec backend python manage.py migrate
echo -e "     ${GREEN}✓${NC} Migrations applied"

echo ""
echo "[4/5] Clearing old data and seeding realistic data..."
docker-compose exec backend python manage.py seed_realistic_data --clear
echo -e "     ${GREEN}✓${NC} Database seeded"

echo ""
echo "[5/5] Verifying data..."
echo ""
docker-compose exec backend python manage.py shell -c "
from django.contrib.auth import get_user_model
from hubs.models import Hub, Event, Announcement
from inventory.models import InventoryItem
from reservations.models import Reservation

print('\n=== DATABASE SUMMARY ===')
print(f'Users: {get_user_model().objects.count()}')
print(f'Hubs: {Hub.objects.count()}')
print(f'Items: {InventoryItem.objects.count()}')
print(f'Reservations: {Reservation.objects.count()}')
print(f'Events: {Event.objects.count()}')
print(f'Announcements: {Announcement.objects.count()}')
print('========================\n')
"

echo ""
echo "========================================"
echo -e "  ${GREEN}SUCCESS!${NC} Database is ready"
echo "========================================"
echo ""
echo "Next steps:"
echo "  1. Backend is running at: http://localhost:8000"
echo "  2. Start frontend: cd frontend && npm run dev"
echo "  3. Visit: http://localhost:3000"
echo ""
echo "To view logs:"
echo "  docker-compose logs -f backend"
echo ""
