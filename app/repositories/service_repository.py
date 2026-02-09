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

    def update(self, service_id: str, service_data: ServiceCreate) -> Service | None:
        service = self.db.query(Service).filter(Service.id == service_id).first()
        if service:
            for field, value in service_data.model_dump().items():
                setattr(service, field, value)
            self.db.commit()
            self.db.refresh(service)
        return service

    def get_services_by_user_roles(self, user_id: str):
        from app.models.user import User
        from app.models.role import Role
        from sqlalchemy import and_, or_
        
        user_roles = (
            self.db.query(Role)
            .join(Role.users)
            .filter(User.id == user_id)
            .subquery()
        )
        
        services_query = self.db.query(Service).join(
            user_roles,
            or_(
                user_roles.c.service_id == Service.id,
                user_roles.c.service_id.is_(None)
            )
        ).distinct()
        
        return services_query.all()
