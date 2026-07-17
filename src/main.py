import contextlib

from fastapi import FastAPI
from sqlalchemy import select

from api import admin, auth, mock, users
from core.database import AsyncSessionLocal
from core.security import hash_password
from models.rbac import BusinessElement
from models.user import Role, User


@contextlib.asynccontextmanager
async def lifespan(app: FastAPI):
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(Role))
        roles = result.scalars().all()

        if not roles:
            default_roles = [
                Role(id=1, name="admin"),
                Role(id=2, name="manager"),
                Role(id=3, name="user"),
            ]
            session.add_all(default_roles)

            default_elements = [
                BusinessElement(id=1, name="products"),
                BusinessElement(id=2, name="access_rules"),
            ]
            session.add_all(default_elements)

            admin_user = User(
                first_name="Admin",
                last_name="System",
                email="admin@example.com",
                hashed_password=hash_password("admin123456"),
                role_id=1,
                is_active=True,
            )
            session.add(admin_user)

            await session.commit()

    yield


app = FastAPI(title="Auth system", lifespan=lifespan)

app.include_router(auth.router)
app.include_router(users.router)
app.include_router(admin.router)
app.include_router(mock.router)
