from pydantic import BaseModel, Field
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

from app.database import Base


class Gender(Base):
    __tablename__ = "genders"

    id = Column(Integer, primary_key=True)
    name = Column(String(50))

    users = relationship("User", back_populates="gender")


class GenderBase(BaseModel):
    name: str = Field()


class GenderResponse(GenderBase):
    id: int = Field()
    name: str = Field()

    class Config:
        from_attributes = True
