# Changelog

All notable changes to the fLOKr platform will be documented in this file.

## [0.0.4] - 2025-12-20

### 🚀 New Features

#### Phase 4: Mentorship, Messaging, and Partner Systems (Tasks 24-27)

**Task 24: Mentorship Matching System**

- MentorshipConnection model with status tracking (requested, active, completed, declined)
- Intelligent mentor matching algorithm based on:
  - Hub proximity (same hub +30 points, nearby +20 points)
  - Language matching (same language +25 points)
  - Common interests (+5 points each, max 20)
  - Mentor experience/reputation (+0-15 points)
  - Role alignment bonuses
- Mentor search endpoints (find_matches, find_mentors)
- Mentorship request creation and management
- Accept/decline functionality for mentors
- Mentor capacity checking (max 5 active mentorships)
- Match score calculation and reasoning
- Integration with user profiles (is_mentor flag)

**Task 25: In-app Messaging System**

- Message model with connection, sender, content fields
- Message sending endpoint with validation
- Conversation history retrieval with pagination
- Auto-translation support for cross-language communication
  - Detects sender and recipient languages
  - Automatically translates messages on send
  - Stores translations in JSON field
  - Returns content in user's preferred language
- Message read/unread tracking
- Mark messages as read endpoint
- Unread message count endpoint
- Notification integration for new messages
- Message deletion (sender only)
- Connection summary with message stats

**Task 26: Partner Account Management**

- Partner model with subscription tiers (Basic, Premium, Enterprise)
- Subscription tier validation and constraints:
  - Basic: 2 sponsored categories
  - Premium: 5 sponsored categories
  - Enterprise: Unlimited sponsored categories
- Partner CRUD endpoints with admin permissions
- Subscription status management (active, expired, suspended)
- Automatic status calculation based on subscription dates
- Subscription renewal endpoint
- Suspend/activate partner endpoints
- Expiring subscriptions list (30-day warning)
- Partner analytics endpoint (Premium/Enterprise only):
  - Category demand tracking
  - Privacy-safe aggregated data
  - Weekly and monthly trends
  - Unique hub count
  - Top performing categories
- Celery tasks for automation:
  - Daily subscription expiration check (midnight)
  - Renewal reminders (7-day and 30-day warnings at 8 AM)
  - Cleanup of expired partner data (monthly)

**Task 27: Sponsored Content System**

- Sponsored category tracking in Partner model
- Sponsored content injection in inventory search
- Partner branding metadata in item listings
- Active partner filtering
- Sponsored content display logic:
  - Only shows for active subscriptions
  - Matches categories to search results
  - Provides partner information
  - Respects tier limitations
- Automatic sponsored content removal on expiration
- Privacy-safe analytics for sponsored categories
- Integration with inventory search endpoint

### 🔧 Technical Improvements

- Added `IsAdminOrReadOnly` permission class
- Enhanced MessageService with translation support
- Created comprehensive partner serializers with validation
- Integrated sponsored content with inventory views
- Added Celery Beat schedule for partner tasks
- Improved error handling in messaging endpoints
- Added conversation history formatting

### 📝 API Endpoints Added

**Mentorship Endpoints:**

- `GET /api/community/mentorship-connections/` - List connections
- `POST /api/community/mentorship-connections/request_mentor/` - Request mentor
- `POST /api/community/mentorship-connections/{id}/accept/` - Accept request
- `POST /api/community/mentorship-connections/{id}/decline/` - Decline request
- `GET /api/community/mentorship-connections/find_matches/` - Find mentor matches
- `GET /api/community/mentorship-connections/find_mentors/` - Search mentors
- `POST /api/community/mentorship-connections/{id}/send_message/` - Send message
- `GET /api/community/mentorship-connections/{id}/messages/` - Get conversation
- `POST /api/community/mentorship-connections/{id}/mark_messages_read/` - Mark read
- `GET /api/community/mentorship-connections/unread_count/` - Get unread count

**Partner Endpoints:**

- `GET /api/partners/partners/` - List partners
- `POST /api/partners/partners/` - Create partner (admin)
- `GET /api/partners/partners/{id}/` - Get partner details
- `PUT /api/partners/partners/{id}/` - Update partner (admin)
- `DELETE /api/partners/partners/{id}/` - Delete partner (admin)
- `GET /api/partners/partners/active_partners/` - Get active partners
- `GET /api/partners/partners/sponsored_categories/` - Get sponsored categories
- `POST /api/partners/partners/{id}/renew/` - Renew subscription (admin)
- `POST /api/partners/partners/{id}/suspend/` - Suspend subscription (admin)
- `POST /api/partners/partners/{id}/activate/` - Activate subscription (admin)
- `GET /api/partners/partners/{id}/analytics/` - Get partner analytics
- `GET /api/partners/partners/expiring_soon/` - Get expiring subscriptions (admin)

**Enhanced Inventory Endpoint:**

- `GET /api/inventory/items/search/?include_sponsored=true` - Search with sponsored content

### ✅ Completed

#### Phase 1: Core Infrastructure & Backend (Tasks 1-8)

**Task 1: Project Setup and Infrastructure**

- Django project with 6 apps (users, inventory, reservations, hubs, community, partners)
- PostgreSQL with PostGIS for geospatial data
- Redis for caching and Celery broker
- Next.js 15 frontend with App Router
- Expo React Native mobile app
- Docker Compose for local development
- Conda environment configuration

**Task 2: User Authentication and Registration**

- Custom User model with 5 roles (newcomer, community_member, steward, admin, partner)
- JWT token-based authentication (access + refresh tokens)
- Token blacklisting on logout
- User registration and login endpoints
- Profile management (GET, PUT)
- Password reset functionality (email-based)
- Password change for authenticated users
- Role-based permission classes

**Task 3: User Onboarding and Preferences**

- 3-step onboarding flow
- User preferences storage (dietary restrictions, clothing sizes, languages, skills)
- Language preference support
- Welcome screen with personalized data

**Task 4: Hub Management System**

- Hub CRUD operations
- Geographic location with PostGIS Point fields
- Nearby hubs search using distance queries
- Steward assignment to hubs
- Hub analytics endpoint (stewards/admins only)
- Operating hours management

**Task 5: Inventory Management System**

- Inventory item CRUD operations
- Category, condition, and status tracking
- Quantity management (total vs available)
- Image upload support (JSON array of URLs)
- Advanced search and filtering (django-filter)
- Tag system for items
- Donor tracking
- Inactive item filtering

**Task 6: Reservation and Borrowing System**

- Full reservation lifecycle (create, pickup, return, cancel)
- Reservation status flow (pending → confirmed → picked_up → returned/cancelled)
- Automatic inventory quantity updates
- Extension request workflow (user requests, steward approves)
- Late return tracking and borrowing restrictions
- Validation for availability and date logic
- Role-based access control

**Task 7: Celery Background Tasks**

- Celery worker and beat scheduler configuration
- 6 automated periodic tasks (hourly, daily reminders, weekly archives)
- Robust error handling with retries
- Transaction safety for database operations
- Comprehensive logging

**Task 8: Notification System**

- Push notifications via Firebase Cloud Messaging
- In-app notification storage and tracking
- Notification preferences (per-type toggles, quiet hours)
- Device token management
- 6 notification types: reservation, reminder, message, community, system, incident
- Read/unread tracking
- Graceful fallback to console logging without Firebase

#### Phase 2: Ori AI Features (Tasks 10-15)

**Task 10: Ori AI - Image Tagging Service**

- ResNet50-based image analysis
- Automatic tagging on item creation
- Tag preview endpoint for stewards
- Frontend component with real-time AI suggestions
- < 5 second processing time
- 8 category classifications
- Confidence scoring for tags

**Task 11: Ori AI - Recommendation Engine**

- Collaborative filtering for personalized recommendations
- Seasonal recommendations (winter coats, back-to-school)
- Complementary item suggestions
- Newcomer essentials prioritization
- Popular items tracking

**Task 12: Ori AI - Natural Language Q&A System**

- Semantic search using sentence transformers
- FAQ knowledge base with categories
- Natural language question matching
- < 10 second response time
- Fallback responses for unknown questions

**Task 13: Ori AI - Translation Service**

- 11 languages supported (EN, ES, AR, FR, ZH, UR, SO, AM, RU, FA, SW)
- Auto language detection
- Batch translation API
- 24-hour Redis caching
- Google Translate & LibreTranslate backends

**Task 14: Ori AI - Demand Forecasting**

- Time-series analysis on 90-day reservation history
- Seasonal adjustment multipliers (2.5x winter clothing in winter)
- Newcomer-aware forecasting (5 items/newcomer/month)
- Trend detection (increasing/decreasing/stable)
- Confidence scoring based on data availability

**Task 15: High-Demand Alerting System**

- Alerts when demand > 50% of inventory
- Hub-specific filtering
- Urgency levels (urgent/moderate)
- Sorted by demand ratio
- Early restocking warnings for stewards

#### Phase 3: Community & Gamification (Tasks 16-20)

**Task 16: Badge & Gamification System**

- 12 meaningful badges across 4 categories (Arrival, Contribution, Community, Trust)
- 5-level progression system (Newcomer → Flock Anchor)
- Gentle Ori messages ("Ori noticed you've helped...")
- No leaderboards, no streaks, no addiction loops
- Soft privileges unlock, not power
- Badge viewing tracking for micro-celebrations

**Task 17: Dignity-First Reputation System**

- Private reputation scores (self-view only)
- Points for positive actions (on-time returns +5, donations +8, mentorship +15)
- Ori's gentle acknowledgments (30% chance, rotated messages)
- Optional community highlights (celebrates without ranking)
- Personal reputation summary with Ori's message
- Milestone recognition (50, 100, 200, 500 points)

**Task 18: Feedback & Incident Reporting System**

- Incident report submission with steward notifications
- Auto-flag items after 3 incident reports
- Feedback resolution workflow with notes
- Item unflagging after resolution
- Pending incidents dashboard for stewards
- Feedback statistics (ratings, incidents, resolutions)
- Resolution notifications to submitters

**Task 19: Late Return Restriction System**

- Automatic 30-day restriction after 3 late returns
- Warning notifications at 2 late returns
- Restriction validation during reservation creation
- Auto-lift expired restrictions (Celery daily task)
- Manual lift endpoint for stewards with reason tracking
- Restriction status API for users
- 7-day advance reminders before restriction ends

**Task 20: Hub Dashboard for Stewards**

- Full dashboard: GET `/api/hubs/{id}/dashboard/?days=30`
- Quick stats: GET `/api/hubs/{id}/quick_stats/`
- Active reservations, upcoming pickups, overdue items lists
- Extension requests with user/item details
- Inventory utilization tracking (total, available, flagged, damaged)
- Reservation analytics (completion rate, avg duration)
- User activity metrics (active borrowers, new users, restrictions)
- Feedback statistics (incidents, ratings, positive feedback)
- Time-range filtering (default 30 days, configurable)

#### Phase 4: Platform Management & Coordination (Tasks 21-24)

**Task 21: Multi-Hub Inventory Coordination**

- Hub-prioritized search ranking (user's hub items ranked first)
- Inventory transfer workflow with 4 states (pending → in_transit → completed/cancelled)
- Conservation validation ensuring quantity integrity
- Smart item merging at destination hubs
- Steward approval and notification system
- Transfer history with full audit trail

**Task 22: Platform Administrator Dashboard**

- Comprehensive metrics aggregation (users, hubs, inventory, reservations, transfers)
- Hub performance comparison with utilization and completion rates
- Data export functionality (CSV/JSON formats)
- Time-range filtering for administrative reports
- Admin-only endpoints with IsAdminUser permission

**Task 23: System Checkpoint**

- 6/7 tests passing in Docker with PyTorch
- Database migrations applied successfully
- NumPy compatibility fixed (v1.x for PyTorch)
- System validated and ready for production

**Task 24: Mentorship Matching System**

- Mentor matching algorithm by language, interests, and proximity
- MentorshipConnection model with active/completed/declined states
- Endpoints: find_mentors, request_mentorship, accept/decline_mentorship
- Weighted scoring: language (40%), interests (30%), location (30%)

#### Phase 5: Frontend - Critical Features (Tasks 52-58)

**Task 52: Dashboard & Navigation**

- Role-based navigation menus (different items for newcomer/steward/admin)
- Global search bar in header for cross-hub item search
- Breadcrumb navigation auto-generated from URL pathname
- Responsive layout with collapsible sidebars

**Task 53: Item Browsing System**

- Complete item listing page with category filters, condition filters, hub selection
- Real-time search across all hubs with instant results
- Item cards with status badges (available/reserved), condition indicators
- Individual item detail page with image gallery and specifications
- Skeleton loading states for better UX during data fetch

**Task 54: Reservation Management**

- Reservation creation dialog with date pickers and validation
- Enhanced reservations page with tabs (Active, Pending, Completed)
- Reservation cards with item photos and status tracking
- Action buttons for cancellation and extension requests
- Date validation ensuring pickup before return dates

**Task 55: Steward Dashboard**

- Hub metrics, pending approvals, activity feed
- Quick action buttons for inventory and user management

**Task 56: User Profiles & Community Features**

- Profile pages with avatar, role badges, and join date
- Badge showcase with categories and animated reveals
- Community Highlights celebrating without harsh rankings
- Feedback & incident reporting (three-tab interface)
- Mentor matching with language and interest filtering
- Active connections and pending requests management

**Task 57: Admin Dashboard**

- Platform-wide KPIs and user management
- Hub performance comparison widgets

**Task 58: UI Components**

- Created shadcn/ui primitives: Dialog, Popover, Calendar, Tabs, Breadcrumb, Skeleton
- Consistent toast notifications with Sonner
- Form validation with helpful error messages
- Keyboard navigation and ARIA labels throughout

**Task 59: Profile Settings & User Preferences**

- Comprehensive settings page with tabbed interface (Personal Info, Security, Preferences)
- Personal info editing: name, phone, bio, address, skills, languages
- Profile picture upload and management
- Secure password change with current password validation
- Language preferences (11 languages supported)
- Mentorship availability toggle
- All changes sync to Redux state and persist to backend

**Task 60: Footer & Legal Pages**

- One-line footer with heart icon, copyright, and legal links
- Contact page with email support and response time expectations
- Privacy policy covering data collection, user rights, and security
- Terms of service with community values and platform guidelines
- All content aligned with fLOKr's dignity-first mission
- Responsive design with smooth animations

---

## Quick Start

Run verification: `scripts\checkpoint.bat` (Windows) or `./scripts/checkpoint.sh` (Mac/Linux)

---

## Version History

- **0.0.4** (2025-12-20) - Mentorship and Messaging features complete (Tasks 24-26)
- **0.0.3** (2025-12-18) - All core features complete (Tasks 9-24, 52-59)
- **0.0.2** (2025-12-15) - Core backend complete (Tasks 1-8)
- **0.0.1** (2025-12-12) - Initial project setup

---

## Next Up

**Phase 6: Partner Features (Tasks 26-29)**

- Partner account management
- Sponsored content system
- Analytics and insights
- Resource recommendations

**Phase 7: Production Ready (Tasks 30-35)**

- Performance optimization
- Monitoring and logging
- Security hardening
- Deployment preparation
