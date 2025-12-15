# fLOKr Mobile App

React Native mobile application built with Expo for iOS and Android.

## Current Status

✅ **Completed:**
- Project structure with navigation
- API client setup
- Redux store configuration
- API services (auth, hubs, inventory, reservations, notifications)

🔄 **Next:**
- Authentication screens
- Onboarding flow
- Dashboard with reservations
- Inventory browsing
- Camera for item photos
- Push notifications setup
- Location services for nearby hubs

## Prerequisites

- Node.js 18+ and npm
- Expo CLI: `npm install -g expo-cli`
- For iOS: Xcode (Mac only)
- For Android: Android Studio

## Installation

1. Install dependencies:
```bash
npm install
```

2. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your backend API URL
```

## Running the App

Start the Expo development server:
```bash
npm start
```

This will open Expo DevTools in your browser. From there you can:
- Press `i` to open iOS simulator
- Press `a` to open Android emulator
- Scan QR code with Expo Go app on your physical device

Or run directly:
```bash
npm run ios     # iOS simulator
npm run android # Android emulator
```

## API Services

All backend endpoints are integrated via `src/api/services.ts`:

- **Auth** - Login, register, profile management
- **Hubs** - List, nearby search (GPS-based)
- **Inventory** - Browse, search, create items
- **Reservations** - Full lifecycle (create, pickup, return, extend)
- **Notifications** - Push notifications, preferences, device tokens

## Environment Variables

```env
API_URL=http://localhost:8000
```

For physical device testing, use your computer's IP:
```env
API_URL=http://192.168.1.X:8000
```

## Project Structure

```
mobile/
├── src/
│   ├── api/          # API client and services
│   ├── navigation/   # Navigation configuration
│   ├── screens/      # Screen components
│   │   ├── auth/     # Authentication screens
│   │   └── home/     # Home screens
│   └── store/        # Redux store
│       └── slices/   # Redux slices
├── App.tsx           # Root component
├── app.json          # Expo configuration
└── package.json      # Dependencies
```

## Testing

Run tests:
```bash
npm test
```

## Building for Production

### iOS
```bash
expo build:ios
```

### Android
```bash
expo build:android
```

## Troubleshooting

### TypeScript Errors
If you see TypeScript errors, make sure all dependencies are installed:
```bash
npm install
```

### Metro Bundler Issues
Clear the cache:
```bash
expo start -c
```

### Module Not Found
Delete node_modules and reinstall:
```bash
rm -rf node_modules
npm install
```
