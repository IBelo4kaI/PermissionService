import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from pydantic import BaseModel, Field, computed_field
from sqlalchemy import CHAR, Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.database import Base

if TYPE_CHECKING:
    from app.models.permission import PermissionBase


class Role(Base):
    __tablename__ = "roles"

    id = Column(CHAR(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    service_id = Column(CHAR(36), ForeignKey("services.id"))
    name = Column(String(100))
    description = Column(String(500))
    is_global = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)

    users = relationship("User", secondary="user_roles")
    permissions = relationship("Permission", secondary="role_permissions", back_populates="roles")
    service = relationship("Service", back_populates="roles")


class RolePermission(Base):
    __tablename__ = "role_permissions"

    role_id = Column(
        CHAR(36),
        ForeignKey("roles.id", ondelete="CASCADE"),
        primary_key=True,
    )
    permission_id = Column(
        CHAR(36),
        ForeignKey("permissions.id", ondelete="CASCADE"),
        primary_key=True,
    )
    granted_at = Column(DateTime, default=datetime.utcnow)


class RoleBase(BaseModel):
    service_id: str | None = Field(default=None)
    name: str = Field()
    description: str = Field()
    is_global: int = Field()


class RoleCreate(RoleBase):
    pass


class RoleResponse(RoleBase):
    id: str = Field()
    service_name: str | None = Field(default=None)
    created_at: datetime = Field()
    permissions: list["PermissionBase"] | None = Field(exclude=True)
    user_count: int = Field(default=0)  # количество пользователей с этой ролью
    permissions_count: int = Field(default=0)  # количество разрешений для этой роли

    class Config:
        from_attributes = True


class RoleAddPermission(BaseModel):
    role_id: str
    perm_id: str
