import uuid
from datetime import datetime, timezone

from pydantic import BaseModel, Field, computed_field
from sqlalchemy import CHAR, Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.database import Base
from app.models import RoleResponse
from app.models.gender import GenderResponse


class User(Base):
    __tablename__ = "users"

    id = Column(CHAR(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(100))
    surname = Column(String(100))
    patronymic = Column(String(100))
    username = Column(String(100))
    gender_id = Column(Integer, ForeignKey("genders.id"))
    birthday = Column(DateTime)
    password = Column(String(100))
    status = Column(String(50), default="active")
    created_at = Column(DateTime, default=datetime.now(timezone.utc))

    roles = relationship("Role", secondary="user_roles", back_populates="users")

    gender = relationship("Gender", back_populates="users")


class UserBase(BaseModel):
    name: str = Field()
    surname: str = Field()
    patronymic: str = Field()
    username: str = Field()
    birthday: datetime = Field()


class UserCreate(UserBase):
    gender_id: int = Field()
    password: str = Field()


class UserResponse(UserBase):
    id: str = Field()
    status: str = Field()
    created_at: datetime = Field()
    gender: GenderResponse = Field()
    roles: list[RoleResponse] = Field(default_factory=list)

    @computed_field
    def roles_count(self) -> int:
        return len(self.roles)

    class Config:
        from_attributes = True


class UserAddRole(BaseModel):
    user_id: str = Field()
    role_id: str = Field()
