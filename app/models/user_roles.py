from sqlalchemy import CHAR, Column, ForeignKey

from app.database import Base


class UserRole(Base):
    __tablename__ = "user_roles"

    user_id = Column(CHAR(36), ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    role_id = Column(CHAR(36), ForeignKey("roles.id", ondelete="CASCADE"), primary_key=True)
