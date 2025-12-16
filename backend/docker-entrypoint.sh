#!/bin/bash
set -e

# Docker-compose handles service dependencies with health checks
# Just add a small delay to be safe
echo "⏳ Waiting for services..."
sleep 3
echo "✓ Services ready (via docker-compose health checks)"

# Run migrations
echo "⏳ Running migrations..."
python manage.py migrate --noinput
echo "✓ Migrations complete"

# Create superuser
python manage.py shell -c "
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(email='admin@flokr.com').exists():
    User.objects.create_superuser(email='admin@flokr.com', password='admin123', first_name='Admin', last_name='User', role='admin')
    print('✓ Superuser created: admin@flokr.com / admin123')
else:
    print('✓ Superuser exists')
" 2>/dev/null || echo "⚠ Superuser setup skipped"

# Setup periodic tasks
python manage.py setup_periodic_tasks 2>/dev/null || echo "⚠ Periodic tasks setup skipped"

# Collect static files
python manage.py collectstatic --noinput >/dev/null 2>&1 || true

echo "🚀 Starting application..."
exec "$@"
