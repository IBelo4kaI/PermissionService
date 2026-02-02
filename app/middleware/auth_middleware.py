import hashlib
from datetime import datetime, timezone

from fastapi import Cookie, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload

from app.database import get_db
from app.models.role import Role
from app.models.session import SessionDB
from app.models.user import User
from app.repositories.permission_repository import PermissionRepository
from app.repositories.session_repository import SessionRepository


def require_permission(entity: str, action: str):
    service_name = "perm"

    def dependency(
        session_token: str | None = Cookie(default=None, alias="session"),
        db: Session = Depends(get_db),
    ):
        if not session_token:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Session token missing"
            )

        session_repository = SessionRepository(db)

        session = session_repository.get_by_token(session_token)

        if not session:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid session")

        perm_repository = PermissionRepository(db)

        exist = perm_repository.exist_by_user_id(str(session.user_id), service_name, entity, action)

        if not exist:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Нет доступа")

        return session

    return dependency
