from fastapi import APIRouter, Depends, HTTPException, Request, Response, status

from core.config import settings
from core.dependencies import get_auth_service
from schemas.user import TokenResponse, UserLogin, UserRegister, UserResponse
from services.auth import AuthService

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post(
    "/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED
)
async def register(
    data: UserRegister,
    response: Response,
    auth_service: AuthService = Depends(get_auth_service),
):
    user = await auth_service.register(data)

    token_data = await auth_service.create_token_for_user(user)

    response.set_cookie(
        key="access_token",
        value=token_data["access_token"],
        httponly=True,
        max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        samesite="lax",
    )

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
        samesite="lax",
    )


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
