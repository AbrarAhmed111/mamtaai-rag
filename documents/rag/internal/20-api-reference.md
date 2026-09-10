# 20. API Reference — MumtaAI

## Overview
MumtaAI exposes **94 REST API endpoints** in the Next.js application layer and multiple streaming and machine learning endpoints in the Python FastAPI backend.

---

## 1. Authentication & Session APIs

### `GET /api/session/status`
- **Purpose**: Returns the live database status of the authenticated session (mid-session reconciliation).
- **Auth**: User JWT required.
- **Response (200 OK)**:
  ```json
  {
    "ok": true,
    "access": { "role": "parent", "isExpert": false, "suspended": false },
    "subscriptionSlug": "plus"
  }
  ```
- **Error Responses**:
  - `401 Unauthorized` with `{ "ok": false, "code": "account_deleted" }`
  - `403 Forbidden` with `{ "ok": false, "code": "account_suspended" }`

### `GET /api/me` & `GET /api/mobile/me`
- **Purpose**: Returns full authenticated user profile, active babies, and subscription context.
- **Auth**: User JWT required.

---

## 2. User Profile APIs

### `GET /api/profile`
- **Purpose**: Retrieves the active user's profile metadata.
- **Auth**: User JWT required.

### `PATCH /api/profile`
- **Purpose**: Updates personal profile information (name, phone, timezone, language).
- **Body**: `{ "full_name"?: string, "phone_number"?: string, "timezone"?: string }`.

### `PATCH /api/profile/active-view`
- **Purpose**: Toggles between Parent View and Expert View for verified experts.
- **Auth**: User JWT required (must be verified expert).
- **Body**: `{ "active_view": "parent" | "expert" }`.

---

## 3. Baby Management APIs

### `GET /api/babies`
- **Purpose**: Lists all active babies associated with the authenticated user.
- **Auth**: User JWT required.

### `POST /api/babies`
- **Purpose**: Creates a new infant profile.
- **Plan Limits**: Enforces `checkLimit(userId, 'create_baby')`.
  - Free: Max 1 | Plus: Max 3 | Pro: Unlimited (soft cap 10).
- **Body**:
  ```json
  {
    "name": "Leo",
    "gender": "male",
    "birth_date": "2026-05-14",
    "birth_weight_kg": 3.4,
    "birth_height_cm": 50.2,
    "blood_type": "O+"
  }
  ```
- **Response**: `{ "ok": true, "baby": { ... } }`.

### `PATCH /api/babies/[id]`
- **Purpose**: Updates infant metadata or oximeter alert thresholds.
- **Auth**: Primary Parent or Caregiver with `can_edit_profile = TRUE`.

### `DELETE /api/babies/[id]`
- **Purpose**: Soft-deletes baby profile (`is_active = false`).
- **Auth**: Primary Parent only.

---

## 4. Family & Caregiver Invites

### `POST /api/invites`
- **Purpose**: Issues a caregiver invitation token.
- **Plan Limits**: Free: 0 | Plus: 2 caregivers/baby | Pro: Unlimited.
- **Body**: `{ "baby_id": "uuid", "relationship": "caregiver", "access_level": "full" | "read_only" | "limited" }`.

### `GET /api/invites/[token]`
- **Purpose**: Validates an invitation link and returns preview details.

### `POST /api/invites/[token]`
- **Purpose**: Accepts the invitation, binding the user to the infant in `baby_parents`.

---

## 5. Daily Activity Tracking

### `GET /api/activities?baby_id=<id>&limit=50`
- **Purpose**: Retrieves paginated activity timeline.

### `POST /api/activities`
- **Purpose**: Logs a routine infant care event.
- **Plan Limits**:
  - Free: Max 20 logs/month; only `feeding`, `sleep`, `diaper_change`.
  - Plus / Pro: Unlimited logs; all 8 activity types allowed.
- **Body Example (Feeding)**:
  ```json
  {
    "baby_id": "uuid",
    "activity_type": "feeding",
    "feeding_type": "bottle",
    "amount_ml": 120,
    "started_at": "2026-09-10T14:30:00Z"
  }
  ```

---

## 6. Audio Recordings & Cry Analysis

### `POST /api/audio/process`
- **Purpose**: Ingestion proxy that saves cleaned audio to Supabase Storage, records a row in `recordings`, and increments plan usage.
- **Plan Limits**: Validates duration limits (Free: 30s, Plus: 120s, Pro: 300s) and monthly quotas (Free: 7/mo, Plus: 60/mo, Pro: 500/mo).
- **Body (Multipart FormData)**:
  - `file`: Original audio file.
  - `baby_id`: Infant UUID.
  - `source`: `'live'` or `'uploaded'`.
  - `duration_seconds`: Number.
  - `processed_audio_base64`: Cleaned WAV audio bytes from FastAPI.

### `POST /api/recordings/[id]/features`
- **Purpose**: Stores acoustic measurement metadata in `extracted_features`.

### `POST /api/recordings/[id]/prediction`
- **Purpose**: Stores final classification output in `cry_predictions`.
- **Body**:
  ```json
  {
    "predicted_cry_type": "hungry",
    "confidence_score": 0.89,
    "urgency_level": "low",
    "suggested_actions": ["Offer breast or bottle"],
    "model_name": "wav2vec2_cry_classifier"
  }
  ```

### `POST /api/recordings/[id]/feedback`
- **Purpose**: Logs parent validation (`is_correct`, `actual_cry_type`, ratings).

---

## 7. Oximeter Telemetry APIs

### `POST /api/oximeter/sessions`
- **Purpose**: Starts or reuses a continuous monitoring session.
- **Body**: `{ "baby_id": "uuid", "device_id": "string" }`.

### `PATCH /api/oximeter/sessions/[id]`
- **Purpose**: Completes session and stores statistical aggregates.

### `POST /api/oximeter/readings`
- **Purpose**: Batch-saves telemetry readings (SpO2, pulse, PI, status).
- **Body**:
  ```json
  {
    "baby_id": "uuid",
    "session_id": "uuid",
    "device_id": "string",
    "spo2": 98,
    "pulse": 132,
    "pi": 2.4,
    "status": "normal"
  }
  ```

### `POST /api/oximeter/alerts`
- **Purpose**: Dispatches urgent in-app and email alerts following a 5-second sustained threshold breach.

---

## 8. Subscriptions & Billing

### `GET /api/subscription`
- **Purpose**: Returns active subscription tier, limitation definitions, and current period usage stats.

### `POST /api/billing/checkout`
- **Purpose**: Creates a Stripe Checkout Session for Plus or Pro upgrades.
- **Body**: `{ "plan_slug": "plus" | "pro" }`.

### `POST /api/billing/portal`
- **Purpose**: Generates a self-service Stripe Customer Billing Portal session URL.

### `POST /api/webhooks/stripe`
- **Purpose**: Webhook listener verifying Stripe HMAC signatures and synchronizing billing states.

---

## 9. Expert System APIs

### `POST /api/experts/apply`
- **Purpose**: Submits medical practitioner credentials and documents.
- **Body**: `{ "specialization": string, "professional_title": string, "license_number": string, "years_experience": number, "document_url": string }`.

### `GET /api/experts/dashboard`
- **Purpose**: Retrieves professional dashboard stats and publication metrics for verified experts.

---

## 10. Administrator APIs (`/api/admin/*`)

- `GET /api/admin/stats`: High-level platform KPIs.
- `GET /api/admin/users`: User search with pagination.
- `GET /api/admin/users/[id]`: Deep inspection of user record, infants, and recent recordings.
- `PATCH /api/admin/users/[id]`: Modifies roles or toggles `suspended = true` (with session revocation).
- `DELETE /api/admin/users/[id]`: Deletes user account from Supabase Auth and database.
- `PATCH /api/admin/experts/[id]`: Approves (`action = 'approve'`) or rejects an expert application.
- `POST /api/admin/coupons`: Creates a discount promotion code.

---

## 11. Python FastAPI Backend Endpoints

- `GET /health`: Service health check.
- `GET /api/streaming/health`: Streaming router availability probe.
- `POST /api/streaming/process-audio`: Primary SSE streaming pipeline performing noise reduction, feature extraction, and cry classification.
- `POST /api/classification/predict-from-audio`: Direct non-streaming classification.
- `POST /api/classification/train`: Triggers model training run.
- `POST /api/classification/improve`: Incremental training run using validated parent feedback data.
