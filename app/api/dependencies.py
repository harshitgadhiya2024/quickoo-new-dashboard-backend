from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.schemas.admin import AdminUserData
from app.services.admin_service import get_active_admin_by_id
from app.utils.tokens import decode_token

bearer_scheme = HTTPBearer(auto_error=True)


async def get_current_admin(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
) -> AdminUserData:
    token = credentials.credentials
    try:
        decoded = decode_token(token)
        if decoded.get("type") != "access":
            raise ValueError("Invalid token type.")
        subject = decoded.get("sub")
        if not subject:
            raise ValueError("Invalid token subject.")
        return await get_active_admin_by_id(subject)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(exc),
        ) from exc
