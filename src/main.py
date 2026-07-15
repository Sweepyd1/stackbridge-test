from fastapi import FastAPI
from api.auth import router as auth_router

app = FastAPI(title="Custom Auth & RBAC System")

app.include_router(auth_router)
# app.include_router(users.router)
# app.include_router(admin.router)
# app.include_router(mock.router)
