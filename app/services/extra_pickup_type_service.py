from datetime import datetime, timezone
from uuid import uuid4

from pymongo import ReturnDocument

from app.db.mongodb import get_database
from app.schemas.extra_pickup_type import (
    ExtraPickupTypeCreateRequest,
    ExtraPickupTypeResponse,
    ExtraPickupTypeUpdateRequest,
)


def _to_response(doc: dict) -> ExtraPickupTypeResponse:
    return ExtraPickupTypeResponse(
        pickup_type_id=doc["pickup_type_id"],
        admin_id=doc["admin_id"],
        pickup_type=doc["pickup_type"],
        additional_pricing_type=doc["additional_pricing_type"],
        base_price=doc["base_price"],
        notes=doc.get("notes", ""),
        is_active=doc["is_active"],
        created_at=doc["created_at"],
        updated_at=doc["updated_at"],
    )


async def create_extra_pickup_type(
    admin_id: str, payload: ExtraPickupTypeCreateRequest
) -> ExtraPickupTypeResponse:
    db = get_database()
    now = datetime.now(timezone.utc)
    document = {
        "pickup_type_id": str(uuid4()),
        "admin_id": admin_id,
        "pickup_type": payload.pickup_type,
        "additional_pricing_type": payload.additional_pricing_type,
        "base_price": payload.base_price,
        "notes": payload.notes,
        "is_active": payload.is_active,
        "created_at": now,
        "updated_at": now,
    }
    await db.extra_pickup_types.insert_one(document)
    return _to_response(document)


async def update_extra_pickup_type(
    pickup_type_id: str, payload: ExtraPickupTypeUpdateRequest
) -> ExtraPickupTypeResponse:
    db = get_database()
    updates = payload.model_dump(exclude_unset=True)
    if not updates:
        raise ValueError("At least one field is required for update.")

    updates["updated_at"] = datetime.now(timezone.utc)
    updated = await db.extra_pickup_types.find_one_and_update(
        {"pickup_type_id": pickup_type_id},
        {"$set": updates},
        return_document=ReturnDocument.AFTER,
    )
    if not updated:
        raise ValueError("Pickup type not found.")
    return _to_response(updated)


async def hard_delete_extra_pickup_type(pickup_type_id: str) -> bool:
    db = get_database()
    result = await db.extra_pickup_types.delete_one({"pickup_type_id": pickup_type_id})
    return result.deleted_count > 0


async def get_all_extra_pickup_types() -> list[ExtraPickupTypeResponse]:
    db = get_database()
    cursor = db.extra_pickup_types.find().sort("created_at", -1)
    docs = await cursor.to_list(length=None)
    return [_to_response(doc) for doc in docs]
