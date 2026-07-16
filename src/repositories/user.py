from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from models.user import User, UserSession
from core.security import hash_password
from schemas.user import UserRegister

class UserRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_email(self, email: str) -> User | None:
        result = await self.session.execute(
            select(User).options(selectinload(User.role)).where(User.email == email)
        )
        return result.scalars().first()

    async def get_by_id(self, user_id: int) -> User | None:
        result = await self.session.execute(
            select(User).options(selectinload(User.role)).where(User.id == user_id)
        )
        return result.scalars().first()

    async def create(self, data: UserRegister, role_id: int) -> User:
        user = User(
            first_name=data.first_name,
            last_name=data.last_name,
            email=data.email,
            hashed_password=hash_password(data.password),
            role_id=role_id
        )
        self.session.add(user)
        await self.session.commit()
        
        result = await self.session.execute(
            select(User).options(selectinload(User.role)).where(User.id == user.id)
        )
        return result.scalars().first()

    async def soft_delete(self, user: User) -> None:
        user.is_active = False
        await self.session.commit()

    async def update(self, user: User, first_name: str | None, last_name: str | None) -> User:
        if first_name: user.first_name = first_name
        if last_name: user.last_name = last_name
        await self.session.commit()
        
        result = await self.session.execute(
            select(User).options(selectinload(User.role)).where(User.id == user.id)
        )
        return result.scalars().first()

    async def save_session(self, user_id: int, token_jti: str) -> UserSession:
        session = UserSession(user_id=user_id, token_jti=token_jti)
        self.session.add(session)
        await self.session.commit()
        return session

    async def get_session_by_jti(self, jti: str) -> UserSession | None:
        result = await self.session.execute(
            select(UserSession).where(UserSession.token_jti == jti)
        )
        return result.scalars().first()

    async def revoke_session(self, token_jti: str) -> bool:
        session = await self.get_session_by_jti(token_jti)
        if session:
            session.is_revoked = True
            await self.session.commit()
            return True
        return False