from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from .repositories.rbac_repo import RbacRepository
from .models.user import User
from .schemas.rbac import AccessRuleCreate, AccessRuleResponse


class RbacService:
    def __init__(self, session: AsyncSession):
        self.rbac_repo = RbacRepository(session)

    async def check_permission(
        self, user: User, element_name: str, action: str, owner_id: int | None = None
    ) -> bool:
        element = await self.rbac_repo.get_element_by_name(element_name)
        if not element:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Resource not found"
            )

        rule = await self.rbac_repo.get_rule(user.role_id, element.id)
        if not rule:
            return False

        if action == "read":
            return rule.read_all or (rule.read and owner_id == user.id)
        if action == "update":
            return rule.update_all or (rule.update and owner_id == user.id)
        if action == "delete":
            return rule.delete_all or (rule.delete and owner_id == user.id)

        return getattr(rule, action, False)

    async def create_rule(self, data: AccessRuleCreate) -> AccessRuleResponse:
        rule = await self.rbac_repo.create_rule(data)
        return AccessRuleResponse.model_validate(rule)
