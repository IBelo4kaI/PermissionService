from sqlalchemy.orm import Session

from app.models.permission import Permission
from app.models.role import Role
from app.utils.pagination_utils import Page, paginate


class RoleRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def get_all(self, page: int, limit: int) -> Page[Role]:
        roles = self.db.query(Role)
        return paginate(roles, page, limit)

    def get_by_id(self, role_id: str) -> Role | None:
        role = self.db.query(Role).filter(Role.id == role_id).first()
        return role

    def permission_add(self, role: Role, perm_data: Permission):
        role.permissions.append(perm_data)
        self.db.commit()
        self.db.refresh(role)
        return role

    def permission_remove(self, role: Role, perm_data: Permission):
        role.permissions.remove(perm_data)
        self.db.commit()
        self.db.refresh(role)
        return role
