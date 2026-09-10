# 02. System Architecture — MumtaAI

## Architectural Topology
MumtaAI is structured as a decoupled, multi-tier distributed system composed of four major environments:
1. **Client Tier**: Modern web browser running React 19 Client Components, Web Audio API, and the Web Bluetooth API.
2. **Web Application & API Gateway**: Next.js 15 App Router running on Node.js runtime, serving dynamic SSR/client pages and 94 REST API endpoints.
3. **Audio & ML Inference Engine**: Dedicated Python 3.10+ service powered by FastAPI and Uvicorn, performing audio preprocessing, spectral transformation, and multi-model cry classification.
4. **Cloud Infrastructure & Data Platform**:
   - **Supabase**: Managed PostgreSQL 15 database, GoTrue JWT authentication, Row-Level Security (RLS), and S3-compatible private/public Storage buckets.
   - **Stripe**: Global payment gateway processing subscriptions, handling checkout redirect flows, and broadcasting asynchronous webhook events.

```text
                                  ┌────────────────────────┐
                                  │   Bluetooth Oximeter   │
                                  │   (PC-60F / NUS BLE)   │
                                  └───────────┬────────────┘
                                              │ Web Bluetooth GATT
                                              ▼
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                                    USER BROWSER                                        │
│  ┌───────────────────────┐  ┌─────────────────────────┐  ┌──────────────────────────┐  │
│  │     Next.js Client    │  │    Oximeter Context     │  │   ProcessingProgress     │  │
│  │    React 19 / State   │  │   AA 55 Packet Decoder  │  │   Audio MediaRecorder    │  │
│  └───────────┬───────────┘  └────────────┬────────────┘  └────────────┬─────────────┘  │
└──────────────┼───────────────────────────┼────────────────────────────┼────────────────┘
               │                           │                            │
               │ HTTPS REST                │ Readings / Alerts          │ Direct SSE Stream
               ▼                           ▼                            ▼
┌─────────────────────────────────────────────────────────┐  ┌───────────────────────────┐
│               NEXT.js 15 APP ROUTER                     │  │    PYTHON FASTAPI ML      │
│  ┌───────────────────────────────────────────────────┐  │  │        SERVICE            │
│  │ Middleware Auth & Session Gate                    │  │  │                           │
│  │ (src/middleware.ts -> updateSession)              │  │  │  - /api/streaming/        │
│  └─────────────────────┬─────────────────────────────┘  │  │    process-audio          │
│                        ▼                                │  │  - /api/audio/            │
│  ┌───────────────────────────────────────────────────┐  │  │  - /api/classification/   │
│  │ 94 REST API Endpoints (/src/app/api/*)            │  │  │  - Bandpass Filtering     │
│  │ - Auth, Profiles, Babies, Activities, Recordings  │  │  │  - NoiseReduce (0.92 prop)│
│  │ - Subscription Limits (src/lib/subscription)      │  │  │  - MFCC / Spectrogram     │
│  │ - Session Reconcile (/api/session/status)         │  │  │  - Random Forest / Voting │
│  │ - Stripe Webhook Dispatch (/api/webhooks/stripe)  │  │  │  - Fine-tuned Wav2Vec2    │
│  └──────────┬───────────────────────────────┬────────┘  │  └───────────────────────────┘
└─────────────┼───────────────────────────────┼───────────┘
              │                               │
              │ Supabase Client & Service SDK │ Stripe SDK
              ▼                               ▼
┌────────────────────────────────────────┐  ┌────────────────────────────────────────────┐
│          SUPABASE PLATFORM             │  │            STRIPE PLATFORM                 │
│  - PostgreSQL 15 DB (3335 lines schema)│  │  - Checkout Sessions (Plus / Pro)          │
│  - Row-Level Security (RLS Enabled)    │  │  - Customer Billing Portal                 │
│  - GoTrue Auth Engine (JWT Issuance)   │  │  - Webhook Broadcasts                      │
│  - Storage Buckets (audio, avatars)    │  │    (invoice.paid, sub.updated, etc.)       │
└────────────────────────────────────────┘  └────────────────────────────────────────────┘
```

---

## 1. Client Browser Tier

### Responsibilities
- Render the interactive user interface using React 19, Framer Motion, and Tailwind CSS.
- Capture microphone input via the HTML5 `MediaRecorder` API.
- Maintain persistent GATT connections with Bluetooth Low Energy (BLE) pulse oximeters.
- Enforce proactive client-side subscription limit warnings and modal upsells.
- Automatically reconcile authentication and authorization states via polling and focus listeners.

### Key Browser APIs Utilized
- **`navigator.bluetooth`**: Scans, filters, and pairs with BLE devices advertising the Nordic UART Service (NUS UUID `6e400001-b5a3-f393-e0a9-e50e24dcca9e`).
- **`navigator.mediaDevices.getUserMedia`**: Captures raw infant audio directly from the device microphone at 44.1 kHz or 48 kHz.
- **`TextDecoder` & `ReadableStreamDefaultReader`**: Consumes Server-Sent Events (SSE) data streams emitted by the FastAPI processing endpoint.
- **`dashboardFetch` (Global Interceptor)**: Wraps standard HTTP fetch calls across the dashboard to inspect responses for the `x-session-invalid` header (`unauthenticated`, `account_deleted`, `account_suspended`) or HTTP 403 plan-limit payloads.

---

## 2. Next.js 15 Web Application & API Gateway

### Framework Configuration
- **Next.js Version**: 15.5.9 (App Router)
- **React Version**: 19.2.1
- **Rendering Model**: Server Components for static marketing pages and data-fetching layouts; Client Components (`'use client'`) for live monitoring, audio recording, and interactive forms.
- **TypeScript**: Strict configuration with absolute path alias `@/*` mapped to `src/*`.

### Middleware Architecture (`src/middleware.ts` & `src/lib/supabase/middleware.ts`)
The Next.js edge/Node middleware acts as the first line of security on every request:
1. **Exclusions**: Skips static assets (`_next/static`, images, icons) and public API routes (`/api/auth/*`, `/api/webhooks/*`, `/api/log-error`).
2. **Session Verification**: Retrieves the authenticated user via `supabase.auth.getUser()`.
3. **Live Profile Integrity Check**: Queries the `profiles` table to ensure:
   - The user record exists (if deleted, terminates session and redirects to `/welcome?reason=account_deleted`).
   - The user is not suspended (`metadata->>'suspended'` is not true; if suspended, redirects to `/account-suspended`).
   - The user has chosen an initial role (if missing, redirects to `/auth/role`).
4. **Role-Based Guards**:
   - `/dashboard/admin/*`: Enforces `profile.role === 'admin'`. Unauthorized users are redirected to `/dashboard`.
   - `/dashboard/expert/*`: Enforces verified expert status (`is_expert === true` or legacy verified expert). Non-experts are redirected to `/dashboard`.
5. **API Session Invalidation**: If an API request is made by a deleted or suspended user, middleware bypasses route logic and returns a structured JSON payload with HTTP 401/403 and the `x-session-invalid` header.

---

## 3. Python / FastAPI Machine Learning Service

### Responsibilities
- Expose high-performance audio preprocessing and machine learning inference endpoints.
- Stream multi-stage processing progress back to the browser in real time via Server-Sent Events (SSE).
- Support model training, incremental fine-tuning from parent feedback, and model artifact versioning.

### Configuration & Communication
- **Default Port**: `8000` (configurable via `PORT` and `BASE_URL`).
- **Next.js Integration**: Next.js client and server communicate with the backend using the environment variable `NEXT_PUBLIC_BACKEND_URL` (fallback: `http://localhost:8000`).
- **CORS Middleware**: Allows requests from configured web origins (specified in `ALLOWED_ORIGINS`).

### Core Internal Pipeline
1. **Format Conversion (`services.audio.convert_audio_format`)**: Converts incoming WebM, WAV, OGG, MP3, or M4A audio buffers to normalized float32 NumPy arrays via PyDub and Librosa.
2. **Live Noise Filtering (`services.audio.remove_noise`)**:
   - Implements a 4th-order Butterworth bandpass filter (200 Hz – 4000 Hz) to isolate infant vocalization frequencies and eliminate low-end room rumble and high-frequency electrical hiss.
   - Extracts the first 500ms of audio as a background noise profile.
   - Applies non-stationary spectral gating using `noisereduce` with a 92% attenuation factor (`prop_decrease=0.92`).
3. **Feature Extraction (`services.audio.extract_features`)**: Computes 13 Mel-Frequency Cepstral Coefficients (MFCCs), delta and delta-delta coefficients, spectral centroid, spectral bandwidth, spectral rolloff, zero-crossing rate, pitch statistics (mean, min, max, std via parabolic interpolation), and silence duration ratios.
4. **Classification Inference**:
   - **Primary (Transformer)**: When weights are present in `models/wav2vec2_cry_classifier/` or via HuggingFace (`WAV2VEC2_HF_REPO`), executes fine-tuned Wav2Vec2 sequence classification on 16 kHz resampled audio.
   - **Secondary (Ensemble)**: Falls back to an ensemble `VotingClassifier` (soft-voting across Random Forest with 300 estimators, Gradient Boosting with 300 estimators, and XGBoost with 500 estimators).
5. **Urgency Assessment**: Assigns categorical urgency (`low`, `medium`, `high`, `critical`) based on predicted distress type, confidence score, pitch frequency deviation, and intensity.

---

## 4. Supabase Data & Security Tier

### Database Layer
- **PostgreSQL 15**: Houses all application state across 20+ relational tables.
- **Extensions**: `uuid-ossp` (UUID generation), `pg_trgm` (fuzzy text search on community blogs and forums), `pgcrypto` (cryptographic operations), `pg_stat_statements` (performance metrics).
- **Triggers**: Automated timestamp management (`update_updated_at_column`), automatic parent-baby relationship binding upon baby creation (`on_baby_created`), forum thread activity tracking, and recording status transitions.

### Storage Buckets
Configured with strict MIME type and file size constraints:
1. `recordings` (Private, 10 MB limit): Stores processed WAV audio files indexed by `recordings/{userId}/{babyId}/{filename}.wav`.
2. `profile-avatars` (Public, 2 MB limit): User profile pictures.
3. `baby-photos` (Private, 5 MB limit): Baby profile images.
4. `community-resources` (Public, 50 MB limit): Downloadable PDF parenting guides and checklists.
5. `blog-media` (Public, 10 MB limit): Featured images for blog publications.
6. `medical-documents` (Private, 20 MB limit): Healthcare licenses and certification documents uploaded during expert applications.

### Security Implementation (RLS)
Every user-facing table has PostgreSQL Row-Level Security enabled:
- Data isolation is anchored to `auth.uid()`.
- Access to infant data (`babies`, `baby_activities`, `recordings`, `oximeter_readings`) requires an accepted membership in `baby_parents`.
- Update and delete rights are restricted to members with `is_primary = TRUE` and `can_edit_profile = TRUE`.

---

## 5. Stripe Billing Infrastructure

### Integration Model
- Uses official `@stripe/stripe-node` SDK v22.
- Handles card payments, tax computation, and localized currency presentation.
- Manages subscription lifecycles: trial periods, monthly recurring billing, automatic retries, cancellation at period end, and customer self-service billing portals.

### Synchronization Architecture
- **Checkout Handshake**: Next.js creates Stripe Checkout sessions embedding `user_id` and `plan_slug` in session metadata.
- **Webhook Gateway (`/api/webhooks/stripe`)**:
  - Validates cryptographically signed headers using `stripe.webhooks.constructEvent` with `STRIPE_WEBHOOK_SECRET`.
  - Dispatches events to handler routines in `src/lib/stripe/sync.ts`.
  - Maps Stripe statuses (`trialing`, `active`, `past_due`, `canceled`) to MumtaAI subscription records.
  - Automatically provisions or downgrades user plans in `user_subscriptions`.
  - Records transactional payment ledger entries in `payment_transactions`.

---

## 6. Communication Protocols & Interfaces

| Source | Destination | Protocol | Purpose | Authentication / Security |
|---|---|---|---|---|
| Browser | Next.js APIs | HTTPS REST | Core operations, CRUD, profile queries | Supabase Auth Bearer JWT |
| Browser | Next.js APIs | HTTPS SSE / Fetch | Real-time session reconciliation & heartbeat | Supabase Auth Cookie / JWT |
| Browser | FastAPI Service | HTTPS POST (SSE) | Audio file streaming & live ML prediction | Public / CORS Whitelist |
| Browser | Oximeter Device | Bluetooth Low Energy | GATT Characteristic Notifications (NUS) | Bluetooth Pairing PIN / Proximity |
| Next.js | Supabase DB | PostgreSQL / TLS | Persistent queries and database transactions | Supabase Service Role / RLS Client |
| Next.js | Supabase Storage | HTTPS S3 API | Audio file and avatar upload/retrieval | Service Role Key / Signed URLs |
| Next.js | Stripe API | HTTPS REST | Checkout creation, customer portal sessions | Stripe Secret Key (`sk_test_...`) |
| Stripe | Next.js Webhook | HTTPS POST | Asynchronous billing state notification | HMAC-SHA256 Webhook Signature |

---

## 7. Mid-Session Authorization & Reconciliation Flow

To prevent deactivated or downgraded users from continuing unauthorized access via long-lived JWTs:

```text
Browser Client (useSessionReconcile)
   │
   │ Polling interval (every 90 seconds) or Window Focus event
   ▼
GET /api/session/status (via dashboardFetch)
   │
   ├─► Query profiles: Check if account exists and whether suspended = true
   ├─► Query user_subscriptions: Check latest active plan slug
   ▼
Next.js Server evaluates live DB state
   │
   ├─► Case A: Profile deleted -> Returns 401 { code: 'account_deleted' }
   │          Action: Client immediately triggers signOut() -> Redirects to /welcome
   │
   ├─► Case B: Profile suspended -> Returns 403 { code: 'account_suspended' }
   │          Action: Client triggers signOut() -> Redirects to /account-suspended
   │
   ├─► Case C: Role changed (Admin revoked / Expert approved)
   │          Action: Client refreshes profile state, shows toast, redirects if on forbidden path
   │
   └─► Case D: Subscription changed (e.g. upgraded via Stripe)
              Action: Client refreshes useSubscription context, recalculating usage meters
```
