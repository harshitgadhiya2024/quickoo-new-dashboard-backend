from datetime import datetime, date, time
from typing import Annotated, Any, Optional

from pydantic import (
    BaseModel,
    BeforeValidator,
    ConfigDict,
    EmailStr,
    Field,
    field_validator,
    model_validator,
)


def _parse_pickup_time(v: Any) -> time:
    if isinstance(v, time):
        return v
    if isinstance(v, datetime):
        return v.replace(tzinfo=None).time() if v.tzinfo else v.time()
    if isinstance(v, str):
        s = v.strip()
        if not s:
            raise ValueError("pickup_time cannot be empty")
        if "T" in s or s.endswith("Z"):
            normalized = s.replace("Z", "+00:00")
            dt = datetime.fromisoformat(normalized)
            return dt.time()
        parts = s.split(":")
        if len(parts) >= 2:
            h = int(parts[0])
            m = int(parts[1])
            if len(parts) > 2:
                sec = int(float(parts[2]))
            else:
                sec = 0
            return time(h, m, sec)
    raise ValueError("Invalid pickup_time format")


def _parse_pickup_time_optional(v: Any) -> Optional[time]:
    if v is None:
        return None
    return _parse_pickup_time(v)


PickupTime = Annotated[time, BeforeValidator(_parse_pickup_time)]
PickupTimeOptional = Annotated[Optional[time], BeforeValidator(_parse_pickup_time_optional)]


class OrderLocation(BaseModel):
    address: str
    latitude: float
    longitude: float


class OrderCreateRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    from_: OrderLocation = Field(..., alias="from")
    to: OrderLocation
    stops: list[OrderLocation] = Field(default_factory=list)
    flight_number: Optional[str] = None
    pickup_date: date
    pickup_time: PickupTime
    vehicle_class: str
    first_name: str
    last_name: str
    email: EmailStr
    phonenumber: str
    special_request: Optional[str] = None
    route_distance: float = Field(ge=0)
    total_price: float = Field(ge=0)
    pricing_breakdown: dict
    is_payment_paid: bool = False
    transcation_id: Optional[str] = None

    @field_validator("flight_number", "special_request", "transcation_id", mode="before")
    @classmethod
    def empty_str_to_none(cls, v: Any) -> Any:
        if v == "":
            return None
        return v


class OrderUpdateRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    from_: Optional[OrderLocation] = Field(default=None, alias="from")
    to: Optional[OrderLocation] = None
    stops: Optional[list[OrderLocation]] = None
    flight_number: Optional[str] = None
    pickup_date: Optional[date] = None
    pickup_time: PickupTimeOptional = None
    vehicle_class: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[EmailStr] = None
    phonenumber: Optional[str] = None
    special_request: Optional[str] = None
    route_distance: Optional[float] = Field(default=None, ge=0)
    total_price: Optional[float] = Field(default=None, ge=0)
    pricing_breakdown: Optional[dict] = None
    is_payment_paid: Optional[bool] = None
    transcation_id: Optional[str] = None
    status: Optional[str] = None

    @field_validator("flight_number", "special_request", "transcation_id", mode="before")
    @classmethod
    def empty_str_to_none(cls, v: Any) -> Any:
        if v == "":
            return None
        return v


class OrderResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    order_id: str
    from_: OrderLocation = Field(alias="from")
    to: OrderLocation
    stops: list[OrderLocation]
    flight_number: Optional[str]
    pickup_date: date
    pickup_time: time
    vehicle_class: str
    first_name: str
    last_name: str
    email: EmailStr
    phonenumber: str
    special_request: Optional[str]
    route_distance: float
    total_price: float
    pricing_breakdown: dict
    is_payment_paid: bool
    transcation_id: Optional[str]
    status: str
    created_at: datetime
    updated_at: datetime

    @model_validator(mode="before")
    @classmethod
    def coerce_mongo_doc(cls, data: Any) -> Any:
        if not isinstance(data, dict):
            return data
        out = dict(data)
        pd = out.get("pickup_date")
        if isinstance(pd, datetime):
            out["pickup_date"] = pd.date()
        pt = out.get("pickup_time")
        if isinstance(pt, str):
            out["pickup_time"] = _parse_pickup_time(pt)
        elif isinstance(pt, datetime):
            out["pickup_time"] = pt.time()
        elif isinstance(pt, time):
            pass
        return out
