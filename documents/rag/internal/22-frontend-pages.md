# 22. Frontend Pages and Navigation Map — MumtaAI

## Overview
MumtaAI is built using the **Next.js 15 App Router** architecture. The frontend comprises **49 distinct page routes** organized into public marketing pages, authentication and onboarding flows, an authenticated multi-view dashboard, community spaces, and an administrative control suite.

---

## Complete Page Catalogue

### 1. Public Marketing & Informational Pages

| Route | Page Name | Access | Purpose |
|---|---|---|---|
| `/` | Landing Page | Public | Value proposition, feature highlights, and call-to-action. |
| `/pricing` | Pricing & Plans | Public | Detailed comparison of Free, Plus, and Pro tiers with checkout buttons. |
| `/oximeter` | Oximeter Guide | Public | Hardware compatibility guide, BLE instructions, and safety disclaimers. |
| `/contact` | Contact Us | Public | Support inquiry submission form. |
| `/terms` | Terms of Service | Public | Legal terms, usage rules, and medical disclaimers. |
| `/privacy` | Privacy Policy | Public | Data handling, biometric audio storage, and privacy assurances. |

---

### 2. Authentication & Account Access Pages (`/src/app/(auth)/*`)

| Route | Page Name | Access | Purpose |
|---|---|---|---|
| `/signin` | Sign In | Public | Email and password login form. |
| `/signup` | Sign Up | Public | Account creation form. |
| `/welcome` | Welcome Screen | Public | Post-signup landing and redirect destination after sign-out. |
| `/verify-email` | Email Verification | Public | Notification prompt instructing user to confirm email. |
| `/forget-password`| Forgot Password | Public | Request password reset token via email. |
| `/reset-password` | Reset Password | Public (Token)| Form to enter new password following recovery link click. |
| `/auth/role` | Role Selection | Authenticated | Mandatory first step to declare parent vs expert intent. |
| `/auth/expert-application`| Expert Apply | Authenticated | Submission of clinical license and credentials during signup. |
| `/auth/expert-onboarding` | Expert Onboarding | Authenticated | Verification guidelines and initial expert profile setup. |

---

### 3. Parent Dashboard (`/src/app/dashboard/*`)

| Route | Submodule | Access | Key Features |
|---|---|---|---|
| `/dashboard` | Dashboard Overview | Authenticated | Infant selector, quick action buttons, recent activities, vitals widget. |
| `/dashboard/babies` | Baby Directory | Authenticated | List all active infant profiles and caregiver counts. |
| `/dashboard/babies/add-baby` | Add Baby | Authenticated | Create a new infant profile (enforces plan limit). |
| `/dashboard/babies/[id]` | Baby Profile Details | Authenticated | Edit birth info, medical notes, growth, and caregiver list. |
| `/dashboard/oximeter` | Live Vitals Monitor | Authenticated | Connect BLE oximeter, live SpO2/pulse cards, trend charts, alerts. |
| `/dashboard/recordings` | Audio Recordings | Authenticated | Record cry audio, launch ML analysis, review previous predictions. |
| `/dashboard/insights` | Insights & Analytics | Authenticated | Weekly cry histograms, sleep trends, health suggestions, export. |
| `/dashboard/settings` | Settings & Billing | Authenticated | Edit profile, timezone, notification channels, Stripe portal link. |
| `/dashboard/experts` | Expert Directory | Authenticated | Browse verified pediatric experts and healthcare credentials. |
| `/dashboard/expert-application` | In-App Expert Apply| Authenticated | Existing parents applying to become verified experts. |

---

### 4. Community Hub Pages (`/src/app/dashboard/community/*`)

| Route | Submodule | Access | Key Features |
|---|---|---|---|
| `/dashboard/community` | Community Home | Authenticated | Featured articles, active forum discussions, downloadable guides. |
| `/dashboard/community/blog/[id]` | Blog Article View | Authenticated | Read article, author credentials badge, post comments. |
| `/dashboard/community/blog/create`| Create Article | Plus / Pro / Expert| Markdown editor, tags, age category selection (plan gated). |
| `/dashboard/community/forums/[id]`| Forum Thread | Authenticated | Read thread, post replies, view accepted answer. |
| `/dashboard/community/forums/create`| Create Thread | Authenticated | Start new discussion (enforces weekly/monthly limits). |
| `/dashboard/community/resources/[id]`| Resource Detail | Authenticated | Preview resource metadata, download PDF file. |
| `/dashboard/community/resources/create`| Upload Resource | Plus / Pro / Expert| Upload parenting checklist or guide (plan gated). |
| `/dashboard/community/favorites` | Bookmarked Items | Authenticated | Access saved articles, threads, and resources. |
| `/dashboard/community/guidelines`| Code of Conduct | Authenticated | Community rules and medical advice policies. |

---

### 5. Verified Expert Dashboard (`/src/app/dashboard/expert/*`)

| Route | Submodule | Access | Key Features |
|---|---|---|---|
| `/dashboard/expert/profile` | Expert Profile | Verified Expert | Public bio, professional credentials, clinic address, avatar. |
| `/dashboard/expert/articles`| Article Management | Verified Expert | Drafts, published articles, view counts, and reader feedback. |

---

### 6. Administration Console (`/src/app/dashboard/admin/*`)

| Route | Submodule | Access | Key Features |
|---|---|---|---|
| `/dashboard/admin` | Admin Overview | Admin Only | System KPIs, active baby counts, MRR, daily cry volume. |
| `/dashboard/admin/users` | User Directory | Admin Only | Search users, filter by role/status, quick-action suspension. |
| `/dashboard/admin/users/[id]`| User Inspection | Admin Only | Detailed audit view of user's babies, recordings, and history. |
| `/dashboard/admin/experts` | Verification Queue | Admin Only | Review uploaded medical licenses, approve or reject experts. |
| `/dashboard/admin/moderation`| Content Moderation | Admin Only | Inspect flagged comments and threads; hide or delete content. |
| `/dashboard/admin/subscriptions`| Subscription Control| Admin Only | Inspect user tiers, manual plan adjustments, Stripe status. |
| `/dashboard/admin/coupons` | Coupon Management | Admin Only | Create promo codes, configure percentage cuts and limits. |
| `/dashboard/admin/promotions`| Promotional Banners| Admin Only | Configure site-wide announcement banners and CTA links. |
| `/dashboard/admin/logs` | Audit & Error Logs | Admin Only | Review administrator actions (`audit_logs`) and exceptions. |

---

### 7. Special Workflow & Status Pages

| Route | Submodule | Access | Purpose |
|---|---|---|---|
| `/onboarding` | Onboarding Wizard | Authenticated | Mandatory first-time infant registration wizard. |
| `/invite/[token]` | Invitation Acceptance | Public/Auth | Verify caregiver invitation token and grant baby access. |
| `/billing/success`| Stripe Success | Authenticated | Confirmation screen following successful plan checkout. |
| `/account-suspended`| Suspension Notice | Authenticated | Informational lockout screen explaining account suspension. |
