from datetime import datetime

from pydantic import BaseModel, EmailStr, Field


class AdminCreateRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)


class AdminCreateResponse(BaseModel):
    id: str
    email: EmailStr
    is_active: bool
    created_at: datetime


class AdminLoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)


class AdminUserData(BaseModel):
    id: str
    email: EmailStr
    is_active: bool
    created_at: datetime


class AdminLoginResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    admin: AdminUserData


class AdminRefreshTokenRequest(BaseModel):
    refresh_token: str
