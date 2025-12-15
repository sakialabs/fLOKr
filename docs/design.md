# fLOKr Platform Design Document

## Overview

The fLOKr platform is a full-stack web and mobile application designed to connect newcomers with community resources through intelligent resource sharing and mentorship. The system consists of four primary layers:

1. **Web Frontend**: Next.js application providing responsive access for desktop and tablet users
2. **Mobile Frontend**: Expo React Native application providing native iOS/Android access
3. **Backend API**: Django REST Framework providing business logic, data persistence, and API endpoints
4. **Ori AI Layer**: Machine learning services for image tagging, recommendations, demand forecasting, and natural language processing

The platform follows a hub-and-spoke model where physical community hubs serve as inventory centers, with digital coordination enabling efficient resource distribution across neighborhoods and cities. Both web and mobile frontends connect to the same backend API, ensuring feature parity and consistent data access.

## Architecture

### High-Level Architecture

```
┌──────────────────────────┐    ┌──────────────────────────┐
│    Web Frontend          │    │   Mobile Frontend        │
│  (Next.js 15 - SSR)      │    │ (React Native - Native)  │
│  Desktop/Tablet          │    │   iOS/Android            │
└────────────┬─────────────┘    └────────────┬─────────────┘
             │                                │
             └────────────┬───────────────────┘
                          │ HTTPS/REST API
                          │
         ┌────────────────▼────────────────┐
         │      API Gateway Layer          │
         │ (Django REST Framework + Auth)  │
         └────────────────┬────────────────┘
                          │
            ┌─────────────┼─────────────┐
            │             │             │
    ┌───────▼──────┐ ┌───▼────────┐ ┌─▼──────────────┐
    │   Core       │ │  Inventory │ │  Community     │
    │   Services   │ │  Services  │ │  Services      │
    └───────┬──────┘ └───┬────────┘ └─┬──────────────┘
            │            │              │
            └────────────┼──────────────┘
                         │
            ┌────────────▼────────────┐
            │   PostgreSQL Database   │
            └────────────┬────────────┘
                         │
            ┌────────────▼────────────┐
            │     Ori AI Services     │
            │  - Image Tagging (CNN)  │
            │  - Recommendations      │
            │  - Demand Forecasting   │
            │  - NLP/Translation      │
            └─────────────────────────┘
```

### Technology Stack

**Web Frontend:**
- Next.js 15 with App Router
- React 19 with Server Components
- TypeScript (strict mode)
- shadcn/ui component library
- Tailwind CSS with custom design system
- Framer Motion for animations
- Redux Toolkit for client state
- TanStack Query for server state
- next-themes for dark mode
- Sonner for toast notifications

**Mobile Frontend:**
- Expo SDK 49+ (React Native)
- React Navigation for routing
- Redux Toolkit for state management
- Axios for API communication
- Expo Camera for image capture
- Expo Notifications for push notifications

**Backend:**
- Python 3.11+
- Django 4.2+
- Django REST Framework 3.14+
- PostgreSQL 15+ for primary database
- Redis for caching and session management
- Celery for asynchronous task processing

**Ori AI:**
- TensorFlow/PyTorch for ML models
- Pre-trained ResNet50 or EfficientNet for image classification
- Sentence transformers for semantic search
- Prophet or ARIMA for time-series forecasting
- Google Translate API or LibreTranslate for translations

**Infrastructure:**
- Docker for containerization
- AWS/GCP for cloud hosting
- S3/Cloud Storage for image storage
- CloudFront/CDN for static asset delivery

## Frontend Architecture

### Web Frontend (Next.js)

The web frontend provides a responsive, accessible interface for desktop and tablet users, with a focus on stewards, administrators, and users who prefer larger screens.

**Design System:**
- **Color Palette**: Warm and modern with dignity
  - Light mode: Warm teal primary (#1F6F78), soft clay accent (#D97A5B), warm off-white background (#FAF7F2)
  - Dark mode: Muted teal primary (#4FA3A8), softened clay accent (#C26A52), deep warm charcoal background (#121816)
- **Typography**: Inter font family for clarity and warmth
- **Spacing**: Generous whitespace for dignity and ease of use
- **Components**: shadcn/ui for consistency and accessibility

**Key Features:**
- Server-side rendering for performance and SEO
- Dark mode with system preference detection
- Responsive design (mobile-first, scales to desktop)
- Optimistic UI updates for perceived performance
- Skeleton loading states
- Toast notifications for feedback
- Smooth page transitions with Framer Motion

**State Management:**
- Redux Toolkit for client state (auth, UI preferences)
- TanStack Query for server state (API data, caching, mutations)
- Local storage for persistence (auth tokens, theme preference)

**Routing:**
- App Router with file-based routing
- Protected routes with middleware
- Dynamic routes for items, users, hubs
- Parallel routes for modals and sheets

### Mobile Frontend (React Native)

The mobile frontend provides native iOS and Android applications optimized for on-the-go access, particularly for newcomers and community members in the field.

**Key Features:**
- Native performance and feel
- Offline-first architecture with sync
- Camera integration for item photos
- Push notifications for reminders
- GPS integration for hub proximity
- Biometric authentication support

**State Management:**
- Redux Toolkit for all state management
- AsyncStorage for persistence
- Optimistic updates with rollback

**Navigation:**
- Stack navigation for hierarchical flows
- Tab navigation for main sections
- Modal presentation for quick actions

### Shared Patterns

Both frontends share:
- Same API client configuration
- Identical Redux slice structure
- Consistent error handling
- Similar component naming conventions
- Unified design tokens (colors, spacing, typography)

This ensures feature parity and makes it easy to port features between platforms.

## Components and Interfaces

### 1. Authentication & User Management Service

**Responsibilities:**
- User registration and authentication
- Role-based access control (Newcomer, Community Member, Steward, Admin, Partner)
- Profile management
- Session management

**Key Interfaces:**
```python
POST /api/auth/register
POST /api/auth/login
POST /api/auth/logout
GET /api/auth/profile
PUT /api/auth/profile
POST /api/auth/password-reset
```

### 2. Inventory Management Service

**Responsibilities:**
- Item CRUD operations
- Inventory tracking across hubs
- Item categorization and tagging
- Image upload and storage
- Item condition tracking

**Key Interfaces:**
```python
GET /api/inventory/items
POST /api/inventory/items
GET /api/inventory/items/{id}
PUT /api/inventory/items/{id}
DELETE /api/inventory/items/{id}
POST /api/inventory/items/{id}/images
GET /api/inventory/categories
GET /api/hubs/{hub_id}/inventory
```

### 3. Reservation & Borrowing Service

**Responsibilities:**
- Reservation creation and management
- Borrow transaction tracking
- Return processing
- Overdue item management
- Extension requests

**Key Interfaces:**
```python
POST /api/reservations
GET /api/reservations
GET /api/reservations/{id}
PUT /api/reservations/{id}/cancel
POST /api/reservations/{id}/pickup
POST /api/reservations/{id}/return
POST /api/reservations/{id}/extend
GET /api/users/{user_id}/borrowing-history
```

### 4. Hub Management Service

**Responsibilities:**
- Hub CRUD operations
- Hub-user assignment
- Multi-hub inventory coordination
- Hub analytics and reporting

**Key Interfaces:**
```python
GET /api/hubs
POST /api/hubs
GET /api/hubs/{id}
PUT /api/hubs/{id}
GET /api/hubs/{id}/stewards
GET /api/hubs/{id}/analytics
GET /api/hubs/nearby?lat={lat}&lng={lng}
```

### 5. Community & Gamification Service

**Responsibilities:**
- Badge system management
- Reputation scoring
- Leaderboards
- Feedback and incident reporting
- Community guidelines enforcement

**Key Interfaces:**
```python
GET /api/community/badges
GET /api/users/{user_id}/badges
POST /api/community/feedback
POST /api/community/incidents
GET /api/community/leaderboard
GET /api/users/{user_id}/reputation
```

### 6. Mentorship Service

**Responsibilities:**
- Mentor-mentee matching
- Connection management
- In-app messaging
- Mentorship feedback

**Key Interfaces:**
```python
GET /api/mentorship/mentors
POST /api/mentorship/requests
PUT /api/mentorship/requests/{id}/accept
PUT /api/mentorship/requests/{id}/decline
GET /api/mentorship/connections
POST /api/mentorship/messages
GET /api/mentorship/messages?connection_id={id}
```

### 7. Ori AI Service

**Responsibilities:**
- Automatic image tagging and categorization
- Personalized item recommendations
- Demand forecasting
- Natural language Q&A
- Multi-language translation

**Key Interfaces:**
```python
POST /api/ori/tag-image
GET /api/ori/recommendations?user_id={id}
GET /api/ori/forecast?hub_id={id}&category={cat}
POST /api/ori/ask
POST /api/ori/translate
```

### 8. Notification Service

**Responsibilities:**
- Push notification delivery
- Email notifications
- SMS notifications (optional)
- Notification preferences management

**Key Interfaces:**
```python
POST /api/notifications/send
GET /api/notifications
PUT /api/notifications/{id}/read
PUT /api/notifications/preferences
```

### 9. Partner & Analytics Service

**Responsibilities:**
- Partner account management
- Sponsored content management
- Privacy-safe analytics aggregation
- Revenue tracking

**Key Interfaces:**
```python
GET /api/partners
POST /api/partners/sponsorships
GET /api/analytics/platform
GET /api/analytics/hubs/{hub_id}
GET /api/analytics/demand-trends
```

## Data Models

### User Model
```python
{
  "id": "uuid",
  "email": "string",
  "phone": "string",
  "first_name": "string",
  "last_name": "string",
  "role": "enum[newcomer, community_member, steward, admin, partner]",
  "preferred_language": "string",
  "address": "string",
  "location": "point",
  "assigned_hub_id": "uuid",
  "arrival_date": "date",
  "preferences": {
    "clothing_sizes": "object",
    "dietary_restrictions": "array",
    "interests": "array"
  },
  "reputation_score": "integer",
  "badges": "array[badge_id]",
  "is_mentor": "boolean",
  "created_at": "timestamp",
  "updated_at": "timestamp"
}
```

### Hub Model
```python
{
  "id": "uuid",
  "name": "string",
  "address": "string",
  "location": "point",
  "operating_hours": "object",
  "stewards": "array[user_id]",
  "capacity": "integer",
  "current_inventory_count": "integer",
  "status": "enum[active, inactive, maintenance]",
  "created_at": "timestamp",
  "updated_at": "timestamp"
}
```

### InventoryItem Model
```python
{
  "id": "uuid",
  "hub_id": "uuid",
  "name": "string",
  "description": "text",
  "category": "string",
  "tags": "array[string]",
  "condition": "enum[new, excellent, good, fair, poor]",
  "images": "array[url]",
  "quantity_total": "integer",
  "quantity_available": "integer",
  "donor_id": "uuid",
  "status": "enum[active, inactive, damaged, reserved]",
  "created_at": "timestamp",
  "updated_at": "timestamp"
}
```

### Reservation Model
```python
{
  "id": "uuid",
  "user_id": "uuid",
  "item_id": "uuid",
  "hub_id": "uuid",
  "quantity": "integer",
  "status": "enum[pending, confirmed, picked_up, returned, cancelled, overdue]",
  "reservation_date": "timestamp",
  "pickup_date": "date",
  "expected_return_date": "date",
  "actual_return_date": "date",
  "extension_requested": "boolean",
  "extension_approved": "boolean",
  "created_at": "timestamp",
  "updated_at": "timestamp"
}
```

### Badge Model
```python
{
  "id": "uuid",
  "name": "string",
  "description": "text",
  "icon_url": "string",
  "criteria": "object",
  "category": "enum[contribution, mentorship, community, milestone]",
  "created_at": "timestamp"
}
```

### Feedback Model
```python
{
  "id": "uuid",
  "user_id": "uuid",
  "item_id": "uuid",
  "reservation_id": "uuid",
  "type": "enum[positive, negative, incident]",
  "rating": "integer",
  "comment": "text",
  "status": "enum[pending, reviewed, resolved]",
  "created_at": "timestamp"
}
```

### MentorshipConnection Model
```python
{
  "id": "uuid",
  "mentor_id": "uuid",
  "mentee_id": "uuid",
  "status": "enum[requested, active, completed, declined]",
  "start_date": "date",
  "end_date": "date",
  "feedback_mentor": "text",
  "feedback_mentee": "text",
  "created_at": "timestamp",
  "updated_at": "timestamp"
}
```

### Message Model
```python
{
  "id": "uuid",
  "connection_id": "uuid",
  "sender_id": "uuid",
  "content": "text",
  "translated_content": "object",
  "read": "boolean",
  "created_at": "timestamp"
}
```

### DemandForecast Model
```python
{
  "id": "uuid",
  "hub_id": "uuid",
  "category": "string",
  "forecast_date": "date",
  "predicted_demand": "integer",
  "actual_demand": "integer",
  "confidence_score": "float",
  "created_at": "timestamp"
}
```

### Partner Model
```python
{
  "id": "uuid",
  "organization_name": "string",
  "contact_email": "string",
  "subscription_tier": "enum[basic, premium, enterprise]",
  "sponsored_categories": "array[string]",
  "subscription_start": "date",
  "subscription_end": "date",
  "status": "enum[active, expired, suspended]",
  "created_at": "timestamp"
}
```


## Correctness Properties

*A property is a characteristic or behavior that should hold true across all valid executions of a system—essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.*

### User Management Properties

**Property 1: Role-based account creation**
*For any* valid user registration data with a specified role, creating an account should result in a user record with that exact role assigned.
**Validates: Requirements 1.1, 2.1**

**Property 2: Preference data persistence**
*For any* valid preference data submitted during onboarding, the stored user preferences should match the submitted data exactly.
**Validates: Requirements 1.2**

**Property 3: Language preference application**
*For any* supported language code selected by a user, the system should set that language for the interface and enable translation services for that language.
**Validates: Requirements 1.3**

**Property 4: Geographic hub assignment**
*For any* user address and set of hub locations, the assigned hub should be the geographically nearest hub to the user's address.
**Validates: Requirements 1.4, 10.2**

**Property 5: Mentor flag setting**
*For any* user who indicates mentor availability, their profile should have the mentor flag set to true.
**Validates: Requirements 2.3**

### Inventory Management Properties

**Property 6: Inventory quantity conservation**
*For any* borrow transaction, the item's available quantity should decrease by the borrowed amount, and for any return transaction, it should increase by the returned amount, maintaining total quantity invariant.
**Validates: Requirements 3.3, 3.4**

**Property 7: Inactive item exclusion**
*For any* item marked as inactive or damaged, that item should not appear in search results or be available for reservation.
**Validates: Requirements 3.5**

**Property 8: Item detail completeness**
*For any* inventory item, the detail view should contain all required fields: photos, description, condition, available quantity, and pickup location.
**Validates: Requirements 4.2**

**Property 9: Multi-hub inventory transfer conservation**
*For any* inventory transfer between two hubs, the sum of inventory quantities across both hubs should remain constant before and after the transfer.
**Validates: Requirements 10.5**

### Reservation & Borrowing Properties

**Property 10: Available item reservation**
*For any* inventory item with available quantity greater than zero, a reservation request should succeed and create a reservation record with confirmed status.
**Validates: Requirements 4.3**

**Property 11: Automatic reservation expiration**
*For any* reservation where the pickup date has passed and status is still pending, the system should automatically cancel the reservation and restore item availability.
**Validates: Requirements 4.4**

**Property 12: Borrow transaction recording**
*For any* successful item pickup, a borrow transaction record should be created containing the user, item, pickup date, and expected return date.
**Validates: Requirements 4.5**

**Property 13: Extension request workflow**
*For any* active reservation where the borrower requests an extension before the due date, the system should create an extension request that the steward can approve or deny.
**Validates: Requirements 9.5**

**Property 14: Late return restriction policy**
*For any* user who returns items late three or more times, the system should temporarily restrict their borrowing privileges.
**Validates: Requirements 9.4**

### Search & Recommendation Properties

**Property 15: Search result availability**
*For any* search query, all returned items should have available quantity greater than zero and status of active.
**Validates: Requirements 4.1**

**Property 16: Hub-prioritized search ranking**
*For any* user search, results from the user's assigned hub should appear before results from other hubs, with secondary sorting by geographic proximity.
**Validates: Requirements 10.3**

**Property 17: Personalized recommendations generation**
*For any* user with completed preference data, the recommendation engine should generate item suggestions based on their preferences, season, and historical patterns.
**Validates: Requirements 5.1, 5.3**

**Property 18: Complementary item suggestions**
*For any* item being viewed, the recommendation engine should suggest items that are frequently borrowed together with the viewed item.
**Validates: Requirements 5.4**

**Property 19: Language-specific content delivery**
*For any* user with a non-English preferred language, all recommendations, guidance, and interface text should be provided in their preferred language.
**Validates: Requirements 5.5**

### Ori AI Properties

**Property 20: Automatic image tagging**
*For any* uploaded item image, the Ori AI should generate suggested tags and category classification within five seconds.
**Validates: Requirements 3.2**

**Property 21: Natural language question answering**
*For any* natural language question submitted to Ori AI, a response should be generated within ten seconds.
**Validates: Requirements 5.2**

**Property 22: Demand forecast generation**
*For any* hub and item category, the Ori AI should generate demand predictions for the next thirty days based on historical data and seasonal patterns.
**Validates: Requirements 6.1**

**Property 23: High-demand alerting**
*For any* item category where predicted demand exceeds available inventory by fifty percent or more, the system should generate an alert to the hub steward.
**Validates: Requirements 6.2**

**Property 24: Newcomer-adjusted forecasting**
*For any* hub where newcomer registration increases significantly, demand forecasts should be adjusted upward proportionally.
**Validates: Requirements 6.3**

**Property 25: Seasonal demand adjustment**
*For any* seasonal item category (e.g., winter clothing), demand forecasts should increase during the relevant season.
**Validates: Requirements 6.4**

**Property 26: Forecast accuracy tracking**
*For any* time period, the system should calculate and display the difference between predicted and actual demand for accuracy measurement.
**Validates: Requirements 6.5**

### Community & Gamification Properties

**Property 27: Milestone badge awards**
*For any* user who reaches a defined contribution milestone (e.g., 5 items donated, 5 mentorships completed), the system should award the corresponding badge.
**Validates: Requirements 2.4, 7.1, 7.4, 12.5**

**Property 28: Badge notification and profile update**
*For any* badge award event, the system should send a celebration notification to the user and add the badge to their public profile.
**Validates: Requirements 7.2**

**Property 29: Badge visibility**
*For any* user profile being viewed, all earned badges with their descriptions should be visible to the viewer.
**Validates: Requirements 7.3**

**Property 30: Reputation score updates**
*For any* positive feedback submitted about a user, that user's reputation score should increase by a defined amount.
**Validates: Requirements 8.5**

**Property 31: Leaderboard calculation**
*For any* hub and contribution category, the leaderboard should rank users by their contribution count in descending order.
**Validates: Requirements 7.5**

### Feedback & Incident Management Properties

**Property 32: Feedback form accessibility**
*For any* screen state in the application, the feedback form should be accessible through the navigation menu.
**Validates: Requirements 8.1**

**Property 33: Incident notification delivery**
*For any* incident report submitted, a notification should be sent to the relevant hub steward within one minute.
**Validates: Requirements 8.2**

**Property 34: Rating data association**
*For any* rating submitted for a borrowing experience, the rating should be stored with associations to the item, hub, and reservation.
**Validates: Requirements 8.3**

**Property 35: Multi-report item flagging**
*For any* item that receives multiple negative reports (threshold: 3 or more), the system should flag the item for steward review.
**Validates: Requirements 8.4**

### Notification Properties

**Property 36: Scheduled reminder creation**
*For any* confirmed reservation, the system should schedule reminder notifications for one day before pickup and one day before the return due date.
**Validates: Requirements 9.1**

**Property 37: Overdue item reminders**
*For any* reservation where the return date has passed and the item has not been returned, the system should send escalating reminder notifications.
**Validates: Requirements 9.2**

**Property 38: Welcome notification delivery**
*For any* newly created community member account, a welcome notification should be sent within one minute of account creation.
**Validates: Requirements 2.5**

**Property 39: Push notification delivery**
*For any* notification event (reservation, message, alert), a push notification should be delivered to the user's mobile device.
**Validates: Requirements 14.3**

### Hub Management Properties

**Property 40: Hub creation validation**
*For any* hub creation request, the system should validate that all required fields (name, address, operating hours, steward assignments) are present before creating the hub.
**Validates: Requirements 10.1**

**Property 41: Hub dashboard data completeness**
*For any* hub steward viewing their dashboard, the display should include all active reservations, upcoming pickups, and overdue items for that hub.
**Validates: Requirements 9.3**

**Property 42: Platform-wide metrics aggregation**
*For any* administrator viewing the platform dashboard, metrics should be correctly aggregated across all hubs (total users, items, transactions).
**Validates: Requirements 10.4**

### Mentorship Properties

**Property 43: Mentor matching criteria**
*For any* mentor matching request, suggested mentors should share at least one language or interest with the newcomer and be within reasonable geographic proximity.
**Validates: Requirements 12.1**

**Property 44: Mentorship connection activation**
*For any* accepted mentorship request, a connection record should be created with active status and messaging should be enabled between mentor and mentee.
**Validates: Requirements 12.2**

**Property 45: Message persistence and retrieval**
*For any* message sent in a mentorship connection, the message should be stored and retrievable in the message history for that connection.
**Validates: Requirements 12.3**

### Partner & Analytics Properties

**Property 46: Partner account creation**
*For any* valid partner subscription, an account should be created with the specified subscription tier and enhanced visibility permissions.
**Validates: Requirements 11.1**

**Property 47: Sponsored content display**
*For any* item in a sponsored category, the partner's branding should be displayed on the item listing.
**Validates: Requirements 11.2**

**Property 48: Privacy-safe analytics aggregation**
*For any* analytics query by a partner, the returned data should be aggregated such that no individual user can be identified from the results.
**Validates: Requirements 11.3, 13.4**

**Property 49: Partner resource recommendations**
*For any* partner-listed resource, the resource should appear in recommendations for users whose needs match the resource criteria.
**Validates: Requirements 11.4**

**Property 50: Subscription expiration enforcement**
*For any* partner whose subscription end date has passed, sponsored content should be removed and premium analytics access should be revoked.
**Validates: Requirements 11.5**

### Security & Privacy Properties

**Property 51: Sensitive data encryption**
*For any* user account, sensitive personal information fields (email, phone, address) should be encrypted in the database using industry-standard encryption.
**Validates: Requirements 13.1**

**Property 52: Data export completeness**
*For any* user data export request, the export should contain all personal data associated with that user account.
**Validates: Requirements 13.2**

**Property 53: Account deletion data removal**
*For any* account deletion request, all personal identifiable information should be removed or anonymized within thirty days while preserving anonymized transaction records.
**Validates: Requirements 13.3**

**Property 54: Token-based authentication**
*For any* authentication request, the system should issue a secure token with automatic expiration after twenty-four hours of inactivity.
**Validates: Requirements 13.5**

### Mobile & API Properties

**Property 55: Image upload functionality**
*For any* photo captured through the mobile app camera, the image should be successfully uploaded to the backend storage.
**Validates: Requirements 14.2**

**Property 56: Offline functionality**
*For any* loss of internet connectivity, the mobile app should display cached content and queue user actions for synchronization when connectivity is restored.
**Validates: Requirements 14.4**

**Property 57: GPS-based distance calculation**
*For any* user location and hub location, the calculated distance should accurately reflect the geographic distance between the two points.
**Validates: Requirements 14.5**

**Property 58: RESTful JSON responses**
*For any* valid API request, the response should be properly formatted JSON following RESTful conventions.
**Validates: Requirements 15.1**

**Property 59: Error response formatting**
*For any* invalid API request, the response should include an appropriate HTTP status code (400, 401, 404, etc.) and a descriptive error message in JSON format.
**Validates: Requirements 15.2**

**Property 60: Concurrent modification safety**
*For any* concurrent API requests that modify the same inventory item, database transactions should ensure data consistency without race conditions.
**Validates: Requirements 15.4**

**Property 61: API rate limiting**
*For any* user making API requests, the system should enforce a rate limit (maximum 100 requests per minute) and return 429 status code when exceeded.
**Validates: Requirements 15.5**

## Error Handling

### Error Categories

1. **Validation Errors**: Invalid input data (missing required fields, invalid formats, out-of-range values)
2. **Authentication Errors**: Invalid credentials, expired tokens, insufficient permissions
3. **Resource Errors**: Item not found, hub not found, user not found
4. **Business Logic Errors**: Insufficient inventory, reservation conflicts, overdue restrictions
5. **External Service Errors**: Ori AI service unavailable, translation service failure, notification delivery failure
6. **System Errors**: Database connection failures, network timeouts, unexpected exceptions

### Error Handling Strategy

**API Error Responses:**
All API errors should return consistent JSON structure:
```json
{
  "error": {
    "code": "ERROR_CODE",
    "message": "Human-readable error message",
    "details": {},
    "timestamp": "ISO-8601 timestamp"
  }
}
```

**Mobile App Error Handling:**
- Display user-friendly error messages
- Provide actionable recovery steps
- Log errors for debugging
- Gracefully degrade functionality when services are unavailable

**Retry Logic:**
- Implement exponential backoff for transient failures
- Maximum 3 retry attempts for external service calls
- Circuit breaker pattern for Ori AI services

**Logging:**
- Log all errors with context (user ID, request ID, stack trace)
- Use structured logging (JSON format)
- Separate log levels: DEBUG, INFO, WARNING, ERROR, CRITICAL
- Integrate with monitoring service (e.g., Sentry, DataDog)

## Testing Strategy

### Unit Testing

The platform will use comprehensive unit testing to verify individual components and functions:

**Backend (Python/Django):**
- Framework: pytest with pytest-django
- Coverage target: 80% minimum
- Focus areas:
  - Model validation and business logic
  - API serializers and validators
  - Service layer functions
  - Utility functions (distance calculation, date handling)
  - Permission and authentication logic

**Frontend (React Native):**
- Framework: Jest with React Native Testing Library
- Coverage target: 70% minimum
- Focus areas:
  - Component rendering and props
  - Navigation flows
  - State management (Redux actions and reducers)
  - API integration layer
  - Utility functions

**Ori AI Services:**
- Framework: pytest
- Focus areas:
  - Image classification accuracy
  - Recommendation algorithm correctness
  - Forecast calculation logic
  - Translation integration

### Property-Based Testing

Property-based testing will verify that universal correctness properties hold across all inputs:

**Framework Selection:**
- Backend: Hypothesis (Python property-based testing library)
- Frontend: fast-check (JavaScript/TypeScript property-based testing library)

**Configuration:**
- Minimum 100 iterations per property test
- Use shrinking to find minimal failing examples
- Seed random generation for reproducibility

**Property Test Requirements:**
- Each property-based test MUST be tagged with a comment referencing the design document property
- Tag format: `# Feature: flokr-platform, Property {number}: {property_text}`
- Each correctness property MUST be implemented by a SINGLE property-based test
- Property tests should use smart generators that constrain inputs to valid ranges

**Key Property Tests:**

1. **Inventory Conservation** (Property 6, 9): Generate random sequences of borrow/return/transfer operations and verify total inventory remains constant
2. **Geographic Assignment** (Property 4): Generate random user locations and hub locations, verify nearest hub is always selected
3. **Search Result Validity** (Property 15): Generate random search queries, verify all results have available quantity > 0
4. **Hub Prioritization** (Property 16): Generate random user/hub configurations, verify assigned hub appears first in results
5. **Badge Award Thresholds** (Property 27): Generate random contribution sequences, verify badges awarded at exact thresholds
6. **Privacy Aggregation** (Property 48): Generate random user data and analytics queries, verify no individual users identifiable
7. **Rate Limiting** (Property 61): Generate request sequences exceeding limits, verify 429 responses at correct thresholds
8. **Concurrent Safety** (Property 60): Generate concurrent modification scenarios, verify no data corruption

### Integration Testing

Integration tests will verify that components work together correctly:

**API Integration Tests:**
- Test complete user workflows (registration → onboarding → search → reserve → borrow → return)
- Test multi-hub scenarios
- Test Ori AI integration points
- Test notification delivery pipelines
- Test partner analytics access

**Database Integration:**
- Test transaction isolation
- Test concurrent access patterns
- Test data migration scripts

**External Service Integration:**
- Mock external services (translation, image storage) for most tests
- Maintain small suite of real integration tests for critical paths

### End-to-End Testing

**Framework:** Detox (React Native E2E testing)

**Test Scenarios:**
- Complete newcomer onboarding flow
- Item search and reservation flow
- Mentor matching and messaging flow
- Hub steward inventory management flow
- Partner analytics access flow

**Test Environment:**
- Dedicated staging environment with test data
- Automated E2E test runs on CI/CD pipeline
- Manual exploratory testing before releases

### Performance Testing

**Load Testing:**
- Simulate 1000 concurrent users
- Test API response times under load
- Test database query performance
- Identify bottlenecks and optimize

**Ori AI Performance:**
- Image tagging: < 5 seconds (Property 20)
- Question answering: < 10 seconds (Property 21)
- Recommendation generation: < 2 seconds

**Tools:** Apache JMeter or Locust for load testing

### Testing Workflow

1. **Development**: Write implementation code first
2. **Unit Tests**: Write unit tests for new functionality
3. **Property Tests**: Write property-based tests for correctness properties
4. **Integration Tests**: Update integration tests for new workflows
5. **Verification**: Run all tests locally before committing
6. **CI/CD**: Automated test execution on pull requests
7. **Staging**: E2E tests on staging environment
8. **Production**: Monitoring and error tracking

## Implementation Phases

### Phase 1: Core Platform (Months 1-2)

**Infrastructure Setup:**
- Django project structure with apps: users, inventory, reservations, hubs, community
- PostgreSQL database with initial schema
- Redis for caching and Celery for background tasks
- Expo React Native project with navigation structure
- CI/CD pipeline (GitHub Actions or GitLab CI)

**Core Features:**
- User authentication and registration
- Basic user profiles with roles
- Hub CRUD operations
- Inventory item CRUD operations
- Basic search functionality
- Reservation creation and management

**Testing:**
- Unit tests for models and API endpoints
- Property tests for inventory conservation and geographic assignment
- Basic integration tests

### Phase 2: Ori AI Integration (Month 2-3)

**AI Services:**
- Image classification model deployment (ResNet50 or EfficientNet)
- Auto-tagging service integration
- Basic recommendation engine (collaborative filtering)
- FAQ knowledge base and Q&A system

**Features:**
- Automatic item tagging on upload
- Personalized item recommendations
- Natural language question answering
- Basic demand forecasting

**Testing:**
- Unit tests for AI service integration
- Property tests for recommendation quality
- Performance tests for AI response times

### Phase 3: Community Features (Month 3-4)

**Features:**
- Badge system and achievement tracking
- Reputation scoring
- Feedback and incident reporting
- Leaderboards
- Notification system (push, email)
- Reminder scheduling

**Testing:**
- Property tests for badge awards and reputation
- Integration tests for notification delivery
- E2E tests for feedback workflows

### Phase 4: Mentorship & Multi-Hub (Month 4-5)

**Features:**
- Mentor matching algorithm
- In-app messaging system
- Multi-hub inventory coordination
- Hub transfer functionality
- Advanced demand forecasting with seasonal adjustments

**Testing:**
- Property tests for mentor matching criteria
- Property tests for multi-hub inventory conservation
- Integration tests for messaging
- E2E tests for mentorship workflows

### Phase 5: Partner Integration & Analytics (Month 5-6)

**Features:**
- Partner account management
- Sponsored content system
- Privacy-safe analytics dashboard
- Revenue tracking
- Advanced Ori AI features (translation, guidance)

**Testing:**
- Property tests for privacy aggregation
- Integration tests for partner workflows
- Security testing for data access controls

### Phase 6: Polish & Scale (Month 6+)

**Features:**
- Performance optimization
- Advanced caching strategies
- Database query optimization
- Mobile app polish and UX improvements
- Comprehensive error handling
- Monitoring and alerting setup

**Testing:**
- Load testing and performance benchmarking
- Security audit
- Accessibility testing
- User acceptance testing

## Deployment Architecture

### Production Environment

**Application Tier:**
- Django application servers (Gunicorn) behind load balancer
- Auto-scaling based on CPU/memory usage
- Health check endpoints for load balancer

**Database Tier:**
- PostgreSQL primary with read replicas
- Automated backups (daily full, hourly incremental)
- Point-in-time recovery capability

**Caching Tier:**
- Redis cluster for session storage and caching
- Cache invalidation strategy for inventory updates

**Storage Tier:**
- S3/Cloud Storage for images and static files
- CDN for global content delivery

**AI Services:**
- Separate service tier for Ori AI
- GPU instances for image classification
- Model versioning and A/B testing capability

**Monitoring:**
- Application performance monitoring (APM)
- Error tracking and alerting
- Log aggregation and analysis
- Uptime monitoring

### Security Considerations

**Authentication & Authorization:**
- JWT tokens for API authentication
- Role-based access control (RBAC)
- OAuth2 for partner integrations

**Data Security:**
- Encryption at rest for sensitive data
- Encryption in transit (TLS 1.3)
- Regular security audits
- Penetration testing

**Privacy Compliance:**
- GDPR compliance for European users
- Data retention policies
- User consent management
- Privacy policy and terms of service

**API Security:**
- Rate limiting per user and IP
- Input validation and sanitization
- SQL injection prevention (ORM usage)
- XSS prevention
- CSRF protection

## Success Metrics

### User Engagement Metrics
- Daily active users (DAU) and monthly active users (MAU)
- User retention rate (7-day, 30-day)
- Average session duration
- Items borrowed per user per month
- Mentor-mentee connection rate

### Platform Health Metrics
- Item availability rate (% of time items are available)
- Average reservation fulfillment time
- Return rate (% of items returned on time)
- Hub utilization rate
- Inventory turnover rate

### AI Performance Metrics
- Image tagging accuracy
- Recommendation click-through rate
- Forecast accuracy (MAPE - Mean Absolute Percentage Error)
- Q&A response relevance score
- Translation quality score

### Business Metrics
- Partner subscription revenue
- Sponsored content engagement
- Cost per newcomer served
- Platform operating costs
- Revenue per hub

### Community Health Metrics
- Badge distribution across users
- Average reputation score
- Feedback sentiment (positive vs negative)
- Incident resolution time
- Community contribution rate

## Future Enhancements

### Short-term (6-12 months)
- Mobile web version for broader accessibility
- Advanced search filters and saved searches
- Recurring reservation scheduling
- Group borrowing for families
- Volunteer opportunity matching

### Medium-term (1-2 years)
- Multi-city expansion toolkit
- White-label platform for other organizations
- Blockchain-based reputation system
- Advanced AI personalization
- Integration with local transit systems

### Long-term (2+ years)
- Global platform with multi-currency support
- Marketplace for services (not just items)
- Carbon footprint tracking for sustainability
- AI-powered community health monitoring
- Predictive intervention for at-risk newcomers
