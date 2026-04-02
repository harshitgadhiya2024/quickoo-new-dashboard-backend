from typing import Any, Optional

from pydantic import BaseModel, ConfigDict, Field


class Location(BaseModel):
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)


class QuoteRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    from_: Location = Field(..., alias="from")
    to: Location
    pickup_type: Optional[str] = None


class PriceBreakdownLine(BaseModel):
    description: str
    amount: float


class VehicleQuoteItem(BaseModel):
    vehicle_class_id: str
    vehicle_class_image: str
    class_name: str
    allow_passengers: int
    allow_luggage: int
    base_price: float
    base_price_per_default_miles: int
    extra_price_per_miles: float
    is_active: bool
    price_breakdown: list[PriceBreakdownLine]
    total_price: float


class QuoteResponse(BaseModel):
    distance_miles: float
    quotes_break_down_price_list: list[dict[str, Any]]
    vehicle_quotes: list[VehicleQuoteItem]
