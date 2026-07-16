from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from core.database import get_db
from repositories.user import UserRepository
from core.dependencies import get_current_user, get_user_repository
from schemas.user import UserUpdate, UserResponse
from models.user import User



router = APIRouter(prefix="/users", tags=["Users"])

@router.get("/me", response_model=UserResponse)
async def get_me(user: User = Depends(get_current_user)):
    return UserResponse(
        id=user.id,
        first_name=user.first_name,
        last_name=user.last_name,
        email=user.email,
        role_name=user.role.name,
    )

@router.patch("/me", response_model=UserResponse)
async def update_me(
    data: UserUpdate, 
    user: User = Depends(get_current_user),
    user_repo: UserRepository = Depends(get_user_repository)
):
    updated_user = await user_repo.update(user, data.first_name, data.last_name)
    return UserResponse(
        id=updated_user.id,
        first_name=updated_user.first_name,
        last_name=updated_user.last_name,
        email=updated_user.email,
        role_name=updated_user.role.name,
    )

@router.delete("/me", status_code=status.HTTP_204_NO_CONTENT)
async def delete_me(
    user: User = Depends(get_current_user), 
    user_repo: UserRepository = Depends(get_user_repository)
):
    await user_repo.soft_delete(user)
