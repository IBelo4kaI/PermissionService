from fastapi import APIRouter, Response

from app.database import DbSession
from app.services.auth_service import AuthService, Login
from app.services.role_service import RoleService

auth_router = APIRouter(prefix="/auth", tags=["Auth"])


@auth_router.post("/login", summary="Аунтентификация пользователя")
def login(
    login: Login,
    response: Response,
    db: DbSession,
):
    service = AuthService(db)
    result = service.login(login)
    response.set_cookie("session", result[0], expires=result[1], httponly=True)
