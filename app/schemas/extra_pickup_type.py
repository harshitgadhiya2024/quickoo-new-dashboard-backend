from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class ExtraPickupTypeCreateRequest(BaseModel):
    pickup_type: str
    additional_pricing_type: str
    base_price: int = Field(ge=0)
    notes: str = ""
    is_active: bool = True


class ExtraPickupTypeUpdateRequest(BaseModel):
    pickup_type: Optional[str] = None
    additional_pricing_type: Optional[str] = None
    base_price: Optional[int] = Field(default=None, ge=0)
    notes: Optional[str] = None
    is_active: Optional[bool] = None


class ExtraPickupTypeResponse(BaseModel):
    pickup_type_id: str
    admin_id: str
    pickup_type: str
    additional_pricing_type: str
    base_price: int
    notes: str
    is_active: bool
    created_at: datetime
    updated_at: datetime
