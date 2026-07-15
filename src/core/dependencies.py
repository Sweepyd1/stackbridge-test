from fastapi import Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from .core.database import get_db
from .services.auth_service import AuthService
from .services.rbac_service import RbacService
from .models.user import User

security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db),
) -> User:
    auth_service = AuthService(db)

    try:
        payload = auth_service.__class__.__dict__["decode_access_token"](
            credentials.credentials
        )
        jti = payload.get("jti")
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token structure"
        )

    user = await auth_service.get_current_user(credentials.credentials)

    user_repo = auth_service.user_repo
    from sqlalchemy import select
    from .models.user import UserSession

    result = await db.execute(select(UserSession).where(UserSession.token_jti == jti))
    session = result.scalars().first()

    if not session or session.is_revoked:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Token has been revoked"
        )

    return user


def require_permission(element_name: str, action: str):
    async def permission_checker(
        user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)
    ):
        rbac_service = RbacService(db)

        is_admin = user.role.name.lower() == "admin"
        if is_admin:
            return user

        has_permission = await rbac_service.check_permission(user, element_name, action)
        if not has_permission:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to perform this action",
            )
        return user

    return permission_checker
