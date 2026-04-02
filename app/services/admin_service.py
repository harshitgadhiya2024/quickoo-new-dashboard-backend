from datetime import datetime, timezone

from bson import ObjectId
from fastapi.concurrency import run_in_threadpool
from pymongo.errors import DuplicateKeyError

from app.db.mongodb import get_database
from app.schemas.admin import AdminCreateRequest, AdminCreateResponse, AdminUserData
from app.utils.security import hash_password, verify_password


async def create_admin_user(payload: AdminCreateRequest) -> AdminCreateResponse:
    db = get_database()
    password_hash = await run_in_threadpool(hash_password, payload.password)
    document = {
        "email": payload.email.lower(),
        "password_hash": password_hash,
        "is_active": True,
        "created_at": datetime.now(timezone.utc),
    }

    try:
        result = await db.admin_users.insert_one(document)
    except DuplicateKeyError as exc:
        raise ValueError("Admin with this email already exists.") from exc

    return AdminCreateResponse(
        id=str(result.inserted_id),
        email=document["email"],
        is_active=document["is_active"],
        created_at=document["created_at"],
    )


async def authenticate_admin(email: str, password: str) -> AdminUserData:
    db = get_database()
    admin = await db.admin_users.find_one({"email": email.lower()})

    if not admin:
        raise ValueError("Invalid email or password.")
    if not admin.get("is_active", False):
        raise ValueError("Admin user is inactive.")

    is_valid_password = await run_in_threadpool(
        verify_password, password, admin.get("password_hash", "")
    )
    if not is_valid_password:
        raise ValueError("Invalid email or password.")

    return AdminUserData(
        id=str(admin["_id"]),
        email=admin["email"],
        is_active=admin["is_active"],
        created_at=admin["created_at"],
    )


async def get_active_admin_by_id(admin_id: str) -> AdminUserData:
    db = get_database()
    if not ObjectId.is_valid(admin_id):
        raise ValueError("Invalid admin token subject.")

    admin = await db.admin_users.find_one({"_id": ObjectId(admin_id)})
    if not admin:
        raise ValueError("Admin user not found.")
    if not admin.get("is_active", False):
        raise ValueError("Admin user is inactive.")

    return AdminUserData(
        id=str(admin["_id"]),
        email=admin["email"],
        is_active=admin["is_active"],
        created_at=admin["created_at"],
    )
