# 15. Admin Panel and Management — MumtaAI

## Overview
The Admin Panel (`/dashboard/admin`) is a restricted management console accessible exclusively to users possessing `profiles.role === 'admin'`.

It provides oversight over user accounts, expert verification queues, subscription records, promotional discount campaigns, community content moderation, immutable audit logging, and system error tracking.

---

## Admin Submodules & Pages

| Route | Submodule | Primary Purpose |
|---|---|---|
| `/dashboard/admin` | **Overview / Stats** | High-level metrics: total users, active babies, MRR, daily cry analyses. |
| `/dashboard/admin/users` | **User Directory** | Search, filter, inspect, suspend, or delete user accounts. |
| `/dashboard/admin/users/[id]` | **User Deep Dive** | View user's babies, subscription tier, recent recordings, and audit logs. |
| `/dashboard/admin/experts` | **Expert Applications** | Review credentials, verify licenses, approve or reject applicants. |
| `/dashboard/admin/moderation` | **Content Moderation** | Inspect flagged blog comments, forum posts, and uploaded files. |
| `/dashboard/admin/subscriptions` | **Billing Oversight** | Inspect user subscriptions, plan distributions, and Stripe sync states. |
| `/dashboard/admin/coupons` | **Coupons & Discounts** | Create and manage discount codes, percentage cuts, and validity windows. |
| `/dashboard/admin/promotions` | **Promotional Banners** | Configure site-wide alert banners, sales notices, and CTA links. |
| `/dashboard/admin/logs` | **Audit & Error Logs** | Review system error stack traces and immutable administrator action history. |

---

## User Management Capabilities (`/api/admin/users/[id]`)

### 1. Account Search & Inspection
- Query users by full name, email, or telephone number.
- Inspect registered infants, caregiver relationships, and recording volumes.

### 2. Account Suspension & Reinstatement
- **Suspension Action**:
  - Sets `profiles.metadata->suspended = true`.
  - Records `suspension_reason`, `suspended_at`, and `suspended_by`.
  - **Instant Session Revocation**: Calls `revokeAllUserSessions(db, id)` to invalidate all active JWT tokens on Supabase's auth service.
  - The suspended user is forcibly signed out and routed to `/account-suspended` within 90 seconds.
- **Reinstatement**:
  - Clears the suspended keys from `profiles.metadata`.
  - User can log in normally on their next attempt.

### 3. Role Modification
- Administrators can elevate a user to `role = 'admin'` or revert an admin to `'parent'`.
- Self-modification safeguard: An administrator cannot modify or revoke their own admin status (`id === auth.admin.id` returns HTTP 400).

### 4. Account Deletion
- Calls `db.auth.admin.deleteUser(id)` to permanently remove the authentication record.
- Cascades deletion to `profiles`, `babies`, `baby_parents`, and related data.
- Self-deletion safeguard: An administrator cannot delete their own account via the admin API.

---

## Audit Logging System (`audit_logs` Table)

Every significant administrative modification automatically records an immutable entry via `writeAuditLog()`:
- `admin_id`: UUID of the performing administrator.
- `action`: E.g. `'admin_user_update'`, `'admin_user_delete'`, `'expert_approved'`, `'expert_rejected'`.
- `entity_type`: Target entity (e.g. `'profile'`, `'expert_application'`, `'discount_coupon'`).
- `entity_id`: UUID of the modified object.
- `old_values`: JSON snapshot of prior state.
- `new_values`: JSON snapshot of updated state.
- `ip_address` & `user_agent`: Network security context.

---

## Error Logging System (`error_logs` Table)

Captures unhandled exceptions and client-side error dispatches:
- `error_type`, `error_message`, `error_stack`.
- `endpoint`, `http_method`, `request_body`.
- `severity`: `'low'`, `'medium'`, `'high'`, `'critical'`.
- `is_resolved`: Resolution status tracked by developers and admins.
