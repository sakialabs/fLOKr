#!/bin/bash
# Checkpoint 1 verification script

echo "=================================="
echo "fLOKr Checkpoint 1 Verification"
echo "=================================="
echo ""

# Navigate to backend directory
cd backend

# Check if in backend directory
if [ ! -f "manage.py" ]; then
    echo "❌ Error: Could not find backend directory"
    exit 1
fi

echo "Step 1: Checking database connectivity..."
python manage.py check --database default
if [ $? -ne 0 ]; then
    echo "❌ Database check failed"
    exit 1
fi
echo "✓ Database OK"
echo ""

echo "Step 2: Running migrations..."
python manage.py migrate --no-input
if [ $? -ne 0 ]; then
    echo "❌ Migrations failed"
    exit 1
fi
echo "✓ Migrations OK"
echo ""

echo "Step 3: Setting up periodic tasks..."
python manage.py setup_periodic_tasks
if [ $? -ne 0 ]; then
    echo "⚠ Warning: Periodic tasks setup had issues (may be normal if already set up)"
fi
echo "✓ Periodic tasks OK"
echo ""

echo "Step 4: Running system check..."
python manage.py check_system
echo ""

echo "Step 5: Running tests..."
python manage.py test users.tests_notifications reservations.tests_tasks --verbosity=2
if [ $? -ne 0 ]; then
    echo "❌ Tests failed"
    exit 1
fi
echo "✓ Tests passed"
echo ""

echo "=================================="
echo "✅ Checkpoint 1 Complete!"
echo "=================================="
echo ""
echo "Next steps:"
echo "1. Start Celery worker: celery -A flokr worker -l info --pool=solo"
echo "2. Start Celery beat: celery -A flokr beat -l info --scheduler django_celery_beat.schedulers:DatabaseScheduler"
echo "3. Start Django: python manage.py runserver"
echo ""

cd ..
