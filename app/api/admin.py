from fastapi import APIRouter, BackgroundTasks, HTTPException, status

from app.schemas.admin import (
    AdminCreateRequest,
    AdminCreateResponse,
    AdminLoginRequest,
    AdminLoginResponse,
    AdminRefreshTokenRequest,
)
from app.services.admin_service import authenticate_admin, create_admin_user, get_active_admin_by_id
from app.services.mail_service import send_admin_created_email
from app.utils.tokens import create_access_token, create_refresh_token, decode_token

router = APIRouter(prefix="/admins", tags=["admins"])


@router.post("/create", response_model=AdminCreateResponse, status_code=status.HTTP_201_CREATED)
async def create_admin(
    payload: AdminCreateRequest, background_tasks: BackgroundTasks
) -> AdminCreateResponse:
    try:
        created_admin = await create_admin_user(payload)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc

    background_tasks.add_task(send_admin_created_email, created_admin.email)

    return created_admin


@router.post("/login", response_model=AdminLoginResponse, status_code=status.HTTP_200_OK)
async def admin_login(payload: AdminLoginRequest) -> AdminLoginResponse:
    try:
        admin = await authenticate_admin(payload.email, payload.password)
    except ValueError as exc:
        message = str(exc)
        status_code = (
            status.HTTP_403_FORBIDDEN
            if message == "Admin user is inactive."
            else status.HTTP_401_UNAUTHORIZED
        )
        raise HTTPException(status_code=status_code, detail=message) from exc

    access_token = create_access_token(subject=admin.id)
    refresh_token = create_refresh_token(subject=admin.id)

    return AdminLoginResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        admin=admin,
    )


@router.post("/refresh-token", response_model=AdminLoginResponse, status_code=status.HTTP_200_OK)
async def admin_refresh_token(payload: AdminRefreshTokenRequest) -> AdminLoginResponse:
    try:
        decoded = decode_token(payload.refresh_token)
        if decoded.get("type") != "refresh":
            raise ValueError("Invalid token type.")
        subject = decoded.get("sub")
        if not subject:
            raise ValueError("Invalid token subject.")
        admin = await get_active_admin_by_id(subject)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail=str(exc)
        ) from exc

    access_token = create_access_token(subject=admin.id)
    refresh_token = create_refresh_token(subject=admin.id)

    return AdminLoginResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        admin=admin,
    )
