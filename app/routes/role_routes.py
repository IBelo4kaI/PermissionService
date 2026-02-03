from fastapi import APIRouter, Depends, Query

from app.database import DbSession
from app.middleware.auth_middleware import require_permission
from app.models.role import RoleAddPermission
from app.services.role_service import RoleService

roles_router = APIRouter(prefix="/roles", tags=["Roles"])


@roles_router.get(
    "",
    summary="Получить список ролей",
    dependencies=[Depends(require_permission("roles", "read"))],
)
def get_roles(
    db: DbSession,
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
):
    service = RoleService(db)
    return service.get_all(page, limit)


@roles_router.post(
    "/perm/add",
    summary="Добавить разрешение для роли",
    dependencies=[Depends(require_permission("roles.perm", "edit"))],
)
def role_add(perm_add_data: RoleAddPermission, db: DbSession):
    service = RoleService(db)
    return service.permission_add(perm_add_data)


@roles_router.post(
    "/perm/remove",
    summary="Удалить разрешение у роли",
    dependencies=[Depends(require_permission("roles.perm", "edit"))],
)
def role_remove(perm_add_data: RoleAddPermission, db: DbSession):
    service = RoleService(db)
    return service.permission_remove(perm_add_data)
