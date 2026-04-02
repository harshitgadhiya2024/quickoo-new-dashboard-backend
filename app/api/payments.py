from typing import Optional

import stripe
from fastapi import APIRouter, Header, HTTPException, status

from app.schemas.payment import CreatePaymentIntentRequest, CreatePaymentIntentResponse
from app.services.stripe_payment_service import create_payment_intent

router = APIRouter(prefix="/payments", tags=["payments"])


@router.post(
    "/create-payment-intent",
    response_model=CreatePaymentIntentResponse,
    status_code=status.HTTP_200_OK,
)
async def create_payment_intent_endpoint(
    body: CreatePaymentIntentRequest,
    idempotency_key: Optional[str] = Header(default=None, alias="Idempotency-Key"),
) -> CreatePaymentIntentResponse:
    try:
        client_secret, payment_intent_id = await create_payment_intent(
            amount=body.amount,
            currency=body.currency,
            receipt_email=body.receipt_email,
            metadata=body.metadata,
            idempotency_key=idempotency_key,
        )
    except stripe.StripeError as exc:
        msg = getattr(exc, "user_message", None) or str(exc)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=msg) from exc
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

    return CreatePaymentIntentResponse(
        client_secret=client_secret,
        payment_intent_id=payment_intent_id,
    )
