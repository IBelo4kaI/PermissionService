from fastapi import APIRouter, Depends, Query

from app.database import DbSession
from app.middleware.auth_middleware import require_permission
from app.models.role import RoleAddPermission, RoleCreate
from app.models.permission import RoleDetailedResponse
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


@roles_router.get(
    "/service/{service_id}",
    summary="Получить список ролей по service_id",
    dependencies=[Depends(require_permission("roles", "read"))],
)
def get_roles_by_service_id(
    service_id: str,
    db: DbSession,
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
):
    service = RoleService(db)
    return service.get_all_by_service_id(service_id, page, limit)


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


@roles_router.post(
    "/create",
    summary="Создать роль",
    dependencies=[Depends(require_permission("roles", "create"))],
)
def create_role(role_data: RoleCreate, db: DbSession):
    service = RoleService(db)
    return service.create(role_data)


@roles_router.put(
    "/{role_id}",
    summary="Редактировать роль",
    dependencies=[Depends(require_permission("roles", "update"))],
)
def update_role(role_id: str, role_data: RoleCreate, db: DbSession):
    service = RoleService(db)
    return service.update(role_id, role_data)


@roles_router.get(
    "/{role_id}/detailed",
    summary="Получить подробную информацию о роли с разрешениями, сгруппированными по сервисам",
    response_model=RoleDetailedResponse,
    dependencies=[Depends(require_permission("roles", "read"))],
)
def get_role_detailed(role_id: str, db: DbSession):
    service = RoleService(db)
    return service.get_role_detailed(role_id)


@roles_router.delete(
    "/{role_id}",
    summary="Удалить роль",
    dependencies=[Depends(require_permission("roles", "delete"))],
)
def delete_role(role_id: str, db: DbSession):
    service = RoleService(db)
    return service.delete(role_id)
