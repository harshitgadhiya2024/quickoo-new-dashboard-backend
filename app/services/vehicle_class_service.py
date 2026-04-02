from datetime import datetime, timezone
from uuid import uuid4

from pymongo import ReturnDocument

from app.db.mongodb import get_database
from app.schemas.vehicle_class import (
    VehicleClassCreateRequest,
    VehicleClassResponse,
    VehicleClassUpdateRequest,
)


def _to_response(doc: dict) -> VehicleClassResponse:
    return VehicleClassResponse(
        vehicle_class_id=doc["vehicle_class_id"],
        admin_id=doc["admin_id"],
        vehicle_class_image=doc["vehicle_class_image"],
        class_name=doc["class_name"],
        allow_passengers=doc["allow_passengers"],
        allow_luggage=doc["allow_luggage"],
        base_price=doc["base_price"],
        base_price_per_default_miles=doc["base_price_per_default_miles"],
        extra_price_per_miles=doc["extra_price_per_miles"],
        is_active=doc["is_active"],
        created_at=doc["created_at"],
        updated_at=doc["updated_at"],
    )


async def create_vehicle_class(admin_id: str, payload: VehicleClassCreateRequest) -> VehicleClassResponse:
    db = get_database()
    now = datetime.now(timezone.utc)
    document = {
        "vehicle_class_id": str(uuid4()),
        "admin_id": admin_id,
        "vehicle_class_image": payload.vehicle_class_image,
        "class_name": payload.class_name,
        "allow_passengers": payload.allow_passengers,
        "allow_luggage": payload.allow_luggage,
        "base_price": payload.base_price,
        "base_price_per_default_miles": payload.base_price_per_default_miles,
        "extra_price_per_miles": payload.extra_price_per_miles,
        "is_active": True,
        "created_at": now,
        "updated_at": now,
    }
    await db.vehicle_classes.insert_one(document)
    return _to_response(document)


async def update_vehicle_class(
    vehicle_class_id: str, payload: VehicleClassUpdateRequest
) -> VehicleClassResponse:
    db = get_database()
    updates = payload.model_dump(exclude_unset=True)
    if not updates:
        raise ValueError("At least one field is required for update.")

    updates["updated_at"] = datetime.now(timezone.utc)
    updated = await db.vehicle_classes.find_one_and_update(
        {"vehicle_class_id": vehicle_class_id},
        {"$set": updates},
        return_document=ReturnDocument.AFTER,
    )
    if not updated:
        raise ValueError("Vehicle class not found.")
    return _to_response(updated)


async def hard_delete_vehicle_class(vehicle_class_id: str) -> bool:
    db = get_database()
    result = await db.vehicle_classes.delete_one({"vehicle_class_id": vehicle_class_id})
    return result.deleted_count > 0


async def get_all_vehicle_classes() -> list[VehicleClassResponse]:
    db = get_database()
    cursor = db.vehicle_classes.find().sort("created_at", -1)
    docs = await cursor.to_list(length=None)
    return [_to_response(doc) for doc in docs]
