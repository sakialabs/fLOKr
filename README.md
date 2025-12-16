# fLOKr Platform

A digital community hub platform designed to support newcomers in unfamiliar cities by enabling them to borrow, share, and reserve essential items while connecting with local mentors and community hubs.

## 🚀 Quick Start

```bash
# Start with Docker (recommended)
scripts\docker.bat start  # Windows
./scripts/docker.sh start  # Mac/Linux

# Visit http://localhost:8000/api/docs/
# Login: admin@flokr.com / admin123
```

See [DOCKER.md](DOCKER.md) for full Docker commands.

## Project Structure

```
flokr/
├── backend/             # Django REST API
│   ├── flokr/           # Main Django project
│   ├── users/           # User management & notifications
│   ├── inventory/       # Inventory management
│   ├── reservations/    # Reservation system & Celery tasks
│   ├── hubs/            # Hub management
│   ├── community/       # Community features (future)
│   ├── partners/        # Partner management (future)
│   └── manage.py
├── frontend/            # Next.js 15 web app (desktop/tablet)
│   └── src/
│       ├── app/         # App Router pages
│       ├── components/  # UI components
│       ├── lib/         # API client & utilities
│       └── store/       # Redux store
├── mobile/              # Expo React Native app (iOS/Android)
│   └── src/
│       ├── api/         # API client & services
│       ├── navigation/  # Navigation config
│       ├── screens/     # Screen components
│       └── store/       # Redux store
├── scripts/             # Utility scripts
│   ├── checkpoint.bat   # Windows checkpoint verification
│   ├── checkpoint.sh    # Mac/Linux checkpoint verification
│   ├── run_tests.py     # Test runner
│   └── setup-backend.sh # Backend setup script
└── docs/                # Documentation
    ├── setup.md         # Setup guide (all platforms)
    ├── checkpoint-1.md  # Checkpoint 1 verification
    ├── requirements.md  # Feature requirements
    ├── design.md        # System design
    └── tasks.md         # Implementation tasks
```

## Prerequisites

### Backend
- Python 3.11+ (or Conda)
- PostgreSQL 15+ with PostGIS extension
- Redis 7+

### Frontend (Web)
- Node.js 18+
- npm or yarn

### Mobile (Optional)
- Node.js 18+
- Expo CLI
- iOS Simulator (Mac) or Android Studio

## Quick Start

### Automated Setup (Recommended)
```bash
# Backend
./scripts/setup-backend.sh
conda activate flokr

# Start services
docker-compose up -d

# Run checkpoint
./scripts/checkpoint.sh  # Mac/Linux
scripts\checkpoint.bat   # Windows
```

### Manual Setup
See detailed instructions in [`docs/setup.md`](docs/setup.md)

## Development Scripts

**Docker (Recommended):**
```bash
./scripts/docker.sh [start|stop|test|logs|shell]
```

**Other Scripts:**
- `setup-backend.sh` - Initial backend setup
- `checkpoint.sh` - Verify milestone completion
- `run_tests.py` - Run backend tests

See [DOCKER.md](DOCKER.md) and [scripts/README.md](scripts/README.md) for details.

## Testing

```bash
# Backend - All tests
python scripts/run_tests.py

# Backend - Specific app
python scripts/run_tests.py users

# Frontend
cd frontend && npm test

# Mobile
cd mobile && npm test
```

## Technology Stack

### Backend
- Django 4.2+ with Django REST Framework
- PostgreSQL with PostGIS for geospatial data
- Redis for caching and Celery broker
- Celery for background tasks
- JWT authentication

### Frontend (Web)
- Next.js 15 with App Router
- TypeScript (strict mode)
- shadcn/ui component library
- Tailwind CSS with custom warm design system
- Redux Toolkit for state management
- Framer Motion for animations
- Axios for API calls

### Mobile
- Expo SDK 49+
- React Native
- Redux Toolkit for state management
- React Navigation
- Axios for API calls

## Features

- User authentication and role-based access control
- Inventory management across multiple hubs
- Reservation and borrowing system
- Community features (badges, feedback, mentorship)
- Partner organization support
- Ori AI integration (planned)
- Push notifications
- Geospatial hub assignment

## Documentation

- **[Setup Guide](docs/setup.md)** - Complete setup for backend, frontend, and mobile
- **[Changelog](docs/CHANGELOG.md)** - Project progress, version history, and checkpoint verification
- **[Requirements](docs/requirements.md)** - Feature requirements
- **[Design Document](docs/design.md)** - System architecture and design
- **[Implementation Tasks](docs/tasks.md)** - Task breakdown

## License

See [LICENSE](LICENSE) file for details.
