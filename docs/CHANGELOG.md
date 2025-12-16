# Changelog

All notable changes to the fLOKr platform will be documented in this file.

## [Unreleased]

### ✅ Completed
- **Task 10: Ori AI - Image Tagging Service** - Automatic tag and category generation
  - ResNet50-based image analysis
  - Automatic tagging on item creation
  - Tag preview endpoint for stewards
  - Frontend component with real-time AI suggestions
  - < 5 second processing time
  - 8 category classifications
  - Confidence scoring for tags

### 🔄 In Progress
- Task 11: Ori AI - Recommendation engine

---

## Checkpoint 1: Verification Guide

### Quick Verification

Run the automated checkpoint script:

**Windows:**
```bash
scripts\checkpoint.bat
```

**Mac/Linux:**
```bash
./scripts/checkpoint.sh
```

This will automatically:
1. Check database connectivity
2. Run migrations
3. Setup Celery periodic tasks
4. Run system health check
5. Execute all 18 tests

### Manual Verification Steps

#### 1. Start Services
```bash
# PostgreSQL and Redis
docker-compose up -d

# Backend
cd backend
conda activate flokr
python manage.py runserver
```

#### 2. Run Tests
```bash
# All tests
python scripts/run_tests.py

# Or specific tests
pytest users/tests_notifications.py -v
pytest reservations/tests_tasks.py -v
```

#### 3. Check API Documentation
Visit: http://localhost:8000/api/docs/

Verify endpoints:
- `/api/auth/register/` - User registration
- `/api/auth/login/` - User login
- `/api/users/notifications/` - Notifications
- `/api/hubs/` - Hub management
- `/api/inventory/items/` - Inventory
- `/api/reservations/` - Reservations

#### 4. Verify Celery Tasks

**Terminal 1: Worker**
```bash
celery -A flokr worker -l info --pool=solo
```

**Terminal 2: Beat Scheduler**
```bash
celery -A flokr beat -l info --scheduler django_celery_beat.schedulers:DatabaseScheduler
```

**Terminal 3: Check Status**
```bash
python manage.py celery_status
```

### Success Criteria

- ✅ All 18 tests pass (8 notification + 10 Celery task tests)
- ✅ System check shows no errors
- ✅ Celery worker and beat are running
- ✅ API documentation is accessible
- ✅ Can create users, hubs, items, reservations
- ✅ Notifications are created (logged to console without Firebase)
- ✅ 6 periodic tasks are scheduled

### Troubleshooting

**Tests failing?**
```bash
python manage.py migrate
```

**Database errors?**
```bash
docker-compose ps  # Check if PostgreSQL is running
docker-compose restart postgres
```

**Celery not working?**
```bash
redis-cli ping  # Should return PONG
docker-compose restart redis
```

**Notifications not sending?**
This is expected! Without Firebase credentials, notifications log to console (perfect for development).

**GDAL library not found?**
```bash
# Update environment with GDAL
scripts\update-env.bat  # Windows
./scripts/update-env.sh # Mac/Linux

# Or manually
conda activate flokr
conda install -c conda-forge gdal geos proj
```

---

## [0.1.0] - 2024-12-15

### ✅ Completed - Core Backend (Tasks 1-8)

#### Task 1: Project Setup and Infrastructure
- Django project with 6 apps (users, inventory, reservations, hubs, community, partners)
- PostgreSQL with PostGIS for geospatial data
- Redis for caching and Celery broker
- Next.js 15 frontend with App Router
- Expo React Native mobile app
- Docker Compose for local development
- Conda environment configuration

#### Task 2: User Authentication and Registration
- Custom User model with 5 roles (newcomer, community_member, steward, admin, partner)
- JWT token-based authentication (access + refresh tokens)
- Token blacklisting on logout
- User registration and login endpoints
- Profile management (GET, PUT)
- Password reset functionality
- Role-based permission classes

#### Task 3: User Onboarding and Preferences
- 3-step onboarding flow
- User preferences storage (dietary restrictions, clothing sizes, languages, skills)
- Language preference support
- Welcome screen with personalized data

#### Task 4: Hub Management System
- Hub CRUD operations
- Geographic location with PostGIS Point fields
- Nearby hubs search using distance queries
- Steward assignment to hubs
- Hub analytics endpoint (stewards/admins only)
- Operating hours management

#### Task 5: Inventory Management System
- Inventory item CRUD operations
- Category, condition, and status tracking
- Quantity management (total vs available)
- Image upload support (JSON array of URLs)
- Advanced search and filtering (django-filter)
- Tag system for items
- Donor tracking
- Inactive item filtering

#### Task 6: Reservation and Borrowing System
- Full reservation lifecycle (create, pickup, return, cancel)
- Reservation status flow (pending → confirmed → picked_up → returned/cancelled)
- Automatic inventory quantity updates
- Extension request workflow (user requests, steward approves)
- Late return tracking and borrowing restrictions
- Validation for availability and date logic
- Role-based access control

#### Task 7: Celery Background Tasks
- Celery worker and beat scheduler configuration
- 6 automated periodic tasks:
  - **Hourly**: Expire pending reservations past pickup date
  - **Daily 9 AM**: Send pickup reminders (1 day before)
  - **Daily 9 AM**: Send return reminders (1 day before)
  - **Daily 10 AM**: Send overdue reminders (escalating: day 1, 3, 7, weekly)
  - **Daily 11 PM**: Generate reservation statistics report
  - **Sunday 2 AM**: Archive old reservations (90+ days)
- Robust error handling with retries
- Transaction safety for database operations
- Comprehensive logging

#### Task 8: Notification System
- Push notifications via Firebase Cloud Messaging (iOS/Android/Web)
- In-app notification storage and tracking
- Notification preferences (per-type toggles, quiet hours)
- Device token management (register/unregister)
- 6 notification types: reservation, reminder, message, community, system, incident
- Read/unread tracking
- Graceful fallback to console logging without Firebase
- Integration with all Celery tasks

### 🧪 Testing
- 18 automated tests (8 notification tests + 10 Celery task tests)
- Test coverage for models, services, and background tasks
- Checkpoint 1 verification scripts (Windows + Mac/Linux)
- Custom test runner script

### 📚 Documentation
- Consolidated backend README
- Complete setup guide for all platforms
- Checkpoint 1 verification guide
- Script documentation
- API documentation with drf-spectacular

### 🎨 Frontend & Mobile
- API client integration for all backend endpoints
- Auth services (login, register, profile)
- Hub services (list, nearby search)
- Inventory services (browse, search, create)
- Reservation services (full lifecycle)
- Notification services (push, preferences, device tokens)
- Redux store setup
- Warm design system (light/dark modes)

### 🛠️ Developer Experience
- Centralized scripts folder (`scripts/`)
- Automated setup script (`setup-backend.sh`)
- Checkpoint verification scripts
- Test runner script
- Comprehensive documentation structure

---

## Version History

- **0.1.0** (2024-12-15) - Core backend complete (Tasks 1-8)
- **0.0.1** (2024-12-01) - Initial project setup

---

## Next Milestones

### Checkpoint 1 (Current)
- Verify all 18 tests pass
- Confirm Celery tasks are scheduled
- Validate API endpoints
- Test notification system

### Phase 2: Ori AI Features (Tasks 10-14)
- Image tagging service
- Recommendation engine
- Natural language Q&A system
- Translation service
- Demand forecasting

### Phase 3: Community Features (Tasks 16-25)
- Badge and gamification system
- Reputation and leaderboard
- Feedback and incident reporting
- Mentorship matching
- In-app messaging

### Phase 4: Partner Features (Tasks 26-29)
- Partner account management
- Sponsored content system
- Analytics and insights
- Resource recommendations

### Phase 5: Mobile & Frontend UI (Tasks 36-50)
- Complete mobile app screens
- Frontend dashboard and features
- Camera and image upload
- Push notification setup
- Location services

### Phase 6: Production Ready (Tasks 53-55)
- Performance optimization
- Monitoring and logging
- Deployment preparation
