from fastapi import APIRouter, Query
from starlette import status

from app.database import DbSession
from app.models.permission import PermissionCreate, PermissionResponse
from app.services.permission_service import PermissionService
from app.utils.pagination_utils import PageResponse

perm_router = APIRouter(prefix="/permissions", tags=["Permissions"])


@perm_router.get(
    "",
    response_model=PageResponse[PermissionResponse],
    status_code=status.HTTP_200_OK,
    summary="Получить список всех разрешений",
)
def get_permissions(
    db: DbSession,
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
):
    service = PermissionService(db)
    return service.get_all(page, limit)


@perm_router.get(
    "/{service_id}",
    response_model=list[PermissionResponse],
    status_code=status.HTTP_200_OK,
    summary="Получить список всех разрешений для сервиса",
)
def get_permissions_by_service_id(
    db: DbSession,
    service_id: str,
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
):
    service = PermissionService(db)
    return service.get_all_by_service_id(service_id, page, limit)


@perm_router.post(
    "/create",
    response_model=PermissionResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Создать разрешение",
)
def create_permission(permission_data: PermissionCreate, db: DbSession):
    service = PermissionService(db)
    return service.create(permission_data)
