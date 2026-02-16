from fastapi import APIRouter, Cookie, Response

from app.database import DbSession
from app.services.auth_service import AuthService, Login

auth_router = APIRouter(prefix="/auth", tags=["Auth"])


@auth_router.post("/login", summary="Аунтентификация пользователя")
def login(
    login: Login,
    response: Response,
    db: DbSession,
):
    service = AuthService(db)
    result = service.login(login)
    # Делает cookie доступной для всех поддоменов *.st29.ru и для основного домена.
    response.set_cookie(
        "session",
        result[0],
        expires=result[1],
        httponly=True,
        domain=".st29.ru",
        path="/",
    )


@auth_router.post("/validate-session", summary="Проверить действительность сессии")
def validate_session(
    db: DbSession, session_token: str | None = Cookie(default=None, alias="session")
):
    if session_token is None:
        return {"valid": False}

    service = AuthService(db)
    is_valid = service.validate_session(session_token)

    return {"valid": is_valid}
