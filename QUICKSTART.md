# fLOKr Quick Start Guide

## Current Status

✅ Backend setup complete (Django + PostgreSQL + PostGIS)
✅ Frontend setup complete (Next.js + React)
✅ Mobile app ready for setup (React Native + Expo)

## What You Need

### Already Installed
- ✅ Conda environment (`flokr`)
- ✅ PostgreSQL with PostGIS
- ✅ Node.js and npm
- ✅ All Python dependencies

### Need to Install for Mobile
- [ ] Expo CLI: `npm install -g expo-cli`
- [ ] Expo Go app on your phone (from App/Play Store)

## Quick Start

### Option 1: Start Everything at Once
```bash
.\scripts\start-all.bat
```

This opens 3 terminals running:
- Django backend (http://localhost:8000)
- Next.js frontend (http://localhost:3000)
- Expo mobile dev server

### Option 2: Start Services Individually

**Backend:**
```bash
cd backend
python manage.py runserver
```

**Frontend:**
```bash
cd frontend
npm run dev
```

**Mobile:**
```bash
cd mobile
npm install
npm start
```

## First Time Setup

### Mobile App Setup
1. Copy environment file:
   ```bash
   cd mobile
   cp .env.example .env
   ```

2. Edit `mobile/.env` and set your computer's IP:
   ```
   API_BASE_URL=http://YOUR_IP:8000/api
   ```
   Find your IP: Run `ipconfig` and look for IPv4 Address

3. Install Expo Go on your phone (App Store or Play Store)

4. Start mobile dev server:
   ```bash
   npm start
   ```

5. Scan QR code with Expo Go (Android) or Camera (iOS)

## Access Points

- **Frontend Web App:** http://localhost:3000
- **Backend API:** http://localhost:8000/api
- **Admin Panel:** http://localhost:8000/admin
- **Mobile App:** Scan QR code from Expo

## Testing the App

### Frontend
1. Go to http://localhost:3000
2. Click "Get Started" to register
3. Fill in the form and create an account
4. You'll be redirected to onboarding

### Backend API
Test if backend is running:
```bash
.\scripts\check-backend.bat
```

## Troubleshooting

### "Connection Refused" Error
- Make sure Django backend is running: `python manage.py runserver`
- Check http://localhost:8000/api in your browser

### Frontend Won't Load
- Make sure you ran `npm install` in the frontend directory
- Check that `.env.local` exists with `NEXT_PUBLIC_API_URL=http://localhost:8000/api`

### Mobile Can't Connect
- Use your computer's IP address, not `localhost`
- Make sure phone and computer are on same WiFi
- Check firewall isn't blocking port 8000

### Database Issues
Run checkpoint to verify:
```bash
.\scripts\checkpoint.bat
```

## Background Services (Optional)

For reservation expiration and notifications:

**Terminal 1 - Celery Worker:**
```bash
cd backend
celery -A flokr worker -l info --pool=solo
```

**Terminal 2 - Celery Beat:**
```bash
cd backend
celery -A flokr beat -l info --scheduler django_celery_beat.schedulers:DatabaseScheduler
```

## Next Steps

1. Create a superuser for admin access:
   ```bash
   cd backend
   python manage.py createsuperuser
   ```

2. Access admin panel: http://localhost:8000/admin

3. Start building! Check `docs/` for requirements and design docs.

## Need Help?

- Backend docs: `backend/README.md`
- Frontend docs: `frontend/README.md`
- Mobile setup: `mobile/SETUP.md`
- Full docs: `docs/` directory
