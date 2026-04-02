from fastapi import APIRouter, Depends, HTTPException, status

from app.api.dependencies import get_current_admin
from app.schemas.admin import AdminUserData
from app.schemas.extra_pickup_type import (
    ExtraPickupTypeCreateRequest,
    ExtraPickupTypeResponse,
    ExtraPickupTypeUpdateRequest,
)
from app.services.extra_pickup_type_service import (
    create_extra_pickup_type,
    get_all_extra_pickup_types,
    hard_delete_extra_pickup_type,
    update_extra_pickup_type,
)

router = APIRouter(prefix="/extra-pickup-types", tags=["extra-pickup-type-management"])


@router.post("", response_model=ExtraPickupTypeResponse, status_code=status.HTTP_201_CREATED)
async def create_extra_pickup_type_api(
    payload: ExtraPickupTypeCreateRequest,
    current_admin: AdminUserData = Depends(get_current_admin),
) -> ExtraPickupTypeResponse:
    return await create_extra_pickup_type(admin_id=current_admin.id, payload=payload)


@router.put("/{pickup_type_id}", response_model=ExtraPickupTypeResponse, status_code=status.HTTP_200_OK)
async def update_extra_pickup_type_api(
    pickup_type_id: str,
    payload: ExtraPickupTypeUpdateRequest,
    _: AdminUserData = Depends(get_current_admin),
) -> ExtraPickupTypeResponse:
    try:
        return await update_extra_pickup_type(pickup_type_id=pickup_type_id, payload=payload)
    except ValueError as exc:
        message = str(exc)
        code = (
            status.HTTP_400_BAD_REQUEST
            if message == "At least one field is required for update."
            else status.HTTP_404_NOT_FOUND
        )
        raise HTTPException(status_code=code, detail=message) from exc


@router.delete("/{pickup_type_id}", status_code=status.HTTP_200_OK)
async def delete_extra_pickup_type_api(
    pickup_type_id: str,
    _: AdminUserData = Depends(get_current_admin),
) -> dict[str, str]:
    deleted = await hard_delete_extra_pickup_type(pickup_type_id=pickup_type_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Pickup type not found.")
    return {"message": "Pickup type deleted successfully."}


@router.get("", response_model=list[ExtraPickupTypeResponse], status_code=status.HTTP_200_OK)
async def get_all_extra_pickup_types_api(
    _: AdminUserData = Depends(get_current_admin),
) -> list[ExtraPickupTypeResponse]:
    return await get_all_extra_pickup_types()
