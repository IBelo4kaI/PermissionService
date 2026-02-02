import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from pydantic import BaseModel, Field, computed_field
from sqlalchemy import CHAR, Column, DateTime, String
from sqlalchemy.orm import relationship

from ..database import Base

if TYPE_CHECKING:
    from app.models.permission import PermissionBase


class Service(Base):
    __tablename__ = "services"

    id = Column(CHAR(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(255))
    description = Column(String(500))
    image_url = Column(String(500))
    prefix = Column(String(5))
    created_at = Column(DateTime, default=datetime.utcnow)

    roles = relationship("Role", back_populates="service")
    permissions = relationship("Permission", back_populates="service")


class ServiceBase(BaseModel):
    name: str = Field(max_length=100)
    description: str = Field()
    image_url: str | None = Field(default=None)
    prefix: str = Field(max_length=5)

    class Config:
        from_attributes = True


class ServiceCreate(ServiceBase):
    pass


class ServiceResponse(ServiceBase):
    id: str = Field()
    service_name: str = Field(alias="name")
    created_at: datetime = Field()
    permissions: list[PermissionBase] | None = Field(exclude=True)

    @computed_field
    def permissions_count(self) -> int:
        return len(self.permissions) if self.permissions else 0  # pyright: ignore[reportArgumentType]
