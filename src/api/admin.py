from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from .core.database import get_db
from .services.rbac_service import RbacService
from .dependencies import require_permission
from .schemas.rbac import AccessRuleCreate, AccessRuleResponse
from .models.user import User

router = APIRouter(prefix="/admin/rules", tags=["Admin RBAC"])


@router.post("/", response_model=AccessRuleResponse, status_code=201)
async def create_access_rule(
    data: AccessRuleCreate,
    user: User = Depends(require_permission("access_rules", "create")),
    db: AsyncSession = Depends(get_db),
):
    rbac_service = RbacService(db)
    return await rbac_service.create_rule(data)
