# 18. Session Management and Mid-Session Authorization — MumtaAI

## The Stale Session Problem
In modern single-page applications utilizing stateless JSON Web Tokens (JWTs), a token issued to a user remains cryptographically valid until its expiration (often 1 hour or more). 

If an administrator suspends an account, deletes a user, revokes admin privileges, or if a user's subscription changes in the database, the user's browser would normally continue accessing protected APIs and views until the local token expired.

MumtaAI solves this through **active mid-session reconciliation**.

---

## The Reconciliation Architecture

```text
               ┌────────────────────────┐
               │    Database Events     │
               │ - Account Suspended    │
               │ - Account Deleted      │
               │ - Role Changed         │
               │ - Plan Upgraded        │
               └───────────┬────────────┘
                           │ Modifies DB Row
                           ▼
┌────────────────────────────────────────────────────────┐
│                   SUPABASE POSTGRES                    │
│             profiles / user_subscriptions              │
└──────────────────────────▲─────────────────────────────┘
                           │
                           │ Live DB Status Query
                           │
┌──────────────────────────┴─────────────────────────────┐
│                 NEXT.JS SERVER LAYER                   │
│                                                        │
│  1. Edge Middleware (src/middleware.ts):               │
│     - Checks live profile status on API calls          │
│                                                        │
│  2. Server Guards (requireActiveProfile):              │
│     - Halts API execution if profile.suspended=true    │
│                                                        │
│  3. Status Endpoint (/api/session/status):             │
│     - Returns { ok, access: { role, isExpert, ... } }  │
└──────────────────────────▲─────────────────────────────┘
                           │
                           │ Polling Heartbeat (90s) & Focus Events
                           │
┌──────────────────────────┴─────────────────────────────┐
│                   BROWSER CLIENT                       │
│                                                        │
│  - useSessionReconcile Hook                            │
│  - dashboardFetch Fetch Interceptor                    │
│  - Invalidation Handler (Redirects to /account-susp)   │
└────────────────────────────────────────────────────────┘
```

---

## Core Components

### 1. Status Route (`GET /api/session/status`)
- **Server Implementation**: `src/lib/session/server.ts` -> `buildSessionStatus()`.
- **Logic**:
  - Queries `profiles` table for `id = auth.uid()`.
  - If no profile exists -> Returns HTTP 401 `{ ok: false, code: 'account_deleted' }`.
  - If `metadata->>'suspended' === 'true'` -> Returns HTTP 403 `{ ok: false, code: 'account_suspended' }`.
  - Retrieves active subscription tier slug (`'free'`, `'plus'`, `'pro'`).
  - Returns access snapshot: `{ role, isExpert, suspended }` and `subscriptionSlug`.

### 2. Client Heartbeat (`src/hooks/useSessionReconcile.ts`)
- Configured with `RECONCILE_INTERVAL_MS = 90000` (90 seconds).
- Registers a window focus listener (`window.addEventListener('focus', reconcile)`), re-verifying credentials whenever a parent switches back to the MumtaAI browser tab.
- Compares previous access snapshot to new server response:
  - If role changed (e.g. elevated to Admin), updates user context and displays an informational toast.
  - If currently on a restricted path (e.g. `/dashboard/admin`) and privileges were revoked, redirects immediately to `/dashboard`.
  - If subscription tier changed, triggers `subscription.refresh()` to recalculate client usage bars.

### 3. Client Fetch Interceptor (`dashboardFetch`)
- Wraps native browser `fetch` across all dashboard requests.
- Inspects response headers for `x-session-invalid`:
  ```typescript
  export function parseSessionInvalidCode(response: Response, body?: any): SessionInvalidCode | null {
    const header = response.headers.get('x-session-invalid');
    if (header === 'account_deleted' || header === 'account_suspended') return header;
    return body?.code ?? null;
  }
  ```
- If an invalid session code is detected, bypasses page rendering, immediately signs out of Supabase Auth, and redirects to the appropriate screen.

### 4. Immediate Session Revocation (`revokeAllUserSessions`)
When an administrator suspends an account in the admin panel:
```typescript
export async function revokeAllUserSessions(adminDb, userId: string): Promise<void> {
  try {
    await adminDb.auth.admin.signOut(userId, 'global');
  } catch {
    // Non-fatal — suspension is still enforced on next API/navigation check
  }
}
```
This terminates all active refresh tokens on Supabase's authentication servers globally.
