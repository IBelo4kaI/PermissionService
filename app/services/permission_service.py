from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.permission import Permission, PermissionCreate, PermissionResponse
from app.repositories.permission_repository import PermissionRepository
from app.utils.pagination_utils import PageResponse


class PermissionService:
    def __init__(self, db: Session):
        self.repo = PermissionRepository(db)

    def get_all(self, page: int = 1, limit: int = 10) -> PageResponse[PermissionResponse]:
        page_data = self.repo.get_all(page, limit)

        return PageResponse(
            items=[PermissionResponse.model_validate(u) for u in page_data.items],
            total=page_data.total,
            page=page_data.page,
            limit=page_data.limit,
            pages=page_data.pages,
        )

    def get_by_id(self, id: str) -> Permission | None:
        permission = self.repo.get_by_id(id)
        return permission

    def get_by_code(self, code: str) -> Permission | None:
        permission = self.repo.get_by_code(code)
        return permission

    def get_all_by_service_id(
        self, service_id: str, page: int = 1, limit: int = 10
    ) -> list[PermissionResponse]:
        permissions = self.repo.get_by_service_id(page, limit, service_id)
        return [PermissionResponse.model_validate(perm) for perm in permissions]

    def get_by_user_id_and_service_id(
        self, user_id: str, service_id: str
    ) -> list[PermissionResponse]:
        permissions = self.repo.get_by_user_id_and_service_id(user_id, service_id)
        return [PermissionResponse.model_validate(perm) for perm in permissions]

    def create(self, permission_data: PermissionCreate) -> PermissionResponse:
        permission_exist = self.repo.get_by_code(permission_data.code)
        if permission_exist:
            raise HTTPException(
                status.HTTP_400_BAD_REQUEST, "Разрешение с таким кодом уже существует"
            )

        permission = self.repo.create(permission_data)
        return PermissionResponse.model_validate(permission)
