import uuid
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from core.security import verify_password, create_access_token, decode_access_token
from repositories.user import UserRepository
from schemas.user import UserRegister, UserLogin
from models.user import User

class AuthService:
    def __init__(self, user_repo: UserRepository):
        self.user_repo = user_repo

    async def register(self, data: UserRegister) -> User:
        existing_user = await self.user_repo.get_by_email(data.email)
        if existing_user:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")
        
        default_role_id = 3 
        return await self.user_repo.create(data, default_role_id)

    async def login(self, data: UserLogin) -> dict:
        user = await self.user_repo.get_by_email(data.email)
        if not user or not verify_password(data.password, user.hashed_password):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect email or password")
        
        if not user.is_active:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Account is deactivated")

        jti = str(uuid.uuid4())
        token = create_access_token({"sub": str(user.id), "jti": jti})
        await self.user_repo.save_session(user.id, jti)
        
        return {"access_token": token, "token_type": "bearer"}

    async def logout(self, token: str) -> None:
        try:
            payload = decode_access_token(token)
            jti = payload.get("jti")
            if not jti:
                raise ValueError
            await self.user_repo.revoke_session(jti)
        except Exception:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid token")