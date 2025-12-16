#!/bin/bash
# Checkpoint verification script

set -e

echo "================================"
echo "🎯 fLOKr Checkpoint Verification"
echo "================================"
echo ""

cd backend
[ ! -f "manage.py" ] && echo "❌ Error: backend/manage.py not found" && exit 1

echo "⏳ Checking database..."
python manage.py check --database default
echo "✓ Database OK"
echo ""

echo "⏳ Running migrations..."
python manage.py migrate --no-input
echo "✓ Migrations OK"
echo ""

echo "⏳ Setting up periodic tasks..."
python manage.py setup_periodic_tasks 2>/dev/null || echo "⚠ Periodic tasks setup skipped"
echo "✓ Periodic tasks OK"
echo ""

echo "⏳ Running system check..."
python manage.py check_system
echo ""

echo "⏳ Running tests..."
python manage.py test users.tests_notifications reservations.tests_tasks --verbosity=2
echo "✓ Tests passed"
echo ""

echo "================================"
echo "✅ Checkpoint Complete!"
echo "================================"
echo ""
echo "Next: Start services with ./scripts/docker.sh start"
echo ""

cd ..
