# fLOKr Mobile App Setup

## Prerequisites

You need to install:

1. **Node.js** (already installed if frontend works)
2. **Expo CLI** - Install globally:
   ```bash
   npm install -g expo-cli
   ```

3. **Expo Go App** on your phone:
   - iOS: Download from App Store
   - Android: Download from Google Play Store

## Setup Steps

1. **Install dependencies:**
   ```bash
   cd mobile
   npm install
   ```

2. **Create environment file:**
   ```bash
   cp .env.example .env
   ```
   
   Edit `.env` and set:
   ```
   API_URL=http://YOUR_COMPUTER_IP:8000/api
   ```
   
   Replace `YOUR_COMPUTER_IP` with your actual local IP address:
   - Windows: Run `ipconfig` and look for IPv4 Address
   - Example: `API_URL=http://192.168.1.100:8000/api`

3. **Start the development server:**
   ```bash
   npm start
   ```

4. **Run on your device:**
   - Scan the QR code with Expo Go app (Android)
   - Scan with Camera app (iOS) - it will open Expo Go

## Testing Without a Phone

You can use emulators:

### Android Emulator
- Install Android Studio
- Set up an Android Virtual Device (AVD)
- Run: `npm run android`

### iOS Simulator (Mac only)
- Install Xcode
- Run: `npm run ios`

## Troubleshooting

**Can't connect to backend:**
- Make sure Django is running: `python manage.py runserver 0.0.0.0:8000`
- Check your firewall allows connections on port 8000
- Verify your phone and computer are on the same WiFi network

**Expo Go not working:**
- Try running in tunnel mode: `expo start --tunnel`
- This is slower but works across different networks
