from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from src.core.database import get_db
from src.repositories.user_repo import UserRepository
from src.dependencies import get_current_user
from src.schemas.user import UserUpdate, UserResponse
from src.models.user import User

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
    db: AsyncSession = Depends(get_db),
):
    user_repo = UserRepository(db)
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
    user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)
):
    user_repo = UserRepository(db)
    await user_repo.soft_delete(user)
