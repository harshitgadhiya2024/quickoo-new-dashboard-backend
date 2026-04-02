from typing import Any, Optional

from pydantic import BaseModel, Field, field_validator


class CreatePaymentIntentRequest(BaseModel):
    amount: int = Field(..., ge=50, le=50_000_000, description="Minor units, e.g. GBP pence")
    currency: str = Field(default="gbp", min_length=3, max_length=3)
    receipt_email: Optional[str] = None
    metadata: Optional[dict[str, Any]] = None

    @field_validator("currency")
    @classmethod
    def currency_lower(cls, v: str) -> str:
        return v.lower().strip()


class CreatePaymentIntentResponse(BaseModel):
    client_secret: str
    payment_intent_id: str
