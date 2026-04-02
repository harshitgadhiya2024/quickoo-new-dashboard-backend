from datetime import date, datetime, time, timezone
from uuid import uuid4

from pymongo import ReturnDocument

from app.db.mongodb import get_database
from app.schemas.order import OrderCreateRequest, OrderResponse, OrderUpdateRequest


def _to_response(doc: dict) -> OrderResponse:
    return OrderResponse(**doc)


def _mongo_pickup_time(value: time) -> str:
    return value.isoformat()


def _mongo_pickup_date(value: date) -> datetime:
    """BSON cannot encode datetime.date; store UTC midnight for the calendar day."""
    return datetime(value.year, value.month, value.day, 0, 0, 0, tzinfo=timezone.utc)


async def create_order(payload: OrderCreateRequest) -> OrderResponse:
    db = get_database()
    now = datetime.now(timezone.utc)
    document = {
        "order_id": str(uuid4()),
        "from": payload.from_.model_dump(),
        "to": payload.to.model_dump(),
        "stops": [s.model_dump() for s in payload.stops],
        "flight_number": payload.flight_number,
        "pickup_date": _mongo_pickup_date(payload.pickup_date),
        "pickup_time": _mongo_pickup_time(payload.pickup_time),
        "vehicle_class": payload.vehicle_class,
        "first_name": payload.first_name,
        "last_name": payload.last_name,
        "email": payload.email,
        "phonenumber": payload.phonenumber,
        "special_request": payload.special_request,
        "route_distance": payload.route_distance,
        "total_price": payload.total_price,
        "pricing_breakdown": payload.pricing_breakdown,
        "is_payment_paid": payload.is_payment_paid,
        "transcation_id": payload.transcation_id,
        "status": "not started",
        "created_at": now,
        "updated_at": now,
    }
    await db.orders.insert_one(document)
    return _to_response(document)


async def get_all_orders() -> list[OrderResponse]:
    db = get_database()
    docs = await db.orders.find().sort("created_at", -1).to_list(length=None)
    return [_to_response(doc) for doc in docs]


async def update_order(order_id: str, payload: OrderUpdateRequest) -> OrderResponse:
    db = get_database()
    updates = payload.model_dump(exclude_unset=True, by_alias=True)
    if not updates:
        raise ValueError("At least one field is required for update.")
    updates.pop("order_id", None)
    if "pickup_date" in updates and isinstance(updates["pickup_date"], date):
        updates["pickup_date"] = _mongo_pickup_date(updates["pickup_date"])
    if "pickup_time" in updates and isinstance(updates["pickup_time"], time):
        updates["pickup_time"] = _mongo_pickup_time(updates["pickup_time"])
    updates["updated_at"] = datetime.now(timezone.utc)

    updated = await db.orders.find_one_and_update(
        {"order_id": order_id},
        {"$set": updates},
        return_document=ReturnDocument.AFTER,
    )
    if not updated:
        raise ValueError("Order not found.")
    return _to_response(updated)
