from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.models.permission import Permission, PermissionCreate
from app.models.role import Role
from app.models.service import Service
from app.models.user import User
from app.utils.pagination_utils import Page, paginate


class PermissionRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_all(self, page: int, limit: int) -> Page[Permission]:
        permissions = self.db.query(Permission)
        return paginate(permissions, page, limit)

    def get_by_id(self, id: str) -> Permission | None:
        permission = self.db.query(Permission).filter(Permission.id == id).first()

        return permission

    def get_by_code(self, code: str) -> Permission | None:
        permission = self.db.query(Permission).filter(Permission.code == code).first()

        return permission

    def get_by_service_id(self, page: int, limit: int, service_id: str) -> list[Permission]:
        offset = (page - 1) * limit
        permissions = (
            self.db.query(Permission)
            .filter(Permission.service_id == service_id)
            .offset(offset)
            .limit(limit)
            .all()
        )

        return permissions

    def get_by_user_id(self, user_id: str) -> list[Permission]:
        permissions = (
            self.db.query(Permission)
            .join(Permission.roles)
            .join(Role.users)
            .filter(User.id == user_id)
            .distinct()
            .all()
        )
        return permissions

    def get_by_user_id_and_service_id(self, user_id: str, service_id: str) -> list[Permission]:
        """
        Возвращает все разрешения пользователя для конкретного сервиса.
        Учитывает wildcard разрешения типа "all:all:all", "api:all:all" и т.д.
        """
        # Получаем имя сервиса по его ID
        service = self.db.query(Service).filter(Service.id == service_id).first()
        if not service:
            return []

        service_name = service.name

        permissions = (
            self.db.query(Permission)
            .join(Permission.roles)
            .join(Role.users)
            .filter(User.id == user_id)
            .filter(
                or_(
                    # Разрешения, привязанные к текущему сервису
                    Permission.service_id == service_id,
                    # Wildcard разрешения, которые покрывают этот сервис
                    or_(
                        # Разрешения, начинающиеся с имени сервиса и двоеточия
                        Permission.code.startswith(f"{service_name}:"),
                        # Разрешения, начинающиеся с "all:"
                        Permission.code.startswith("all:"),
                    ),
                )
            )
            .distinct()
            .all()
        )

        return permissions

    def exist_by_user_id(self, user_id: str, service: str, entity: str, action: str) -> bool:
        """
        Проверяет наличие разрешения у пользователя.

        Формат кода разрешения: "service:entity:permission"
        Поддерживается wildcard "all" для каждого сегмента.

        Args:
            user_id: ID пользователя
            service: Сервис (например, "api")
            entity: Сущность (например, "users")
            perm: Разрешение (например, "read")

        Returns:
            True если у пользователя есть соответствующее разрешение
        """

        # Формируем возможные паттерны разрешений
        # Например, для "api:users:read" проверяем:
        # - api:users:read (точное совпадение)
        # - api:users:all (все действия над users в api)
        # - api:all:read (read для всех сущностей в api)
        # - api:all:all (все действия во всех сущностях api)
        # - all:users:read (read users во всех сервисах)
        # - all:all:read (read везде)
        # - all:users:all (все действия над users везде)
        # - all:all:all (полный доступ)

        permission_patterns = [
            f"{service}:{entity}:{action}",
            f"{service}:{entity}:all",
            f"{service}:all:{action}",
            f"{service}:all:all",
            f"all:{entity}:{action}",
            f"all:{entity}:all",
            f"all:all:{action}",
            "all:all:all",
        ]

        exists = (
            self.db.query(Permission.id)
            .join(Permission.roles)
            .join(Role.users)
            .filter(User.id == user_id)
            .filter(Permission.code.in_(permission_patterns))
            .limit(1)
            .scalar()
        ) is not None

        return exists

    def create(self, permission_data: PermissionCreate) -> Permission:
        permission = Permission(**permission_data.model_dump())
        self.db.add(permission)
        self.db.commit()
        self.db.refresh(permission)
        permission.service_name = permission.service.name
        return permission

    def update(self, permission_id: str, permission_data: PermissionCreate) -> Permission | None:
        permission = self.db.query(Permission).filter(Permission.id == permission_id).first()
        if permission:
            for field, value in permission_data.model_dump().items():
                setattr(permission, field, value)
            self.db.commit()
            self.db.refresh(permission)
        return permission

    def delete(self, permission_id: str) -> Permission | None:
        permission = self.db.query(Permission).filter(Permission.id == permission_id).first()
        if permission:
            self.db.delete(permission)
            self.db.commit()
        return permission
