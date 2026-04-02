# Stripe Keys Setup Guide (Quickoo)

This guide explains how to get all Stripe keys required for your current Quickoo setup.

## Keys You Need

- `STRIPE_SECRET_KEY` (backend/FastAPI) - `sk_test_...` or `sk_live_...`
- `STRIPE_WEBHOOK_SECRET` (backend/FastAPI) - `whsec_...`
- `VITE_STRIPE_PUBLISHABLE_KEY` (frontend) - `pk_test_...` or `pk_live_...`

Optional:

- `STRIPE_API_VERSION` (backend/FastAPI) - set only if you want a pinned version

---

## 1) Create / Access Stripe Account

1. Go to [https://dashboard.stripe.com](https://dashboard.stripe.com)
2. Log in (or create account).
3. In the top-right, keep **Test mode** ON while integrating.

---

## 2) Get Publishable + Secret API Keys

1. Open **Developers -> API keys** in Stripe Dashboard.
2. Under **Standard keys**:
   - Copy **Publishable key** (`pk_test_...`)
   - Copy **Secret key** (`sk_test_...`)
3. For production later, switch off Test mode and copy live keys (`pk_live_...`, `sk_live_...`).

### Where to use


- Frontend (`Quickoo` app `.env`):
  - `VITE_STRIPE_PUBLISHABLE_KEY=pk_test_...`
- Backend (`quickoo new backend/.env`):
  - `STRIPE_SECRET_KEY=sk_test_...`

---

## 3) Get Webhook Signing Secret (`whsec_...`)

You have two common options:

### Option A: Local development with Stripe CLI (recommended for local)

1. Install Stripe CLI:
   - macOS: `brew install stripe/stripe-cli/stripe`
2. Login:
   - `stripe login`
3. Start forwarding:
   - `stripe listen --forward-to localhost:8000/api/v1/payments/stripe-webhook`
4. CLI prints:
   - `Ready! Your webhook signing secret is whsec_...`
5. Copy that `whsec_...` value.

Set in backend `.env`:

- `STRIPE_WEBHOOK_SECRET=whsec_...`

### Option B: Dashboard webhook endpoint (for deployed env)

1. Go to **Developers -> Webhooks**.
2. Click **Add endpoint**.
3. Endpoint URL:
   - `https://<your-domain>/api/v1/payments/stripe-webhook`
4. Select events:
   - `payment_intent.succeeded`
   - `payment_intent.payment_failed`
5. Save endpoint.
6. Open endpoint details -> click **Reveal** under Signing secret.
7. Copy `whsec_...`.

Set in backend `.env`:

- `STRIPE_WEBHOOK_SECRET=whsec_...`

---

## 4) Backend Env Example

In `quickoo new backend/.env`:

```env
STRIPE_SECRET_KEY=sk_test_xxxxxxxxxxxxxxxxx
STRIPE_WEBHOOK_SECRET=whsec_xxxxxxxxxxxxxxxxx
STRIPE_API_VERSION=
```

Notes:
- Leave `STRIPE_API_VERSION` empty unless you intentionally pin a version.
- Never expose `STRIPE_SECRET_KEY` or `STRIPE_WEBHOOK_SECRET` to frontend.

---

## 5) Frontend Env Example

In Quickoo frontend `.env` or `.env.local`:

```env
VITE_STRIPE_PUBLISHABLE_KEY=pk_test_xxxxxxxxxxxxxxxxx
ADMIN_API_BASE_URL=http://127.0.0.1:8000
```

---

## 6) Quick Validation Steps

1. Start backend.
2. Call payment intent API once:
   - `POST /api/v1/payments/create-payment-intent`
3. Confirm response contains:
   - `client_secret`
   - `payment_intent_id`
4. Confirm frontend payment page loads Stripe element correctly.
5. Trigger webhook test event (Stripe CLI):
   - `stripe trigger payment_intent.succeeded`

---

## 7) Production Checklist

- Use live keys only in production.
- Use HTTPS for backend webhook endpoint.
- Rotate keys if exposed.
- Keep secrets in server env/secret manager, not in code.
