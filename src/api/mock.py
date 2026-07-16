from fastapi import APIRouter, Depends

from core.dependencies import require_permission
from models.user import User

router = APIRouter(prefix="/products", tags=["Mock Business"])


@router.get("/")
async def get_products(user: User = Depends(require_permission("products", "read"))):
    return [
        {"id": 1, "name": "Laptop", "owner_id": 1},
        {"id": 2, "name": "Mouse", "owner_id": 2},
    ]


@router.post("/")
async def create_product(
    user: User = Depends(require_permission("products", "create")),
):
    return {"message": "Product created", "owner_id": user.id}
