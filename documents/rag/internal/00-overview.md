# MumtaAI RAG Knowledge Base — Master Overview

## Document Overview
This directory (`docs/rag/`) contains the complete, implementation-verified knowledge base for **MumtaAI**. It is structured for direct chunking and ingestion into a Retrieval-Augmented Generation (RAG) pipeline (using pgvector embeddings) and for conversion into a unified reference PDF.

Every claim across these documents is derived directly from the active MumtaAI codebase:
- **Web Application & APIs**: Next.js 15.5.9 (App Router), React 19, TypeScript
- **Database & Auth**: Supabase PostgreSQL, Row-Level Security (RLS), Supabase Storage, Supabase Auth
- **Audio & ML Engine**: Python 3, FastAPI, Uvicorn, Librosa, Scikit-learn, XGBoost, Wav2Vec2 Sequence Classification
- **Device Hardware I/O**: Web Bluetooth API, Nordic Semiconductor UART Service (NUS)
- **Billing & Subscriptions**: Stripe Checkout, Stripe Billing Portal, Webhooks

---

## Knowledge Base Navigation Index

| Document | Topic | Target Audience & Scope |
|---|---|---|
| [`01-product-overview.md`](file:///c:/TORRENT/Devwebies/mamtaAi/docs/rag/01-product-overview.md) | Product Overview | Core vision, problems solved, target personas, non-diagnostic boundaries |
| [`02-system-architecture.md`](file:///c:/TORRENT/Devwebies/mamtaAi/docs/rag/02-system-architecture.md) | System Architecture | Multi-service architecture, client/server boundaries, FastAPI integration |
| [`03-user-roles-and-permissions.md`](file:///c:/TORRENT/Devwebies/mamtaAi/docs/rag/03-user-roles-and-permissions.md) | Roles & Permissions | Complete matrix: Parent, Primary, Caregiver, Expert, Admin, Suspended |
| [`04-authentication-and-account.md`](file:///c:/TORRENT/Devwebies/mamtaAi/docs/rag/04-authentication-and-account.md) | Auth & Onboarding | Signup, signin, password recovery, verification, onboarding flows |
| [`05-baby-profiles.md`](file:///c:/TORRENT/Devwebies/mamtaAi/docs/rag/05-baby-profiles.md) | Baby Profiles | Profiles, avatars, age calculation, medical notes, vitals threshold config |
| [`06-family-and-caregivers.md`](file:///c:/TORRENT/Devwebies/mamtaAi/docs/rag/06-family-and-caregivers.md) | Family & Caregivers | Invitations, acceptance, role delegation, access control, revocation |
| [`07-activity-tracking.md`](file:///c:/TORRENT/Devwebies/mamtaAi/docs/rag/07-activity-tracking.md) | Activity Tracking | Feeding, sleep, diaper changes, medicine, milestones, plan restrictions |
| [`08-recordings-and-audio.md`](file:///c:/TORRENT/Devwebies/mamtaAi/docs/rag/08-recordings-and-audio.md) | Audio Recordings | Live microphone capture, file upload, durations, storage, retention |
| [`09-cry-analysis.md`](file:///c:/TORRENT/Devwebies/mamtaAi/docs/rag/09-cry-analysis.md) | Cry Analysis | Full ML pipeline: SSE streaming, noise filtering, MFCC, classification, urgency |
| [`10-oximeter.md`](file:///c:/TORRENT/Devwebies/mamtaAi/docs/rag/10-oximeter.md) | Oximeter Integration | Web Bluetooth, Nordic UART (NUS), AA 55 packet parsing, sustained breach alerts |
| [`11-insights.md`](file:///c:/TORRENT/Devwebies/mamtaAi/docs/rag/11-insights.md) | Insights & Analytics | Daily aggregations, weekly trends, health suggestions, CSV/PDF reports |
| [`12-notifications.md`](file:///c:/TORRENT/Devwebies/mamtaAi/docs/rag/12-notifications.md) | Notifications | In-app alerts, oximeter emergencies, sound/quiet hours, email delivery |
| [`13-community.md`](file:///c:/TORRENT/Devwebies/mamtaAi/docs/rag/13-community.md) | Community Hub | Editorial blog, discussion forums, downloadable resource library, moderation |
| [`14-expert-system.md`](file:///c:/TORRENT/Devwebies/mamtaAi/docs/rag/14-expert-system.md) | Expert System | Healthcare professional applications, verification, dual parent/expert views |
| [`15-admin-panel.md`](file:///c:/TORRENT/Devwebies/mamtaAi/docs/rag/15-admin-panel.md) | Admin Panel | User management, suspensions, audit logs, coupon management, system health |
| [`16-subscriptions-and-plans.md`](file:///c:/TORRENT/Devwebies/mamtaAi/docs/rag/16-subscriptions-and-plans.md) | Plans & Limitations | Free, Plus ($9.99/mo), Pro ($19.99/mo) limits, hard/soft caps, meters |
| [`17-billing-and-stripe.md`](file:///c:/TORRENT/Devwebies/mamtaAi/docs/rag/17-billing-and-stripe.md) | Billing & Stripe | Stripe Checkout, Customer Portal, webhooks, coupons, payment ledger |
| [`18-session-and-authorization.md`](file:///c:/TORRENT/Devwebies/mamtaAi/docs/rag/18-session-and-authorization.md) | Session Reconciliation | 90s heartbeat, live profile checks, instant token revocation on suspension |
| [`19-security-and-privacy.md`](file:///c:/TORRENT/Devwebies/mamtaAi/docs/rag/19-security-and-privacy.md) | Security & Privacy | RLS policies, service role safety, signature validation, data protection |
| [`20-api-reference.md`](file:///c:/TORRENT/Devwebies/mamtaAi/docs/rag/20-api-reference.md) | API Reference | Comprehensive catalogue of 94 Next.js endpoints and FastAPI routes |
| [`21-database-and-data-model.md`](file:///c:/TORRENT/Devwebies/mamtaAi/docs/rag/21-database-and-data-model.md) | Database & Schema | Entity-relationship model, tables, foreign keys, triggers, storage buckets |
| [`22-frontend-pages.md`](file:///c:/TORRENT/Devwebies/mamtaAi/docs/rag/22-frontend-pages.md) | Page Map | 49 Next.js App Router paths across marketing, auth, dashboard, admin |
| [`23-settings-and-preferences.md`](file:///c:/TORRENT/Devwebies/mamtaAi/docs/rag/23-settings-and-preferences.md) | Settings & Preferences | Account profile, timezones, notification channels, baby vitals bounds |
| [`24-user-workflows.md`](file:///c:/TORRENT/Devwebies/mamtaAi/docs/rag/24-user-workflows.md) | User Workflows | Step-by-step procedural guides for top user tasks |
| [`25-error-handling-and-limitations.md`](file:///c:/TORRENT/Devwebies/mamtaAi/docs/rag/25-error-handling-and-limitations.md) | Errors & Limitations | Plan limit error payloads, Web Bluetooth limits, network degradation |
| [`26-faq-knowledge.md`](file:///c:/TORRENT/Devwebies/mamtaAi/docs/rag/26-faq-knowledge.md) | FAQ Knowledge Base | 50+ real-world questions and implementation-derived answers |
| [`27-glossary.md`](file:///c:/TORRENT/Devwebies/mamtaAi/docs/rag/27-glossary.md) | Glossary | Authoritative definitions of application-specific and medical-adjacent terms |
| [`28-rag-chatbot-guidance.md`](file:///c:/TORRENT/Devwebies/mamtaAi/docs/rag/28-rag-chatbot-guidance.md) | RAG Chatbot Guidance | System prompts, behavioral guardrails, source hierarchy, medical disclaimers |
| [`99-source-map.md`](file:///c:/TORRENT/Devwebies/mamtaAi/docs/rag/99-source-map.md) | Source Map | File traceability map matching features to concrete source code paths |
| [`AUDIT_REPORT.md`](file:///c:/TORRENT/Devwebies/mamtaAi/docs/rag/AUDIT_REPORT.md) | Codebase Audit Report | Formal executive audit report summarizing findings, modules, and next steps |

---

## Verification & Trust Standard

1. **Codebase Over Documentation**: Where existing documentation or comments conflict with actual code execution, the verified runtime behavior documented here takes precedence.
2. **Explicit Medical Disclaimer**: MumtaAI is a supportive parenting technology. Neither cry classification nor pulse oximetry readings constitute a clinical diagnosis or medical monitoring service.
3. **No Secret Ingestion**: All sensitive environment variable values, secret tokens, private credentials, and personal data have been excluded from this knowledge base.
