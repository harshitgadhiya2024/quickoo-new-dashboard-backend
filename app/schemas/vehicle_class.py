from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class VehicleClassCreateRequest(BaseModel):
    vehicle_class_image: str
    class_name: str
    allow_passengers: int = Field(ge=1)
    allow_luggage: int = Field(ge=0)
    base_price: float = Field(ge=0)
    base_price_per_default_miles: int = Field(ge=1)
    extra_price_per_miles: float = Field(ge=0)


class VehicleClassUpdateRequest(BaseModel):
    vehicle_class_image: Optional[str] = None
    class_name: Optional[str] = None
    allow_passengers: Optional[int] = Field(default=None, ge=1)
    allow_luggage: Optional[int] = Field(default=None, ge=0)
    base_price: Optional[float] = Field(default=None, ge=0)
    base_price_per_default_miles: Optional[int] = Field(default=None, ge=1)
    extra_price_per_miles: Optional[float] = Field(default=None, ge=0)
    is_active: Optional[bool] = None


class VehicleClassResponse(BaseModel):
    vehicle_class_id: str
    admin_id: str
    vehicle_class_image: str
    class_name: str
    allow_passengers: int
    allow_luggage: int
    base_price: float
    base_price_per_default_miles: int
    extra_price_per_miles: float
    is_active: bool
    created_at: datetime
    updated_at: datetime
