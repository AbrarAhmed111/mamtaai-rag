# MumtaAI Codebase Audit Report & RAG Knowledge Base Summary

**Date of Audit**: September 10, 2026  
**Target Repository**: MumtaAI Full-Stack Ecosystem By Abrar Ahmed
**Audit Scope**: Next.js 15 Web Application (`src/`), Database Schemas (`supabase/` & `src/types/schema.sql`), Python FastAPI ML Backend (`mamtaai_python_backend/`), and Supporting Tooling.  
**Deliverable Output**: Complete, verified RAG knowledge base inside [`docs/rag/`](file:///c:/TORRENT/Devwebies/mamtaAi/docs/rag/).

---

## 1. Executive Summary
A comprehensive, line-by-line codebase audit of MumtaAI was performed to construct an authoritative knowledge base suitable for PDF generation, chunking, and embedding into a Supabase pgvector RAG pipeline.

Rather than relying on claims made in documentation or README files, the audit verified implementation truth across:
- **377 Git-tracked Next.js project files** + **23 Python ML service files**.
- **94 REST API endpoints** implemented in Next.js App Router route handlers.
- **49 Frontend page routes** covering marketing, onboarding, parental tracking, expert tooling, and administration.
- **3,335 lines of production PostgreSQL schema** including 20+ tables, triggers, and Row-Level Security policies.
- **Dual-model machine learning architecture** combining a fine-tuned HuggingFace Wav2Vec2 transformer sequence classifier and a soft-voting ensemble (Random Forest, Gradient Boosting, XGBoost).
- **Web Bluetooth Low Energy (BLE)** integration communicating with Nordic UART Service (NUS) pulse oximeters.

---

## 2. Major Modules & Architectural Discovery

| Module | Core Technology | Primary Responsibilities |
|---|---|---|
| **Web Frontend** | Next.js 15.5.9, React 19, Tailwind CSS, Framer Motion | User interface, baby timeline, live vitals display, and audio recording. |
| **API Gateway & Business Logic** | Next.js Route Handlers (`/src/app/api/*`) | Plan limit enforcement, session reconciliation, DB mutations, Stripe handshakes. |
| **Edge & Auth Middleware** | Next.js Middleware (`src/middleware.ts`) | Continuous live profile validation, suspension checks, admin/expert route guards. |
| **Persistence & Auth Platform** | Supabase (PostgreSQL 15, Auth, Storage) | Relational storage, GoTrue JWT issuance, RLS policies, binary audio storage. |
| **Acoustic ML Inference Service** | Python 3, FastAPI, Uvicorn, Librosa, PyTorch | SSE streaming audio processing, Butterworth bandpass noise reduction, cry classification. |
| **Hardware Telemetry Module** | Web Bluetooth API, Nordic UART Service (NUS) | Bluetooth pairing, AA 55 binary packet decoding, 5-second sustained breach alerts. |
| **Billing Infrastructure** | Stripe Node SDK v22, Checkout, Billing Portal | Subscription recurring billing, tier synchronization, coupon redemptions. |

---

## 3. Major Features Documented

1. **Baby Profile Management**: Birth metrics, growth tracking, avatar uploads, and per-baby vitals threshold configuration.
2. **Family Collaboration**: Multi-parent model with Primary Parent privileges and granular Caregiver access levels (Full, Read-Only, Limited).
3. **Activity Timeline**: Daily tracking across 8 categories (feeding, sleep, diapers, medicine, milestones, play, bath, other) with automated duration calculation.
4. **Live Acoustic Cry Analysis**: 8-second microphone capture, real-time SSE progress updates, 7 cry distress categories, urgency meter (Low, Medium, High, Critical), soothing guidance, and feedback loop.
5. **Continuous Pulse Oximeter Monitoring**: Nordic UART BLE integration, AA 55 packet parsing (SpO2, PR, PI), real-time trend charts, and 5-second sustained breach alerts with 60-second cooldowns.
6. **Analytics & Longitudinal Insights**: Daily cry histograms, weekly sleep/cry trend trajectories, rule-based health suggestions, and exportable PDF/CSV reports.
7. **Omnichannel Notifications**: In-app toasts, persistent drawers, email alerts, quiet hours, sound chime options, and critical alarm quiet-hours bypass.
8. **Community Ecosystem**: Editorial blog with expert badges, categorized discussion forums with accepted answers, and a downloadable parenting resource library.
9. **Healthcare Expert System**: Verification workflow, medical document review queue, verified expert directory, and seamless in-place Parent/Expert workspace switching (`active_view`).
10. **Administration Suite**: User management, search, immediate session-revoking suspension, deletion safeguards, coupon campaigns, promotional banners, audit logs, and error tracking.
11. **Mid-Session Reconciliation**: 90-second heartbeat and window-focus listener verifying live account status, preventing de-authenticated users from utilizing stale JWTs.

---

## 4. API & Database Coverage

- **APIs Documented**: All 94 Next.js API endpoints catalogued in [`20-api-reference.md`](file:///c:/TORRENT/Devwebies/mamtaAi/docs/rag/20-api-reference.md), covering authentication, profile, babies, invites, activities, recordings, audio, oximeter, notifications, subscription, billing, experts, admin, community, insights, mobile, and webhooks, alongside FastAPI routes (`/api/streaming/process-audio`, `/api/classification/*`, `/health`).
- **Database Areas Documented**: 20+ tables fully detailed in [`21-database-and-data-model.md`](file:///c:/TORRENT/Devwebies/mamtaAi/docs/rag/21-database-and-data-model.md), including relational linkages, triggers (`create_baby_parent_relationship`, `update_recording_processing_status`), materialized view `mv_baby_summary`, and RLS isolation rules.

---

## 5. Python Backend Status
- **Status**: **Fully Audited & Verified**.
- **Inspection Summary**: The sibling backend in `mamtaai_python_backend/` was thoroughly reviewed. It exposes FastAPI routes on port 8000. It implements dual inference paths: a fine-tuned HuggingFace `Wav2Vec2ForSequenceClassification` transformer (16 kHz audio) and a soft-voting ensemble (`RandomForestClassifier`, `GradientBoostingClassifier`, `XGBClassifier`). It includes an audio noise reduction pipeline utilizing a 4th-order Butterworth bandpass filter (200–4000 Hz) and non-stationary spectral gating (`prop_decrease=0.92`).

---

## 6. Discrepancies Found in Existing README.md

During the audit, several contradictions and outdated claims in the root `README.md` were identified:

| README Claim | Codebase Implementation Truth | Severity |
|---|---|:---:|
| Mentions individual SQL migration files in `supabase/` (e.g. `supabase/subscription_setup.sql`, `supabase/admin_setup.sql`, `supabase/oximeter_integration.sql`). | Those individual files do **not** exist in `supabase/`. The complete database definition is consolidated in [`src/types/schema.sql`](file:///c:/TORRENT/Devwebies/mamtaAi/src/types/schema.sql) (3,335 lines) and `supabase/coupons_promotions.sql`. | Medium |
| Suggests `role` can be `'expert'` directly in the database. | The schema strictly checks `role IN ('parent', 'admin')`. Healthcare professionals are represented as `role = 'parent'` with `is_expert = TRUE` ("Parent + Expert"), with fallback support for legacy rows. | Low |
| Free plan features bullet says "8-second recordings". | The cry recorder defaults to capturing 8 seconds in the UI, but the hard server-enforced duration limit in `plans.ts` is **30 seconds** for Free, **120 seconds** for Plus, and **300 seconds** for Pro. | Low |
| Does not mention dedicated mobile API endpoints. | The codebase includes an entire family of mobile endpoints under `/api/mobile/*` (`me`, `babies`, `recordings`, `notifications`, `oximeter/readings`, `community`). | Informational |

---

## 7. Planned vs Implemented Features

- **Fully Implemented & Verified**:
  - Live Web Bluetooth Oximeter streaming, AA 55 decoding, trend charts, sustained breach alerts.
  - End-to-end cry analysis via SSE streaming to FastAPI, feature extraction, and prediction feedback.
  - Mid-session reconciliation via 90s heartbeat and window focus polling.
  - Complete Stripe Checkout, Customer Portal, and webhook billing synchronization.
  - Multi-parent baby sharing with granular access levels (Full, Read-Only, Limited).
  - Admin panel with user suspension, audit logs, coupon management, and expert review.
- **Partially Implemented / External Constraints**:
  - **SMS Notifications**: Database schema supports `sms_sent` and `sms_enabled`, but Twilio/telephony driver integration relies on external webhooks or provider credentials not configured by default.
  - **Product Reviews**: Tables exist (`products`, `product_reviews`, `product_categories`), but frontend views are secondary to the community blog and forum.

---

## 8. Security & Privacy Assurance

- **Zero Secrets Ingested**: All sensitive environment variables (`SUPABASE_SERVICE_ROLE_KEY`, `STRIPE_SECRET_KEY`, `STRIPE_WEBHOOK_SECRET`, `SMTP_PASS`) were strictly excluded from documentation.
- **Zero Live Credentials**: No passwords, tokens, or personal identifiers appear in any markdown document.
- **Medical Boundaries Reinforced**: Non-diagnostic medical disclaimers and explicit clarification that MumtaAI does **not** call emergency services are embedded across all guidance documents.

---

## 9. Recommended Next Steps for RAG Deployment

1. **PDF Generation**:
   - Merge `docs/rag/00-overview.md` through `docs/rag/28-rag-chatbot-guidance.md` and `docs/rag/AUDIT_REPORT.md` into a single styled PDF document using Pandoc or WeasyPrint.
2. **Chunking Strategy**:
   - Split markdown documents along H2 (`##`) and H3 (`###`) boundaries.
   - Maintain chunk sizes between 400 and 800 tokens with 10% overlap to preserve workflow context.
3. **Embedding & Ingestion**:
   - Embed chunks using an embedding model (e.g. `text-embedding-3-small` or Google Vertex AI embeddings).
   - Ingest into Supabase pgvector table (`documents` with `embedding vector(1536)`).
4. **Chatbot Prompt System**:
   - Ingest [`28-rag-chatbot-guidance.md`](file:///c:/TORRENT/Devwebies/mamtaAi/docs/rag/28-rag-chatbot-guidance.md) as the persistent system prompt for the bottom-right AI assistant.
