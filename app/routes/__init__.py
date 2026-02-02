from fastapi import APIRouter

from app.routes.auth_routes import auth_router
from app.routes.permission_routes import perm_router
from app.routes.role_routes import roles_router
from app.routes.service_routers import service_router
from app.routes.user_routes import user_router

main_router = APIRouter(prefix="/api/as")

main_router.include_router(auth_router)
main_router.include_router(perm_router)
main_router.include_router(service_router)
main_router.include_router(roles_router)
main_router.include_router(user_router)
