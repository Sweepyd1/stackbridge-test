from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from src.core.database import get_db
from src.services.rbac_service import RbacService
from src.dependencies import require_permission
from src.schemas.rbac import AccessRuleCreate, AccessRuleResponse
from src.models.user import User

router = APIRouter(prefix="/admin/rules", tags=["Admin RBAC"])


@router.post("/", response_model=AccessRuleResponse, status_code=201)
async def create_access_rule(
    data: AccessRuleCreate,
    user: User = Depends(require_permission("access_rules", "create")),
    db: AsyncSession = Depends(get_db),
):
    rbac_service = RbacService(db)
    return await rbac_service.create_rule(data)
