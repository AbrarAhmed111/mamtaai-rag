# 99. Source Code Map and Traceability Guide — MumtaAI

## Overview
This document maps each functional domain in MumtaAI to the exact files, routes, components, database schemas, and service modules in the codebase where the behavior is defined.

---

## 1. Authentication & Session Management

- **Middleware**:
  - `src/middleware.ts`
  - `src/lib/supabase/middleware.ts`
- **Server Guard & Status**:
  - `src/lib/session/server.ts`
  - `src/app/api/session/status/route.ts`
  - `src/lib/session/types.ts`
- **Client Heartbeat & Interceptor**:
  - `src/hooks/useSessionReconcile.ts`
  - `src/lib/session/client.ts`
  - `src/components/Dashboard/DashboardSessionReconcile.tsx`
- **Frontend Pages**:
  - `src/app/(auth)/signin/page.tsx`
  - `src/app/(auth)/signup/page.tsx`
  - `src/app/(auth)/forget-password/page.tsx`
  - `src/app/(auth)/reset-password/page.tsx`
  - `src/app/auth/role/page.tsx`
  - `src/app/onboarding/page.tsx`
  - `src/app/account-suspended/page.tsx`

---

## 2. Baby Profiles & Family Sharing

- **Database Schemas & Triggers**:
  - `src/types/schema.sql` (Tables: `babies`, `baby_parents`, `baby_medical_conditions`)
- **API Endpoints**:
  - `src/app/api/babies/route.ts`
  - `src/app/api/babies/[id]/route.ts`
  - `src/app/api/invites/route.ts`
  - `src/app/api/invites/[token]/route.ts`
- **Permission Helpers**:
  - `src/lib/baby-permissions.ts`
- **Frontend Pages**:
  - `src/app/dashboard/babies/page.tsx`
  - `src/app/dashboard/babies/add-baby/page.tsx`
  - `src/app/dashboard/babies/[id]/page.tsx`
  - `src/app/invite/[token]/page.tsx`

---

## 3. Daily Activity Tracking

- **Database Schema**:
  - `src/types/schema.sql` (Table: `baby_activities`)
- **API Endpoints**:
  - `src/app/api/activities/route.ts`
  - `src/app/api/activities/[id]/route.ts`
- **Plan Enforcement**:
  - `src/lib/subscription/limits.ts` (`checkLimit` action: `'create_activity'`)

---

## 4. Audio Ingestion & Cry Analysis

- **Frontend Recording & SSE Stream Consumer**:
  - `src/components/Dashboard/ProcessingProgress.tsx`
  - `src/components/Dashboard/PredictionFeedback.tsx`
  - `src/lib/cry-urgency.ts`
  - `src/lib/cry-type-guidance.ts`
- **Next.js Ingestion & Prediction APIs**:
  - `src/app/api/audio/process/route.ts`
  - `src/app/api/recordings/route.ts`
  - `src/app/api/recordings/[id]/prediction/route.ts`
  - `src/app/api/recordings/[id]/features/route.ts`
  - `src/app/api/recordings/[id]/feedback/route.ts`
- **Python FastAPI ML Backend**:
  - `mamtaai_python_backend/api/main.py`
  - `mamtaai_python_backend/api/routers/streaming.py` (SSE progress endpoint)
  - `mamtaai_python_backend/api/routers/audio.py`
  - `mamtaai_python_backend/api/routers/classification.py`
  - `mamtaai_python_backend/services/audio.py` (Butterworth filter, noise reduction, Librosa MFCC)
  - `mamtaai_python_backend/services/classification.py` (VotingClassifier, RF, GB, XGBoost)
  - `mamtaai_python_backend/services/wav2vec2_classifier.py` (Wav2Vec2 transformer sequence classification)
- **Database Schema**:
  - `src/types/schema.sql` (Tables: `recordings`, `extracted_features`, `cry_predictions`, `prediction_feedback`)

---

## 5. Bluetooth Pulse Oximeter

- **Frontend BLE Driver & Context**:
  - `src/contexts/OximeterContext.tsx`
  - `src/lib/oximeter/ble.ts` (Web Bluetooth Nordic UART Service GATT connection)
  - `src/lib/oximeter/decode.ts` (AA 55 binary packet parser)
  - `src/lib/oximeter/types.ts` (UUIDs, reading states)
  - `src/lib/oximeter/sustained-breach.ts` (5-second sustained breach tracker & cooldowns)
  - `src/lib/oximeter/baby-thresholds.ts` (Sanitization, copy generation)
- **API Endpoints**:
  - `src/app/api/oximeter/devices/route.ts`
  - `src/app/api/oximeter/sessions/route.ts`
  - `src/app/api/oximeter/sessions/[id]/route.ts`
  - `src/app/api/oximeter/readings/route.ts`
  - `src/app/api/oximeter/readings/latest/route.ts`
  - `src/app/api/oximeter/alerts/route.ts`
- **Frontend Pages**:
  - `src/app/dashboard/oximeter/page.tsx`
  - `src/app/oximeter/page.tsx` (Public guide)
- **Database Schema**:
  - `src/types/schema.sql` (Tables: `oximeter_devices`, `oximeter_sessions`, `oximeter_readings`)

---

## 6. Subscriptions, Stripe & Plan Limitations

- **Plan Definitions & Limitations**:
  - `src/lib/subscription/plans.ts` (Free, Plus, Pro limitation records)
  - `src/lib/subscription/limits.ts` (Centralized `checkLimit()` logic)
  - `src/lib/subscription/service.ts` (DB plan context and usage sync)
  - `src/lib/subscription/types.ts`
  - `src/hooks/useSubscription.tsx`
  - `src/lib/subscription/plan-limit-client.ts`
- **Stripe Integration & Webhooks**:
  - `src/lib/stripe/client.ts`
  - `src/lib/stripe/prices.ts`
  - `src/lib/stripe/sync.ts` (Webhook handlers and plan transitions)
  - `src/app/api/billing/checkout/route.ts`
  - `src/app/api/billing/portal/route.ts`
  - `src/app/api/webhooks/stripe/route.ts`
- **Database Schema**:
  - `src/types/schema.sql` (Tables: `subscription_plans`, `user_subscriptions`, `payment_transactions`, `discount_coupons`)
  - `supabase/coupons_promotions.sql`

---

## 7. Healthcare Expert System

- **Expert Workflow & Role Logic**:
  - `src/lib/expert/profile-role.ts`
  - `src/lib/expert/applications.ts`
  - `src/app/api/experts/apply/route.ts`
  - `src/app/api/experts/dashboard/route.ts`
  - `src/app/api/profile/active-view/route.ts`
  - `src/app/api/admin/experts/[id]/route.ts` (Admin approval/rejection)
- **Frontend Pages**:
  - `src/app/dashboard/expert-application/page.tsx`
  - `src/app/dashboard/experts/page.tsx` (Public expert directory)
  - `src/app/dashboard/expert/profile/page.tsx`
  - `src/app/dashboard/expert/articles/page.tsx`
- **Database Schema**:
  - `src/types/schema.sql` (Table: `expert_applications`, columns in `profiles`)

---

## 8. Platform Administration

- **Admin Core & Security**:
  - `src/lib/admin/index.ts`
  - `src/lib/admin/auth.ts` (`requireAdminApi`, `isProfileSuspended`)
  - `src/lib/admin/audit.ts` (`writeAuditLog`)
- **API Endpoints**:
  - `src/app/api/admin/stats/route.ts`
  - `src/app/api/admin/users/route.ts`
  - `src/app/api/admin/users/[id]/route.ts`
  - `src/app/api/admin/experts/route.ts`
  - `src/app/api/admin/experts/[id]/route.ts`
  - `src/app/api/admin/coupons/route.ts`
  - `src/app/api/admin/promotions/route.ts`
  - `src/app/api/admin/community/route.ts`
- **Frontend Pages**:
  - `src/app/dashboard/admin/page.tsx`
  - `src/app/dashboard/admin/users/page.tsx`
  - `src/app/dashboard/admin/users/[id]/page.tsx`
  - `src/app/dashboard/admin/experts/page.tsx`
  - `src/app/dashboard/admin/moderation/page.tsx`
  - `src/app/dashboard/admin/subscriptions/page.tsx`
  - `src/app/dashboard/admin/coupons/page.tsx`
  - `src/app/dashboard/admin/promotions/page.tsx`
  - `src/app/dashboard/admin/logs/page.tsx`
