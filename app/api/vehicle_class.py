from fastapi import APIRouter, Depends, HTTPException, status

from app.api.dependencies import get_current_admin
from app.schemas.admin import AdminUserData
from app.schemas.vehicle_class import (
    VehicleClassCreateRequest,
    VehicleClassResponse,
    VehicleClassUpdateRequest,
)
from app.services.vehicle_class_service import (
    create_vehicle_class,
    get_all_vehicle_classes,
    hard_delete_vehicle_class,
    update_vehicle_class,
)

router = APIRouter(prefix="/vehicle-classes", tags=["vehicle-class-management"])


@router.post("", response_model=VehicleClassResponse, status_code=status.HTTP_201_CREATED)
async def create_vehicle_class_api(
    payload: VehicleClassCreateRequest,
    current_admin: AdminUserData = Depends(get_current_admin),
) -> VehicleClassResponse:
    return await create_vehicle_class(admin_id=current_admin.id, payload=payload)


@router.put("/{vehicle_class_id}", response_model=VehicleClassResponse, status_code=status.HTTP_200_OK)
async def update_vehicle_class_api(
    vehicle_class_id: str,
    payload: VehicleClassUpdateRequest,
    _: AdminUserData = Depends(get_current_admin),
) -> VehicleClassResponse:
    try:
        return await update_vehicle_class(vehicle_class_id=vehicle_class_id, payload=payload)
    except ValueError as exc:
        message = str(exc)
        code = (
            status.HTTP_400_BAD_REQUEST
            if message == "At least one field is required for update."
            else status.HTTP_404_NOT_FOUND
        )
        raise HTTPException(status_code=code, detail=message) from exc


@router.delete("/{vehicle_class_id}", status_code=status.HTTP_200_OK)
async def delete_vehicle_class_api(
    vehicle_class_id: str,
    _: AdminUserData = Depends(get_current_admin),
) -> dict[str, str]:
    deleted = await hard_delete_vehicle_class(vehicle_class_id=vehicle_class_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Vehicle class not found.")
    return {"message": "Vehicle class deleted successfully."}


@router.get("", response_model=list[VehicleClassResponse], status_code=status.HTTP_200_OK)
async def get_all_vehicle_classes_api(
    _: AdminUserData = Depends(get_current_admin),
) -> list[VehicleClassResponse]:
    return await get_all_vehicle_classes()
