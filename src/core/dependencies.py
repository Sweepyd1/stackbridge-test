import select
from fastapi import Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt
from sqlalchemy.ext.asyncio import AsyncSession
from core.database import get_db
from core.security import decode_access_token
from repositories.rbac import RbacRepository
from repositories.user import UserRepository
from services.auth import AuthService
from services.rbac import RbacService
from models.user import User, UserSession



def get_user_repository(db: AsyncSession = Depends(get_db)) -> UserRepository:
    return UserRepository(db)

def get_rbac_repository(db: AsyncSession = Depends(get_db)) -> RbacRepository:
    return RbacRepository(db)

def get_auth_service(user_repo: UserRepository = Depends(get_user_repository)) -> AuthService:
    return AuthService(user_repo)

def get_rbac_service(rbac_repo: RbacRepository = Depends(get_rbac_repository)) -> RbacService:
    return RbacService(rbac_repo)

async def get_current_user(
    request: Request,
    user_repo: UserRepository = Depends(get_user_repository)
) -> User:
    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
    
    try:
        payload = decode_access_token(token)
        jti = payload.get("jti")
        user_id = int(payload.get("sub"))
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token has expired")
    except jwt.InvalidTokenError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=f"Invalid token: {str(e)}")

    user = await user_repo.get_by_id(user_id)
    if not user or not user.is_active:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found or inactive")

    session = await user_repo.get_session_by_jti(jti)
    if not session or session.is_revoked:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token has been revoked")

    return user

def require_permission(element_name: str, action: str):
    async def permission_checker(
        user: User = Depends(get_current_user),
        rbac_service: RbacService = Depends(get_rbac_service)
    ):
        is_admin = user.role.name.lower() == "admin"
        if is_admin:
            return user

        has_permission = await rbac_service.check_permission(user, element_name, action)
        if not has_permission:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")
        return user
    return permission_checker