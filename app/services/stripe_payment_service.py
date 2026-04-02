from typing import Any, Optional

import stripe
from fastapi.concurrency import run_in_threadpool

from app.core.config import get_settings


def _normalize_metadata(metadata: Optional[dict[str, Any]]) -> dict[str, str]:
    if not metadata:
        return {}
    out: dict[str, str] = {}
    for key, value in metadata.items():
        if value is None:
            continue
        sk = str(key)[:40]
        sv = str(value)[:500]
        out[sk] = sv
    return out


def _create_intent_sync(
    amount: int,
    currency: str,
    receipt_email: Optional[str],
    metadata: dict[str, str],
    idempotency_key: Optional[str],
) -> stripe.PaymentIntent:
    settings = get_settings()
    kwargs: dict[str, Any] = {
        "amount": amount,
        "currency": currency,
        "automatic_payment_methods": {"enabled": True},
        "metadata": metadata,
        "api_key": settings.stripe_secret_key,
    }
    if receipt_email:
        kwargs["receipt_email"] = receipt_email
    if idempotency_key:
        kwargs["idempotency_key"] = idempotency_key
    if settings.stripe_api_version:
        kwargs["stripe_version"] = settings.stripe_api_version
    return stripe.PaymentIntent.create(**kwargs)


async def create_payment_intent(
    amount: int,
    currency: str,
    receipt_email: Optional[str],
    metadata: Optional[dict[str, Any]],
    idempotency_key: Optional[str] = None,
) -> tuple[str, str]:
    meta = _normalize_metadata(metadata)
    intent = await run_in_threadpool(
        _create_intent_sync,
        amount,
        currency,
        receipt_email,
        meta,
        idempotency_key,
    )
    if not intent.client_secret:
        raise ValueError("Stripe did not return a client_secret.")
    return intent.client_secret, intent.id
