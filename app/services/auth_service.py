from datetime import datetime, timedelta, timezone

from fastapi import HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.database import DbSession
from app.models.session import SessionCreate
from app.repositories.session_repository import SessionRepository
from app.repositories.user_repository import UserRepository
from app.utils.password_utils import verify_password
from app.utils.token_utils import create_hash, generate_token


class Login(BaseModel):
    login: str
    password: str


class AuthService:
    def __init__(self, db: Session) -> None:
        self.repo_session = SessionRepository(db)
        self.repo_user = UserRepository(db)

    def login(
        self,
        login: Login,
    ):
        user = self.repo_user.get_by_username(login.login)
        if not user:
            raise HTTPException(404, detail="Неверный логин или пароль")

        if not verify_password(str(user.password), login.password):
            raise HTTPException(404, detail="Неверный логин или пароль")

        token = generate_token()
        token_hash = create_hash(token)
        expires_at = datetime.now(timezone.utc) + timedelta(hours=3)

        session_create = SessionCreate(
            user_id=str(user.id), token_hash=token_hash, expires_at=expires_at
        )

        self.repo_session.create(session_create)

        return (token, expires_at)
