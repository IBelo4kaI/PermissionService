from fastapi import APIRouter, Depends, Query, status

from app.database import DbSession
from app.middleware.auth_middleware import get_session, require_permission
from app.models.session import SessionDB
from app.models.user import UserAddRole, UserCreate, UserResponse, UserUpdate
from app.services.permission_service import PermissionService
from app.services.user_service import UserService

user_router = APIRouter(prefix="/users", tags=["Users"])


@user_router.get(
    "",
    status_code=status.HTTP_200_OK,
    summary="Получить список пользователей",
    dependencies=[Depends(require_permission("users", "read_all"))],
)
def get(
    db: DbSession,
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
):
    service = UserService(db)
    return service.get_all(page, limit)


@user_router.get(
    "/all",
    status_code=status.HTTP_200_OK,
    summary="Получить список пользователей без пагинации",
    dependencies=[Depends(require_permission("users", "read_all"))],
)
def getWithoutLimits(
    db: DbSession,
):
    service = UserService(db)
    return service.get_all_without_limits()


@user_router.get(
    "/me",
    status_code=status.HTTP_200_OK,
    summary="Получить пользователя по id",
    dependencies=[],
)
def get_me(db: DbSession, session: SessionDB = Depends(get_session)):
    service = UserService(db)
    return service.get_by_id(str(session.user_id))


@user_router.get(
    "/me/permissions/{service_id}",
    status_code=status.HTTP_200_OK,
    summary="Получить список разрешений пользователя",
    dependencies=[],
)
def get_me_permissions(service_id: str, db: DbSession, session: SessionDB = Depends(get_session)):
    service = PermissionService(db)
    return service.get_by_user_id_and_service_id(str(session.user_id), service_id)


@user_router.get(
    "/{user_id}",
    status_code=status.HTTP_200_OK,
    summary="Получить пользователя по id",
    dependencies=[Depends(require_permission("users", "read"))],
)
def get_by_id(user_id: str, db: DbSession):
    service = UserService(db)
    return service.get_by_id(user_id)


@user_router.put(
    "/{user_id}",
    summary="Обновить пользователя",
    response_model=UserResponse,
    dependencies=[Depends(require_permission("users", "update"))],
)
def update_user(user_id: str, user_data: UserUpdate, db: DbSession):
    service = UserService(db)
    return service.update(user_id, user_data)


@user_router.delete(
    "/{user_id}",
    summary="Удалить пользователя",
    dependencies=[Depends(require_permission("users", "delete"))],
)
def delete_user(user_id: str, db: DbSession):
    service = UserService(db)
    return service.delete(user_id)


@user_router.post(
    "/create",
    summary="Создать пользователя",
    response_model=UserResponse,
    dependencies=[Depends(require_permission("users", "create"))],
)
def create(user_data: UserCreate, db: DbSession):
    service = UserService(db)
    return service.create(user_data)


@user_router.post(
    "/roles/add",
    summary="Добавить роль пользователю",
    dependencies=[Depends(require_permission("users.roles", "edit"))],
)
def role_add(user_add_data: UserAddRole, db: DbSession):
    service = UserService(db)
    return service.role_add(user_add_data)


@user_router.post(
    "/roles/remove",
    summary="Удалить роль у пользователя",
    dependencies=[Depends(require_permission("users.roles", "edit"))],
)
def role_remove(user_remove_data: UserAddRole, db: DbSession):
    service = UserService(db)
    return service.role_remove(user_remove_data)
