# 21. Database and Data Model — MumtaAI

## Overview
The MumtaAI persistence layer runs on **PostgreSQL 15** inside Supabase. The database architecture is documented in `src/types/schema.sql` (3,335 lines), `supabase/coupons_promotions.sql`, and `scripts/seed_blog_posts.sql`.

It uses UUID primary keys, automated timestamp triggers, Row-Level Security (RLS) on all tables, and foreign keys with cascading deletions.

---

## Conceptual Entity-Relationship Hierarchy

```text
auth.users
   │
   └── profiles (User Profiles)
         │
         ├── baby_parents ◄─── babies (Infant Profiles)
         │                        │
         │                        ├── baby_activities (Timeline Logs)
         │                        ├── baby_medical_conditions (Health Notes)
         │                        ├── recordings (Audio Files)
         │                        │     │
         │                        │     ├── extracted_features (Acoustic Vectors)
         │                        │     └── cry_predictions (ML Results)
         │                        │           │
         │                        │           └── prediction_feedback (User Validation)
         │                        │
         │                        ├── oximeter_sessions (Continuous Monitoring)
         │                        └── oximeter_readings (Time-Series Vitals)
         │
         ├── user_subscriptions ◄─── subscription_plans
         ├── payment_transactions
         ├── notifications
         ├── notification_preferences
         ├── expert_applications
         ├── blog_posts ─── blog_comments
         ├── forum_threads ─── forum_replies
         └── shared_resources
```

---

## Core Database Tables

### 1. User & Identity Tables
- **`profiles`**: Extends `auth.users`. Contains `full_name`, `role` (`'parent' | 'admin'`), `is_expert`, `is_verified`, `active_view`, `timezone`, `onboarding_completed`, `last_active_at`, and extensible `metadata` JSONB (tracks suspension state).
- **`expert_applications`**: Manages credential submissions from healthcare professionals (`specialization`, `professional_title`, `license_number`, `years_experience`, `document_url`, `status`, `rejection_reason`, `can_reapply_after`).

### 2. Infant & Family Tables
- **`babies`**: Core infant entity storing `name`, `gender`, `birth_date`, `birth_weight_kg`, `birth_height_cm`, `blood_type`, `avatar_url`, `medical_notes`, `is_active`, and `metadata->oximeterAlerts`.
- **`baby_parents`**: Many-to-many relationship tracking parental membership (`relationship`, `is_primary`, `access_level`, `can_edit_profile`, `can_record_audio`, `can_view_history`, `invitation_status`).
- **`baby_medical_conditions`**: Historical allergies, chronic conditions, and past illnesses.
- **`baby_activities`**: Daily care events (`activity_type`, `started_at`, `ended_at`, `duration_minutes`, `feeding_type`, `amount_ml`, `sleep_quality`, `diaper_type`, `medicine_name`, `milestone_category`).

### 3. Audio & Cry Analysis Tables
- **`recordings`**: Stored audio files (`file_url`, `duration_seconds`, `source`, `device_type`, `quality_score`, `processing_status`, `recorded_at`).
- **`extracted_features`**: ML features extracted by Librosa/PyDub (`mfcc_coefficients`, `pitch_hz_mean`, `zero_crossing_rate`, `spectral_centroid`, `spectrogram_url`).
- **`cry_predictions`**: Inference results (`predicted_cry_type`, `confidence_score`, `all_class_probabilities`, `urgency_level`, `suggested_actions`, `medical_red_flags`, `model_name`).
- **`prediction_feedback`**: Continuous learning validation (`is_correct`, `actual_cry_type`, `prediction_quality_rating`, `comments`, `use_for_training`).
- **`custom_cry_labels`**: User-defined cry tags.

### 4. Oximeter & IoT Telemetry Tables
- **`oximeter_devices`**: Paired BLE hardware (`device_id`, `device_name`, `model`, `last_sync_at`, `is_active`).
- **`oximeter_sessions`**: Aggregated monitoring sessions (`started_at`, `ended_at`, `avg_spo2`, `min_spo2`, `max_spo2`, `avg_pulse`, `reading_count`).
- **`oximeter_readings`**: High-frequency vitals (`spo2_percentage`, `pulse_rate_bpm`, `perfusion_index`, `status`, `is_alarm`, `measured_at`).

### 5. Analytics & Insights Tables
- **`daily_cry_stats`**: Daily cry counts by type, peak crying hour, and total duration.
- **`weekly_insights`**: Weekly cry trends, sleep quality progression, and AI suggestions.
- **`health_suggestions`**: Actionable recommendations for parents based on activity trends.

### 6. Subscriptions & Billing Tables
- **`subscription_plans`**: Master definitions for Free, Plus, and Pro (`price_usd`, `billing_cycle`, `features`, `limitations`).
- **`user_subscriptions`**: Active user tier (`status`, `current_period_start`, `current_period_end`, `stripe_subscription_id`, `stripe_customer_id`, `usage_stats`).
- **`payment_transactions`**: Charge history (`amount`, `currency`, `gateway_transaction_id`, `status`, `invoice_url`).
- **`discount_coupons`**: Promotional discount codes (`code`, `discount_type`, `discount_value`, `max_uses`, `current_uses`).

### 7. Community Tables
- **`blog_posts`** & **`blog_comments`**: Curated articles and discussion.
- **`forum_categories`**, **`forum_threads`**, **`forum_replies`**: Parent discussion boards.
- **`shared_resources`**: Downloadable guides and templates.

### 8. System & Governance Tables
- **`notifications`** & **`notification_preferences`**: Omnichannel messaging state and quiet hours.
- **`audit_logs`**: Immutable administrator action ledger.
- **`error_logs`**: System error stack traces.
- **`ml_models`** & **`model_training_batches`**: Model registry and training metrics.

---

## Materialized Views & Performance Optimizations

### Materialized View `mv_baby_summary`
Pre-aggregates dashboard metrics:
```sql
CREATE MATERIALIZED VIEW mv_baby_summary AS
SELECT 
    b.id AS baby_id,
    b.name,
    b.birth_date,
    EXTRACT(YEAR FROM AGE(b.birth_date)) * 12 + EXTRACT(MONTH FROM AGE(b.birth_date)) AS age_months,
    COUNT(DISTINCT bp.parent_id) AS parent_count,
    COUNT(DISTINCT r.id) AS total_recordings,
    COUNT(DISTINCT CASE WHEN r.created_at >= NOW() - INTERVAL '7 days' THEN r.id END) AS recordings_last_7_days,
    MAX(r.recorded_at) AS last_recording_at
FROM babies b
LEFT JOIN baby_parents bp ON b.id = bp.baby_id
LEFT JOIN recordings r ON b.id = r.baby_id
WHERE b.is_active = TRUE
GROUP BY b.id, b.name, b.birth_date;
```

### Full-Text Search Indexes
- GIN index on `to_tsvector('english', title || ' ' || content)` across `blog_posts` and `forum_threads` for fast fuzzy keyword search.
