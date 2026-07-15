from pydantic import BaseModel


class AccessRuleCreate(BaseModel):
    role_id: int
    element_id: int
    read: bool = False
    read_all: bool = False
    create: bool = False
    update: bool = False
    update_all: bool = False
    delete: bool = False
    delete_all: bool = False


class AccessRuleResponse(AccessRuleCreate):
    id: int

    class Config:
        from_attributes = True
