from fastapi import APIRouter, Depends

from core.dependencies import get_rbac_service, require_permission
from models.user import User
from schemas.rbac import AccessRuleCreate, AccessRuleResponse
from services.rbac import RbacService

router = APIRouter(prefix="/admin/rules", tags=["Admin RBAC"])


@router.post("/", response_model=AccessRuleResponse, status_code=201)
async def create_access_rule(
    data: AccessRuleCreate,
    user: User = Depends(require_permission("access_rules", "create")),
    rbac_service: RbacService = Depends(get_rbac_service),
):
    return await rbac_service.create_rule(data)
