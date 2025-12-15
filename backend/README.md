# fLOKr Backend API

Django REST API with JWT authentication, Celery background tasks, and push notifications.

## Quick Start

```bash
# 1. Setup environment
conda env create -f environment.yml
conda activate flokr

# 2. Start services
cd ..
docker-compose up -d
cd backend

# 3. Configure
cp .env.example .env

# 4. Migrate & run
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Visit http://localhost:8000/api/docs/ for API documentation.

## Features

✅ **Authentication** - JWT tokens, role-based permissions (newcomer, steward, admin, partner)
✅ **User Management** - Registration, profiles, onboarding, preferences
✅ **Hub System** - Geographic search with PostGIS, steward assignments
✅ **Inventory** - CRUD, search, filtering, image support
✅ **Reservations** - Full lifecycle (create, pickup, return, extend, cancel)
✅ **Notifications** - Push notifications via Firebase, in-app, preferences, quiet hours
✅ **Background Tasks** - Celery for expiration, reminders, reports
✅ **API Docs** - Interactive Swagger UI with drf-spectacular


## API Endpoints

### Authentication (`/api/auth/`)
- `POST /register/` - Create account
- `POST /login/` - Get JWT tokens
- `POST /logout/` - Blacklist refresh token
- `POST /token/refresh/` - Refresh access token
- `GET /profile/` - Get user profile
- `PUT /profile/` - Update profile
- `POST /password-reset/request/` - Request password reset
- `POST /password-reset/confirm/` - Confirm password reset

### Notifications (`/api/users/`)
- `GET /notifications/` - List notifications
- `GET /notifications/unread_count/` - Get unread count
- `POST /notifications/{id}/mark_read/` - Mark as read
- `POST /notifications/mark_all_read/` - Mark all as read
- `GET /notification-preferences/` - Get preferences
- `POST /notification-preferences/` - Update preferences
- `POST /devices/` - Register device token
- `POST /devices/unregister/` - Unregister device

### Hubs (`/api/hubs/`)
- `GET /` - List hubs
- `GET /nearby/?lat=X&lng=Y` - Find nearby hubs
- `GET /{id}/analytics/` - Hub statistics (stewards/admins)

### Inventory (`/api/inventory/items/`)
- `GET /` - List items (with filters)
- `GET /search/?q=X&hub_id=Y` - Search items
- `POST /` - Create item (stewards/admins)
- `GET /{id}/` - Item details
- `PUT /{id}/` - Update item
- `POST /{id}/mark_inactive/` - Mark inactive

### Reservations (`/api/reservations/`)
- `GET /` - List reservations
- `POST /` - Create reservation
- `POST /{id}/cancel/` - Cancel reservation
- `POST /{id}/pickup/` - Mark as picked up
- `POST /{id}/return/` - Return item
- `POST /{id}/request_extension/` - Request extension
- `POST /{id}/approve_extension/` - Approve extension (stewards)


## User Roles & Permissions

- **newcomer** - New arrivals, can browse and reserve items
- **community_member** - Local residents, can donate items
- **steward** - Hub managers, can manage inventory and reservations
- **admin** - Platform administrators, full access
- **partner** - Partner organizations, analytics access

## Celery Background Tasks

Start worker and scheduler:
```bash
# Terminal 1: Worker
celery -A flokr worker -l info --pool=solo

# Terminal 2: Beat Scheduler
celery -A flokr beat -l info --scheduler django_celery_beat.schedulers:DatabaseScheduler

# Check status
python manage.py celery_status
```

**Automated Tasks:**
- **Hourly** - Expire pending reservations past pickup date
- **Daily 9 AM** - Send pickup reminders (1 day before)
- **Daily 9 AM** - Send return reminders (1 day before)
- **Daily 10 AM** - Send overdue reminders (escalating: day 1, 3, 7, weekly)
- **Daily 11 PM** - Generate reservation statistics
- **Sunday 2 AM** - Archive old reservations (90+ days)


## Push Notifications

Notifications are sent via Firebase Cloud Messaging (FCM) for iOS/Android/Web.

**Setup (Optional for Development):**
1. Create Firebase project at https://console.firebase.google.com
2. Download service account JSON
3. Add to `.env`: `FIREBASE_CREDENTIALS_PATH=/path/to/credentials.json`
4. Install: `pip install firebase-admin`

**Without Firebase:** Notifications log to console (perfect for development).

**Notification Types:**
- `reservation` - Confirmations, cancellations
- `reminder` - Pickup/return reminders, overdue alerts
- `message` - Direct messages
- `community` - Badges, achievements
- `system` - Maintenance, updates
- `incident` - Urgent steward alerts

**User Preferences:**
- Enable/disable push notifications
- Per-type toggles (reservations, reminders, messages, community)
- Quiet hours (e.g., 22:00-08:00)

## Testing

```bash
# Run all tests
pytest -v

# Run specific tests
pytest users/tests_notifications.py -v
pytest reservations/tests_tasks.py -v

# With coverage
pytest --cov=. --cov-report=html

# System check
python manage.py check_system
```

**Test Coverage:**
- ✅ 8 notification tests (models, service, preferences)
- ✅ 10 Celery task tests (expiration, reminders, error handling)
- ✅ Task configuration validation


## Environment Variables

```env
# Django
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Database
DATABASE_URL=postgresql://flokr_user:flokr_password@localhost:5432/flokr_db

# Redis & Celery
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0
REDIS_URL=redis://localhost:6379/0

# JWT
JWT_ACCESS_TOKEN_LIFETIME_MINUTES=60
JWT_REFRESH_TOKEN_LIFETIME_DAYS=7

# Frontend
FRONTEND_URL=http://localhost:3000

# Firebase (Optional)
FIREBASE_CREDENTIALS_PATH=/path/to/firebase-credentials.json

# Email (Optional)
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
EMAIL_HOST=
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=
EMAIL_HOST_PASSWORD=
DEFAULT_FROM_EMAIL=noreply@flokr.com
```

## Project Structure

```
backend/
├── flokr/              # Django project settings
├── users/              # User auth, profiles, notifications
├── hubs/               # Hub management
├── inventory/          # Item management
├── reservations/       # Reservation system, Celery tasks
├── community/          # Community features (future)
├── partners/           # Partner features (future)
├── manage.py           # Django management
├── requirements.txt    # Python dependencies
└── environment.yml     # Conda environment
```

## Troubleshooting

**Database errors:** Check PostgreSQL is running: `docker-compose ps`
**Celery not working:** Check Redis: `redis-cli ping` (should return PONG)
**Import errors:** Activate environment: `conda activate flokr`
**Port in use:** Run on different port: `python manage.py runserver 8001`

## Scripts

All scripts are in the `scripts/` folder at project root:

- `scripts/checkpoint.bat` / `scripts/checkpoint.sh` - Run Checkpoint 1 verification
- `scripts/run_tests.py` - Run backend tests
- `scripts/setup-backend.sh` - Initial backend setup

## Next Steps

1. ✅ Complete Tasks 1-8 (Auth, Hubs, Inventory, Reservations, Celery, Notifications)
2. 🔄 Run Checkpoint 1: `scripts/checkpoint.bat` or `./scripts/checkpoint.sh`
3. ⏭️ Task 10: Ori AI - Image tagging service

See `docs/CHANGELOG.md` for detailed checkpoint verification instructions.
