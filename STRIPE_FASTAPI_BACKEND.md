# Stripe integration — FastAPI backend contract

The Quickoo React app collects card details with **Stripe.js** (Payment Element) and confirms payment in the browser. **Secret keys and PaymentIntent creation must stay on your FastAPI server** (or behind the Quickoo Express proxy).

This document describes what to implement in **FastAPI** so the existing frontend and `POST /api/stripe/create-payment-intent` proxy work end-to-end.

---

## Architecture (current Quickoo setup)

1. **Browser** → `POST /api/stripe/create-payment-intent` (same-origin, Express dev / Vercel).
2. **Express** → forwards JSON body to  
   `{ADMIN_API_BASE_URL}/api/v1/payments/create-payment-intent`.
3. **FastAPI** → creates a Stripe **PaymentIntent** with `stripe` Python SDK, returns **`client_secret`**.
4. **Browser** → Stripe.js confirms the payment using that `client_secret`.
5. **Optional but recommended** → Stripe **webhooks** hit FastAPI to mark bookings paid, send internal emails, etc.

Set `ADMIN_API_BASE_URL` in Quickoo `.env` to your FastAPI base URL (e.g. `http://127.0.0.1:8000`).

---

## Environment variables (FastAPI)

| Variable | Purpose |
|----------|---------|
| `STRIPE_SECRET_KEY` | Secret API key (`sk_test_...` / `sk_live_...`). **Never** expose to the frontend. |
| `STRIPE_WEBHOOK_SECRET` | Signing secret for `whsec_...` from Stripe Dashboard → Webhooks. |

Optional:

| Variable | Purpose |
|----------|---------|
| `STRIPE_API_VERSION` | Pin Stripe API version if you need reproducible behaviour. |

---

## Python dependencies

```bash
pip install stripe
```

Use the official Stripe Python library: [https://stripe.com/docs/api?lang=python](https://stripe.com/docs/api?lang=python)

---

## 1. Create PaymentIntent (required)

### Endpoint

`POST /api/v1/payments/create-payment-intent`

- **Auth:** Decide if this route is public (guest checkout) or protected (JWT). The Quickoo proxy does **not** send admin Bearer tokens today; add auth in FastAPI if needed and extend the Express proxy headers later.

### Request body (JSON)

The frontend sends:

```json
{
  "amount": 51600,
  "currency": "gbp",
  "receipt_email": "customer@example.com",
  "metadata": {
    "customer_email": "customer@example.com",
    "customer_name": "Jane Doe",
    "vehicle_class_id": "uuid-or-id",
    "vehicle_name": "Business Class",
    "booking_type": "oneway"
  }
}
```

| Field | Type | Notes |
|-------|------|--------|
| `amount` | integer | **Minor units** (e.g. GBP **pence**). `51600` = £516.00. Must be ≥ Stripe minimum (typically **50** for GBP). |
| `currency` | string | Lowercase ISO code, e.g. `gbp`. |
| `receipt_email` | string, optional | Stripe can email a receipt if enabled. |
| `metadata` | object, optional | String values only; Stripe metadata **keys/values have length limits** (500 chars per value). |

Validate `amount` and `currency` server-side; reject absurd values.

### Successful response (JSON)

Return HTTP **200** with a JSON body that includes the PaymentIntent **client secret** (the frontend accepts either snake_case or camelCase):

```json
{
  "client_secret": "pi_xxx_secret_xxx",
  "payment_intent_id": "pi_xxx"
}
```

Alternative shape (also supported by the frontend parser):

```json
{
  "data": {
    "client_secret": "pi_xxx_secret_xxx"
  }
}
```

### FastAPI example (minimal)

```python
import stripe
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

stripe.api_key = os.environ["STRIPE_SECRET_KEY"]

router = APIRouter(prefix="/api/v1/payments", tags=["payments"])

class CreatePaymentIntentBody(BaseModel):
    amount: int = Field(..., ge=50, description="Amount in minor units, e.g. pence")
    currency: str = "gbp"
    receipt_email: str | None = None
    metadata: dict[str, str] | None = None

@router.post("/create-payment-intent")
def create_payment_intent(body: CreatePaymentIntentBody):
    try:
        intent = stripe.PaymentIntent.create(
            amount=body.amount,
            currency=body.currency.lower(),
            automatic_payment_methods={"enabled": True},
            receipt_email=body.receipt_email,
            metadata=body.metadata or {},
        )
        return {
            "client_secret": intent.client_secret,
            "payment_intent_id": intent.id,
        }
    except stripe.error.StripeError as e:
        raise HTTPException(status_code=400, detail=str(e.user_message or e))
```

Adjust `automatic_payment_methods` vs `payment_method_types` per your Stripe Dashboard and product needs.

---

## 2. Webhook (strongly recommended)

Browser confirmation proves the customer completed the flow, but **webhooks** are the reliable source of truth for:

- `payment_intent.succeeded` — money captured (or ready to capture, depending on your capture settings).
- `payment_intent.payment_failed` — log / notify ops.

### Endpoint

`POST /api/v1/payments/stripe-webhook`

- **Raw body required:** Stripe signs the **raw** request body. In FastAPI, read the raw bytes and verify the signature with `stripe.Webhook.construct_event`.

### Headers

- `Stripe-Signature`: used with `STRIPE_WEBHOOK_SECRET`.

### Behaviour

1. Verify signature.
2. Handle events idempotently (same event ID may be delivered more than once).
3. On `payment_intent.succeeded`, load your booking/order by `metadata` or by storing `payment_intent_id` when you create the intent.
4. Return `200` quickly; heavy work can go to a background task queue.

Stripe docs: [https://stripe.com/docs/webhooks](https://stripe.com/docs/webhooks)

---

## 3. CORS (if the frontend ever calls FastAPI directly)

Prefer the **Quickoo proxy** so the browser only talks to your site origin. If you call FastAPI from the browser, enable CORS for your frontend origin and restrict methods/headers.

---

## 4. Testing

1. Use **test** keys (`pk_test_...`, `sk_test_...`).
2. Frontend: set `VITE_STRIPE_PUBLISHABLE_KEY=pk_test_...` in Quickoo `.env` / `.env.local`.
3. Test cards: [https://stripe.com/docs/testing](https://stripe.com/docs/testing)  
   - e.g. `4242 4242 4242 4242`, any future expiry, any CVC.
4. Test webhooks locally with **Stripe CLI**:

```bash
stripe listen --forward-to localhost:8000/api/v1/payments/stripe-webhook
```

---

## 5. Security checklist

- [ ] `STRIPE_SECRET_KEY` only on the server (FastAPI env / secrets manager).
- [ ] Never log full `client_secret` or card numbers.
- [ ] Validate `amount` against your own quote/booking record when possible (avoid client tampering).
- [ ] Use webhooks to confirm payment before fulfilling high-value or irreversible actions.
- [ ] For production, use **live** keys and HTTPS everywhere.

---

## 6. Optional improvements

- **Idempotency key:** pass `Idempotency-Key` header when creating PaymentIntent to avoid duplicate charges on retries (`stripe.PaymentIntent.create(..., idempotency_key=...)`).
- **Store `payment_intent_id`** on your booking row when the intent is created (from frontend callback or a small “register intent” call).
- **Connect / destination charges** if you use Stripe Connect for drivers or partners.

---

## Quickoo frontend reference

- **Publishable key:** `VITE_STRIPE_PUBLISHABLE_KEY` (e.g. `pk_test_...`).
- **Proxy:** `POST /api/stripe/create-payment-intent` → FastAPI `POST /api/v1/payments/create-payment-intent`.
- **Payment page:** `client/pages/booking/Payment.tsx` + `client/components/booking/StripePaymentForm.tsx`.
- After **successful** payment, the app calls `POST /api/booking/notify-admin` (existing SMTP flow).

If you change FastAPI paths, update `server/routes/stripe-payment-proxy.ts` to match.
