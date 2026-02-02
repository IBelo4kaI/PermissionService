import uuid
from datetime import datetime

from pydantic import BaseModel
from sqlalchemy import CHAR, Column, DateTime, ForeignKey, String

from ..database import Base


class SessionDB(Base):
    __tablename__ = "sessions"

    id = Column(CHAR(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(CHAR(36), ForeignKey("users.id"))
    token_hash = Column(String(64))
    expires_at = Column(DateTime)


class SessionBase(BaseModel):
    user_id: str
    token_hash: str
    expires_at: datetime


class SessionCreate(SessionBase):
    pass
