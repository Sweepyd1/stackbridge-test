from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from .models.rbac import AccessRule, BusinessElement
from .schemas.rbac import AccessRuleCreate


class RbacRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_rule(self, role_id: int, element_id: int) -> AccessRule | None:
        result = await self.session.execute(
            select(AccessRule).where(
                AccessRule.role_id == role_id, AccessRule.element_id == element_id
            )
        )
        return result.scalars().first()

    async def get_element_by_name(self, name: str) -> BusinessElement | None:
        result = await self.session.execute(
            select(BusinessElement).where(BusinessElement.name == name)
        )
        return result.scalars().first()

    async def create_rule(self, data: AccessRuleCreate) -> AccessRule:
        rule = AccessRule(**data.model_dump())
        self.session.add(rule)
        await self.session.commit()
        await self.session.refresh(rule)
        return rule
