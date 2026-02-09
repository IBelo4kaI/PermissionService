import uuid
from datetime import datetime
from typing import TYPE_CHECKING, Union

from pydantic import BaseModel, Field, computed_field
from sqlalchemy import CHAR, Column, DateTime, ForeignKey, String
from sqlalchemy.orm import relationship

from ..database import Base

if TYPE_CHECKING:
    from app.models.service import ServiceBase


class Permission(Base):
    __tablename__ = "permissions"

    id = Column(CHAR(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    service_id = Column(CHAR(36), ForeignKey("services.id"))
    code = Column(String(255))
    name = Column(String(255))
    description = Column(String(500))
    created_at = Column(DateTime, default=datetime.utcnow)

    roles = relationship("Role", secondary="role_permissions", back_populates="permissions")
    service = relationship("Service", back_populates="permissions")


class PermissionBase(BaseModel):
    service_id: str | None = Field(default=None)
    code: str = Field()
    name: str = Field()
    description: str = Field()

    class Config:
        from_attributes = True


class PermissionCreate(PermissionBase):
    pass


class PermissionResponse(PermissionBase):
    id: str = Field()
    created_at: datetime = Field()
    service: Union["ServiceBase", None] = Field(exclude=True)

    @computed_field
    def service_name(self) -> str:
        return self.service.name if self.service else ""


class PermissionWithUse(BaseModel):
    id: str
    service_id: str | None
    code: str
    name: str
    description: str
    created_at: str  # будет в формате dd.mm.yyyy HH:MM
    service_name: str | None
    use: bool  # используется ли разрешение в данной роли


class UserRoleInfo(BaseModel):
    id: str
    name: str
    surname: str
    username: str


class RoleDetailedResponse(BaseModel):
    id: str
    name: str
    description: str
    is_global: int
    created_at: str  # будет в формате dd.mm.yyyy HH:MM
    used_permissions_count: int  # количество разрешений с use: true
    permissions_by_service: dict[str, list[PermissionWithUse]]  # группировка по service_id
    users: list[UserRoleInfo]  # пользователи, имеющие эту роль

    class Config:
        from_attributes = True
