from fastapi import APIRouter, Depends, HTTPException, Response, status, Request
from sqlalchemy.ext.asyncio import AsyncSession
from core.database import get_db
from services.auth import AuthService
from schemas.user import UserRegister, UserLogin, TokenResponse, UserResponse
from core.dependencies import get_auth_service, get_current_user
from models.user import User
from core.config import settings

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(
    data: UserRegister, 
    auth_service: AuthService = Depends(get_auth_service)
):
    user = await auth_service.register(data)
    return UserResponse(
        id=user.id,
        first_name=user.first_name,
        last_name=user.last_name,
        email=user.email,
        role_name=user.role.name,
    )

@router.post("/login", response_model=TokenResponse)
async def login(
    data: UserLogin, 
    response: Response,
    auth_service: AuthService = Depends(get_auth_service),
    
):
    token_data = await auth_service.login(data)
    
    response.set_cookie(
        key="access_token",
        value=token_data["access_token"],
        httponly=True,
        max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        samesite="lax"
    )
    return token_data

@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(
    request: Request,
    response: Response,
    auth_service: AuthService = Depends(get_auth_service),
    
):
    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    await auth_service.logout(token)
    response.delete_cookie(key="access_token")
