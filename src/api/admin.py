from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from core.database import get_db
from services.rbac import RbacService
from core.dependencies import get_rbac_service, require_permission
from schemas.rbac import AccessRuleCreate, AccessRuleResponse
from models.user import User



router = APIRouter(prefix="/admin/rules", tags=["Admin RBAC"])

@router.post("/", response_model=AccessRuleResponse, status_code=201)
async def create_access_rule(
    data: AccessRuleCreate,
    user: User = Depends(require_permission("access_rules", "create")),
    rbac_service: RbacService = Depends(get_rbac_service)
):
    return await rbac_service.create_rule(data)
