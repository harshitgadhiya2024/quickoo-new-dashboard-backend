from pymongo import ASCENDING

from app.db.mongodb import get_database


async def ensure_indexes() -> None:
    db = get_database()
    await db.admin_users.create_index([("email", ASCENDING)], unique=True, name="idx_admin_email_unique")
    await db.vehicle_classes.create_index(
        [("vehicle_class_id", ASCENDING)],
        unique=True,
        name="idx_vehicle_class_id_unique",
    )
    await db.extra_pickup_types.create_index(
        [("pickup_type_id", ASCENDING)],
        unique=True,
        name="idx_pickup_type_id_unique",
    )
    await db.orders.create_index(
        [("order_id", ASCENDING)],
        unique=True,
        name="idx_order_id_unique",
    )
