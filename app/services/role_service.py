from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models import RoleResponse
from app.models.role import RoleAddPermission
from app.repositories.permission_repository import PermissionRepository
from app.repositories.role_repository import RoleRepository
from app.utils.pagination_utils import PageResponse


class RoleService:
    def __init__(self, db: Session) -> None:
        self.repo = RoleRepository(db)
        self.perm_repo = PermissionRepository(db)

    def get_all(self, page: int, limit: int) -> PageResponse[RoleResponse]:
        page_data = self.repo.get_all(page, limit)

        return PageResponse(
            items=[RoleResponse.model_validate(u) for u in page_data.items],
            total=page_data.total,
            page=page_data.page,
            limit=page_data.limit,
            pages=page_data.pages,
        )

    def permission_add(self, permission_add_data: RoleAddPermission):
        role = self.repo.get_by_id(permission_add_data.role_id)
        if not role:
            raise HTTPException(status_code=404, detail="Роль не найдена")

        perm = self.perm_repo.get_by_id(permission_add_data.perm_id)
        if not perm:
            raise HTTPException(status_code=404, detail="Роль не найдена")

        if perm in role.permissions:
            raise HTTPException(status_code=400, detail="Роль уже имеет это разрешение")

        role = self.repo.permission_add(role, perm)
        return RoleResponse.model_validate(role)

    def permission_remove(self, permission_add_data: RoleAddPermission):
        role = self.repo.get_by_id(permission_add_data.role_id)
        if not role:
            raise HTTPException(status_code=404, detail="Роль не найдена")

        perm = self.perm_repo.get_by_id(permission_add_data.perm_id)
        if not perm:
            raise HTTPException(status_code=404, detail="Разрешение не найдено")

        if perm in role.permissions:
            raise HTTPException(status_code=400, detail="Роль не имеет это разрешение")

        role = self.repo.permission_remove(role, perm)
        return RoleResponse.model_validate(role)
