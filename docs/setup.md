# fLOKr Platform Setup

Complete setup guide for backend, frontend, and mobile apps.

## Option 1: Using Conda (Recommended)

### Create the Environment

```bash
cd backend
conda env create -f environment.yml
```

This will create a conda environment named `flokr` with Python 3.11 and all dependencies.

### Activate the Environment

```bash
conda activate flokr
```

### Update the Environment (if needed)

If you add new dependencies to `environment.yml`:

```bash
conda env update -f environment.yml --prune
```

### Verify Installation

```bash
python --version  # Should show Python 3.11.x
python -c "import django; print(django.get_version())"  # Should show 4.2.7
```

## Option 2: Using venv

```bash
cd backend
python -m venv venv

# Activate (Windows)
venv\Scripts\activate

# Activate (Mac/Linux)
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

## Database Setup

### Using Docker (Easiest)

From the project root:

```bash
docker-compose up -d
```

This starts PostgreSQL with PostGIS and Redis.

### Manual PostgreSQL Setup

If you prefer to install PostgreSQL locally:

```bash
# Create database
createdb flokr_db

# Enable PostGIS extension
psql flokr_db -c "CREATE EXTENSION postgis;"
```

## Environment Variables

1. Copy the example file:
```bash
cp .env.example .env
```

2. Edit `.env` with your settings:
```env
SECRET_KEY=your-secret-key-here
DEBUG=True
DATABASE_URL=postgresql://flokr_user:flokr_password@localhost:5432/flokr_db
REDIS_URL=redis://localhost:6379/0
FRONTEND_URL=http://localhost:3000
```

## Run Migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

## Create Superuser

```bash
python manage.py createsuperuser
```

Follow the prompts to create an admin account.

## Start Development Server

```bash
python manage.py runserver
```

The API will be available at:
- API: http://localhost:8000/api/
- Admin: http://localhost:8000/admin/
- API Docs: http://localhost:8000/api/docs/

## Start Celery (Background Tasks)

Celery handles background jobs like reservation expiration, reminders, and notifications.

### Quick Start

**Terminal 1: Celery Worker**
```bash
conda activate flokr  # or activate your venv
celery -A flokr worker -l info --pool=solo  # --pool=solo for Windows
```

**Terminal 2: Celery Beat (Scheduler)**
```bash
conda activate flokr
celery -A flokr beat -l info --scheduler django_celery_beat.schedulers:DatabaseScheduler
```

### Setup Periodic Tasks

First time only:
```bash
python manage.py migrate django_celery_beat
python manage.py setup_periodic_tasks
```

### Monitor Celery

Check status:
```bash
python manage.py celery_status
```

For more details, see [reservations/CELERY_README.md](/backend/reservations/README.md)

## Running Tests

```bash
pytest
```

With coverage:

```bash
pytest --cov=. --cov-report=html
```

## Code Quality

Format code:

```bash
black .
isort .
```

Lint code:

```bash
flake8
```

## Troubleshooting

### "No module named 'django'"

Make sure your conda environment is activated:
```bash
conda activate flokr
```

### Database connection errors

1. Check if PostgreSQL is running:
```bash
docker-compose ps
```

2. Verify DATABASE_URL in `.env` matches your setup

### Port already in use

If port 8000 is taken:
```bash
python manage.py runserver 8001
```

### PostGIS errors

Make sure PostGIS extension is enabled:
```bash
psql flokr_db -c "CREATE EXTENSION IF NOT EXISTS postgis;"
```

## Quick Start (All-in-One)

### Backend
```bash
# Automated setup
./scripts/setup-backend.sh
conda activate flokr

# Or manual setup
cd backend
conda env create -f environment.yml
conda activate flokr
cd ..
docker-compose up -d
cd backend
cp .env.example .env
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

### Frontend
```bash
cd frontend
npm install
cp .env.example .env.local
# Edit .env.local: NEXT_PUBLIC_API_URL=http://localhost:8000
npm run dev
```

### Mobile
```bash
cd mobile
npm install
cp .env.example .env
# Edit .env: API_URL=http://localhost:8000
npm start
```

**Access:**
- Backend API: http://localhost:8000/api/docs/
- Frontend: http://localhost:3000
- Mobile: Expo DevTools in browser

---

# Backend Setup




---

# Frontend Setup

## Prerequisites
- Node.js 18+
- npm or yarn

## Installation

```bash
cd frontend
npm install
```

## Environment Variables

```bash
cp .env.example .env.local
```

Edit `.env.local`:
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## Development

```bash
npm run dev
```

Visit http://localhost:3000

## Tech Stack
- Next.js 15 (App Router)
- TypeScript (strict mode)
- shadcn/ui components
- Tailwind CSS (custom warm design system)
- Framer Motion
- Redux Toolkit + TanStack Query

## Design System
**Light:** Warm Off-White bg, Deep Teal primary, Soft Clay secondary
**Dark:** Deep Charcoal bg, Teal Muted primary, Clay Softened accent

---

# Mobile Setup

## Prerequisites
- Node.js 18+
- Expo CLI: `npm install -g expo-cli`
- iOS: Xcode (Mac only)
- Android: Android Studio

## Installation

```bash
cd mobile
npm install
```

## Environment Variables

```bash
cp .env.example .env
```

Edit `.env`:
```env
API_URL=http://localhost:8000
```

## Development

```bash
npm start
```

Then:
- Press `i` for iOS simulator
- Press `a` for Android emulator
- Scan QR code with Expo Go app

## Tech Stack
- React Native with Expo
- TypeScript
- Redux Toolkit
- React Navigation
- Expo Camera, Location, Notifications

---

# Full Stack Development

## Start All Services

**Terminal 1: Databases**
```bash
docker-compose up
```

**Terminal 2: Backend**
```bash
cd backend
conda activate flokr
python manage.py runserver
```

**Terminal 3: Celery Worker**
```bash
cd backend
conda activate flokr
celery -A flokr worker -l info --pool=solo
```

**Terminal 4: Celery Beat**
```bash
cd backend
conda activate flokr
celery -A flokr beat -l info --scheduler django_celery_beat.schedulers:DatabaseScheduler
```

**Terminal 5: Frontend**
```bash
cd frontend
npm run dev
```

**Terminal 6: Mobile**
```bash
cd mobile
npm start
```

## Ports
- Backend: 8000
- Frontend: 3000
- PostgreSQL: 5432
- Redis: 6379
- Expo: 19000-19006
