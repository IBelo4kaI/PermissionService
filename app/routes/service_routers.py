from fastapi import APIRouter, Depends, Query, status

from app.database import DbSession
from app.middleware.auth_middleware import get_session, require_permission
from app.models.service import ServiceAccessResponse, ServiceCreate, ServiceResponse
from app.services.service_service import ServiceService
from app.utils.pagination_utils import PageResponse

service_router = APIRouter(prefix="/services", tags=["Services"])


@service_router.get(
    "",
    response_model=PageResponse[ServiceResponse],
    status_code=status.HTTP_200_OK,
    summary="Получить список сервисов",
    dependencies=[Depends(require_permission("services", "read_all"))],
)
def get_all(
    db: DbSession,
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
):
    service = ServiceService(db)
    return service.get_all(page, limit)


@service_router.post(
    "/create",
    summary="Создать сервис",
    response_model=ServiceResponse,
    dependencies=[Depends(require_permission("services", "create"))],
)
def create(service_data: ServiceCreate, db: DbSession):
    service = ServiceService(db)
    return service.create(service_data)


@service_router.put(
    "/{service_id}",
    summary="Редактировать сервис",
    response_model=ServiceResponse,
    dependencies=[Depends(require_permission("services", "update"))],
)
def update(service_id: str, service_data: ServiceCreate, db: DbSession):
    service = ServiceService(db)
    return service.update(service_id, service_data)


@service_router.get(
    "/user-accessible",
    response_model=list[ServiceAccessResponse],
    summary="Получить список сервисов, доступных пользователю по его ролям",
)
def get_user_accessible_services(
    db: DbSession,
    session=Depends(get_session)
):
    service = ServiceService(db)
    user_id = str(session.user_id)
    return service.get_services_by_user_roles(user_id)
