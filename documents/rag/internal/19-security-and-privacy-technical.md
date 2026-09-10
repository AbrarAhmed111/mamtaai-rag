# 19. Security and Privacy — MumtaAI

## Security Principles & Architecture
MumtaAI handles sensitive infant health records, vital sign streams, and personal audio recordings. Security is implemented through defense-in-depth across database rules, network middleware, server guards, and cryptographic signature validations.

---

## 1. Authentication & Session Security
- **Asymmetric Token Cryptography**: Identity is established via Supabase Auth using cryptographically signed JSON Web Tokens (JWTs).
- **Secure Cookie Transport**: Auth tokens are transferred via HTTP-only, Secure, SameSite cookies managed by `@supabase/ssr`.
- **Active State Re-Verification**: Long-lived JWT tokens are coupled with live database checks via `useSessionReconcile` and `updateSession` middleware to ensure revoked or suspended accounts cannot continue performing actions.

---

## 2. Database Row-Level Security (RLS)
PostgreSQL Row-Level Security is strictly enabled across all user-facing database tables.

### Key Isolation Rules
- **Profiles**: Users can only read and modify their own profile row (`auth.uid() = id`).
- **Baby Isolation**: Access to an infant profile requires an accepted relationship in `baby_parents`:
  ```sql
  EXISTS (
      SELECT 1 FROM baby_parents 
      WHERE baby_parents.baby_id = babies.id 
      AND baby_parents.parent_id = auth.uid() 
      AND baby_parents.invitation_status = 'accepted'
  )
  ```
- **Caregiver Guard**: Modification and deletion of an infant profile requires primary parental status (`is_primary = TRUE`) and edit permissions (`can_edit_profile = TRUE`).
- **Telemetry & Recordings**: Users can only access recordings and oximeter readings belonging to babies they have accepted access to.

---

## 3. Server-Side Execution Guards
Client-side checks are treated as UI conveniences only. The server strictly validates every incoming request:
- **`requireActiveProfile()`**: Verifies that the requesting user exists in `auth.users`, has an active record in `profiles`, and is not suspended.
- **`requireAdminApi()`**: Enforces that `profile.role === 'admin'`. Rejects unauthorized calls with HTTP 403.
- **`checkLimit()`**: Verifies that the user has not exceeded their subscription tier allowances before executing resource-intensive operations.

---

## 4. Storage Bucket Security
Supabase Storage buckets enforce strict access permissions:
- **`recordings` (Private)**: Audio files are inaccessible publicly. Retrieval requires authenticated Supabase client sessions or time-limited signed URLs.
- **`medical-documents` (Private)**: Expert verification licenses and certificates are strictly restricted to the uploading user and platform administrators.
- **`baby-photos` (Private)**: Infant photos are accessible only to authorized caregivers.
- **`profile-avatars` & `community-resources` (Public)**: Assets intended for community consumption are served publicly with file-size caps.

---

## 5. Webhook Signature Verification
Incoming Stripe billing events at `/api/webhooks/stripe` must verify their HMAC-SHA256 signature against the raw request body using `STRIPE_WEBHOOK_SECRET`:
```typescript
event = stripe.webhooks.constructEvent(body, signature, getStripeWebhookSecret());
```
Any request with an invalid or missing signature is immediately rejected with HTTP 400.

---

## 6. Secrets & Environment Configuration

### Server-Only Secrets
The following sensitive variables are isolated to server runtimes and never exposed to the client bundle:
- `SUPABASE_SERVICE_ROLE_KEY`: Elevated administrative database key.
- `STRIPE_SECRET_KEY`: Stripe API private secret.
- `STRIPE_WEBHOOK_SECRET`: Stripe webhook signing secret.
- `SMTP_USER` & `SMTP_PASS`: Transactional email credentials.

### Client-Safe Variables
Only variables prefixed with `NEXT_PUBLIC_` are bundled into frontend code:
- `NEXT_PUBLIC_SUPABASE_URL`
- `NEXT_PUBLIC_SUPABASE_ANON_KEY`
- `NEXT_PUBLIC_BACKEND_URL`
- `NEXT_PUBLIC_SITE_URL`

---

## 7. RAG Knowledge Base Redaction Standard
In compliance with strict data privacy guidelines, this knowledge base contains:
- **Zero API keys or secret tokens.**
- **Zero actual passwords or database connection strings.**
- **Zero real patient or infant data.**
- **Zero live test account credentials.**
