from sqlalchemy.orm import Session

from app.models.service import Service, ServiceCreate
from app.utils.pagination_utils import Page, paginate


class ServiceRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_all(self, page: int, limit: int) -> Page[Service]:
        services = self.db.query(Service)
        return paginate(services, page, limit)

    def create(self, service_data: ServiceCreate) -> Service:
        service = Service(**service_data.model_dump())
        self.db.add(service)
        self.db.commit()
        self.db.refresh(service)
        return service
