# Stripe Frontend Direct Flow (No Webhook)

This guide matches the current backend setup: direct Stripe PaymentIntent flow without webhook.

## Overview

1. Frontend asks backend to create PaymentIntent.
2. Backend returns `client_secret`.
3. Frontend confirms payment with Stripe.js (Payment Element).
4. Frontend shows toast based on Stripe result.

---

## Required Frontend Env

```env
VITE_STRIPE_PUBLISHABLE_KEY=pk_test_xxxxxxxxx
ADMIN_API_BASE_URL=http://127.0.0.1:8000
```

If you use your existing same-origin proxy:
- Frontend calls `POST /api/stripe/create-payment-intent`
- Proxy forwards to backend `POST /api/v1/payments/create-payment-intent`

---

## Backend Endpoint Contract

### Request

`POST /api/v1/payments/create-payment-intent`

```json
{
  "amount": 51600,
  "currency": "gbp",
  "receipt_email": "customer@example.com",
  "metadata": {
    "customer_email": "customer@example.com",
    "customer_name": "Jane Doe",
    "vehicle_class_id": "uuid-or-id",
    "booking_type": "oneway"
  }
}
```

### Response

```json
{
  "client_secret": "pi_xxx_secret_xxx",
  "payment_intent_id": "pi_xxx"
}
```

---

## Frontend Integration Steps

1. Create PaymentIntent from frontend/proxy.
2. Initialize Stripe Elements with returned `client_secret`.
3. Render Payment Element.
4. On submit, call `stripe.confirmPayment(...)`.
5. Handle result:
   - success (`paymentIntent.status === "succeeded"`) -> show success toast
   - failure -> show error toast

---

## Example (React + Stripe.js)

```ts
const onPay = async () => {
  setLoading(true);
  try {
    const createRes = await fetch("/api/stripe/create-payment-intent", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        amount: 51600,
        currency: "gbp",
        receipt_email: customerEmail,
        metadata: {
          customer_email: customerEmail,
          customer_name: customerName,
          vehicle_class_id: selectedVehicleClassId,
          booking_type: bookingType,
        },
      }),
    });

    const createData = await createRes.json();
    if (!createRes.ok) throw new Error(createData?.detail || "Unable to create payment intent");

    const clientSecret = createData.client_secret;
    if (!clientSecret) throw new Error("Missing client_secret");

    const { error, paymentIntent } = await stripe.confirmPayment({
      elements,
      confirmParams: {
        return_url: `${window.location.origin}/booking/payment-result`,
      },
      redirect: "if_required",
    });

    if (error) {
      toast.error(error.message || "Payment failed");
      return;
    }

    if (paymentIntent?.status === "succeeded") {
      toast.success("Payment completed");
      // Optional: call your backend booking-confirm API here
      return;
    }

    toast.info(`Payment status: ${paymentIntent?.status ?? "unknown"}`);
  } catch (e: any) {
    toast.error(e.message || "Payment failed");
  } finally {
    setLoading(false);
  }
};
```

---

## Important Notes (No Webhook Mode)

- This is fine for user UX and basic flow.
- For stronger backend trust, after frontend success you should call a backend API that:
  - receives `payment_intent_id`
  - fetches intent from Stripe server-side
  - verifies `status === succeeded`
  - then marks booking/order as paid

This gives you better reliability even without webhooks.
