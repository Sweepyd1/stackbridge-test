from sqlalchemy import Boolean, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base


class BusinessElement(Base):
    __tablename__ = "business_elements"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), unique=True)


class AccessRule(Base):
    __tablename__ = "access_rules"
    id: Mapped[int] = mapped_column(primary_key=True)
    role_id: Mapped[int] = mapped_column(ForeignKey("roles.id"))
    element_id: Mapped[int] = mapped_column(ForeignKey("business_elements.id"))

    read: Mapped[bool] = mapped_column(Boolean, default=False)
    read_all: Mapped[bool] = mapped_column(Boolean, default=False)
    create: Mapped[bool] = mapped_column(Boolean, default=False)
    update: Mapped[bool] = mapped_column(Boolean, default=False)
    update_all: Mapped[bool] = mapped_column(Boolean, default=False)
    delete: Mapped[bool] = mapped_column(Boolean, default=False)
    delete_all: Mapped[bool] = mapped_column(Boolean, default=False)
