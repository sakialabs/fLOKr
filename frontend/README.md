# fLOKr Web Frontend

Next.js 15 web application with shadcn/ui and Framer Motion for desktop and tablet access.

## Current Status

✅ **Completed:**
- Authentication (login, register, JWT tokens)
- User onboarding (3-step flow with preferences)
- API client with auto token refresh
- Protected routes middleware
- Redux store setup
- Warm design system (light/dark modes)

🔄 **In Progress:**
- Dashboard UI
- Inventory browsing
- Reservation management
- Notifications UI

## Tech Stack

- **Next.js 15** - App Router with React Server Components
- **TypeScript** - Strict mode enabled
- **shadcn/ui** - Beautiful, accessible component library
- **Tailwind CSS** - Utility-first styling with custom design system
- **Framer Motion** - Smooth animations and transitions
- **Redux Toolkit** - State management
- **Axios** - API client
- **Sonner** - Toast notifications
- **next-themes** - Dark mode support

## Design System

### Light Mode
- **Background**: Warm Off-White (#FAF7F2)
- **Primary**: Warm Deep Teal (#1F6F78)
- **Secondary**: Soft Clay/Terracotta (#D97A5B)
- **Text**: Charcoal (#2B2B2B)
- **Success**: Muted Sage Green (#6FAF8E)
- **Warning**: Soft Amber (#F2B705)

### Dark Mode
- **Background**: Deep Warm Charcoal (#121816)
- **Surface**: Warm Dark Slate (#1C2422)
- **Primary**: Teal Muted (#4FA3A8)
- **Accent**: Clay Softened (#C26A52)
- **Text**: Warm White (#E6ECE8)
- **Success**: Sage (#6FAF8E)
- **Warning**: Amber Dimmed (#D9A441)

## Installation

1. Install dependencies:
```bash
npm install
```

2. Install shadcn/ui components (Day 1 essentials):
```bash
npx shadcn@latest add button
npx shadcn@latest add input
npx shadcn@latest add textarea
npx shadcn@latest add select
npx shadcn@latest add card
npx shadcn@latest add badge
npx shadcn@latest add avatar
npx shadcn@latest add alert
npx shadcn@latest add sonner
npx shadcn@latest add separator
```

3. Set up environment variables:
```bash
cp .env.example .env.local
# Edit .env.local with your backend API URL
```

## Running the App

Start the development server:
```bash
npm run dev
```

The app will be available at `http://localhost:3000`

## Building for Production

```bash
npm run build
npm start
```

## Project Structure

```
frontend/
├── src/
│   ├── app/              # Next.js App Router pages
│   │   ├── login/        # Authentication pages
│   │   ├── dashboard/    # Dashboard pages
│   │   └── layout.tsx    # Root layout
│   ├── components/       # React components
│   │   ├── ui/           # shadcn/ui components
│   │   ├── auth/         # Auth components
│   │   └── dashboard/    # Dashboard components
│   ├── lib/              # Utilities
│   │   ├── utils.ts      # Helper functions
│   │   └── api.ts        # API client
│   └── store/            # Redux store
│       └── slices/       # Redux slices
├── public/               # Static assets
└── components.json       # shadcn/ui config
```

## Adding More shadcn/ui Components

When you need additional components:

```bash
# Soon after
npx shadcn@latest add dialog
npx shadcn@latest add sheet
npx shadcn@latest add tabs
npx shadcn@latest add dropdown-menu
npx shadcn@latest add skeleton
npx shadcn@latest add tooltip

# Nice to have
npx shadcn@latest add table
npx shadcn@latest add calendar
npx shadcn@latest add command
npx shadcn@latest add pagination
```

## Design Philosophy

**Warm and Modern** - fLOKr is about arrival, trust, and dignity. The design reflects:
- Warmth through earthy tones (teal, clay, sage)
- Dignity through generous spacing and clear hierarchy
- Trust through consistent, accessible patterns
- Not loud, not sterile - just right

## Testing

Run tests:
```bash
npm test
```

Watch mode:
```bash
npm run test:watch
```

## API Services

All backend endpoints are integrated via `src/lib/api-services.ts`:

- **Auth** - Login, register, profile, password reset
- **Hubs** - List, nearby search, details
- **Inventory** - Browse, search, create items
- **Reservations** - Create, cancel, pickup, return, extend
- **Notifications** - List, mark read, preferences, device tokens

## Environment Variables

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## Next Steps

1. Build dashboard UI with reservation list
2. Create inventory browsing screens
3. Add notification bell with unread count
4. Implement reservation flow
5. Add hub map view
6. Build steward inventory management UI
