from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models import ServiceCreate, ServiceResponse
from app.models.service import ServiceAccessResponse
from app.repositories.service_repository import ServiceRepository
from app.utils.pagination_utils import PageResponse


class ServiceService:
    def __init__(self, db: Session) -> None:
        self.repo = ServiceRepository(db)

    def get_all(self, page: int = 1, limit: int = 10) -> PageResponse[ServiceResponse]:
        page_data = self.repo.get_all(page, limit)

        return PageResponse(
            items=[ServiceResponse.model_validate(u) for u in page_data.items],
            total=page_data.total,
            page=page_data.page,
            limit=page_data.limit,
            pages=page_data.pages,
        )

    def create(self, service_date: ServiceCreate) -> ServiceResponse:
        service = self.repo.create(service_date)
        return ServiceResponse.model_validate(service)

    def update(self, service_id: str, service_data: ServiceCreate) -> ServiceResponse:
        service = self.repo.update(service_id, service_data)
        if not service:
            raise HTTPException(status_code=404, detail="Сервис не найден")
        return ServiceResponse.model_validate(service)

    def get_services_by_user_roles(self, user_id: str):
        services = self.repo.get_services_by_user_roles(user_id)
        return [ServiceAccessResponse.model_validate(service) for service in services]
