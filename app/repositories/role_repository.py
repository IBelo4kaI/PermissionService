from sqlalchemy.orm import Session

from app.models.permission import Permission
from app.models.role import Role
from app.utils.pagination_utils import Page, paginate


class RoleRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def get_all_with_counts(self, page: int, limit: int):
        """Получает страницу ролей с количеством пользователей и разрешений для каждой роли"""
        from sqlalchemy import func
        from app.models.user_roles import UserRole
        from app.models.role import RolePermission
        
        # Запрос для получения ролей с количеством пользователей и разрешений
        # Используем подзапросы, чтобы избежать неправильного подсчета из-за декартова произведения
        from sqlalchemy.orm import aliased
        
        # Подзапрос для подсчета пользователей
        user_counts = (
            self.db.query(
                UserRole.role_id,
                func.count(UserRole.user_id).label('user_count')
            )
            .group_by(UserRole.role_id)
            .subquery()
        )
        
        # Подзапрос для подсчета разрешений
        perm_counts = (
            self.db.query(
                RolePermission.role_id,
                func.count(RolePermission.permission_id).label('permission_count')
            )
            .group_by(RolePermission.role_id)
            .subquery()
        )
        
        # Основной запрос с подзапросами
        query = (
            self.db.query(
                Role,
                func.coalesce(user_counts.c.user_count, 0).label('user_count'),
                func.coalesce(perm_counts.c.permission_count, 0).label('permission_count')
            )
            .select_from(Role)
            .outerjoin(user_counts, Role.id == user_counts.c.role_id)
            .outerjoin(perm_counts, Role.id == perm_counts.c.role_id)
        )
        
        return paginate(query, page, limit)

    def get_all_with_counts_by_service_id(self, page: int, limit: int, service_id: str):
        """Получает страницу ролей по service_id с количеством пользователей и разрешений"""
        from sqlalchemy import func
        from app.models.user_roles import UserRole
        from app.models.role import RolePermission

        user_counts = (
            self.db.query(
                UserRole.role_id,
                func.count(UserRole.user_id).label('user_count')
            )
            .group_by(UserRole.role_id)
            .subquery()
        )

        perm_counts = (
            self.db.query(
                RolePermission.role_id,
                func.count(RolePermission.permission_id).label('permission_count')
            )
            .group_by(RolePermission.role_id)
            .subquery()
        )

        query = (
            self.db.query(
                Role,
                func.coalesce(user_counts.c.user_count, 0).label('user_count'),
                func.coalesce(perm_counts.c.permission_count, 0).label('permission_count')
            )
            .select_from(Role)
            .outerjoin(user_counts, Role.id == user_counts.c.role_id)
            .outerjoin(perm_counts, Role.id == perm_counts.c.role_id)
            .filter(Role.service_id == service_id)
        )

        return paginate(query, page, limit)
    
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

    def create(self, role_data):
        """Создает новую роль"""
        from app.models.role import Role, RoleCreate
        role = Role(**role_data.model_dump())
        self.db.add(role)
        self.db.commit()
        self.db.refresh(role)
        return role

    def update(self, role_id: str, role_data):
        """Обновляет роль по ID"""
        from app.models.role import Role, RoleCreate
        role = self.db.query(Role).filter(Role.id == role_id).first()
        if role:
            for field, value in role_data.model_dump().items():
                setattr(role, field, value)
            self.db.commit()
            self.db.refresh(role)
        return role

    def get_role_with_permissions(self, role_id: str):
        """Получает роль с разрешениями, сгруппированными по сервисам"""
        from sqlalchemy.orm import joinedload
        from app.models.role import Role
        from app.models.permission import Permission
        
        # Получаем роль с предзагрузкой связанных разрешений и сервисов
        role = (
            self.db.query(Role)
            .options(joinedload(Role.permissions).joinedload(Permission.service))
            .filter(Role.id == role_id)
            .first()
        )
        
        return role

    def get_role_with_all_permissions_info(self, role_id: str):
        """Получает роль и всю информацию о разрешениях (все разрешения и какие используются в роли)"""
        from sqlalchemy.orm import joinedload
        from app.models.role import Role
        from app.models.permission import Permission
        from app.models.role import RolePermission
        
        # Получаем роль
        role = self.db.query(Role).filter(Role.id == role_id).first()
        
        if not role:
            return None
        
        # Если у роли service_id не NULL, то получаем все разрешения для этого сервиса
        # Если у роли service_id NULL (глобальная роль), то получаем все разрешения
        if role.service_id:
            # Для роли с конкретным сервисом получаем все разрешения для этого сервиса
            all_perms_for_service = (
                self.db.query(Permission)
                .options(joinedload(Permission.service))
                .filter(Permission.service_id == role.service_id)
                .all()
            )
        else:
            # Для глобальной роли получаем все разрешения
            all_perms_for_service = (
                self.db.query(Permission)
                .options(joinedload(Permission.service))
                .all()
            )
        
        # Получаем ID разрешений, которые используются в данной роли
        used_permission_ids = (
            self.db.query(RolePermission.permission_id)
            .filter(RolePermission.role_id == role_id)
            .all()
        )
        used_permission_ids = {item[0] for item in used_permission_ids}
        
        from sqlalchemy.orm import joinedload
        from app.models.user import User
        from app.models.user_roles import UserRole
        
        # Получаем пользователей, имеющих эту роль
        users_with_role = (
            self.db.query(User)
            .join(UserRole)
            .filter(UserRole.role_id == role_id)
            .all()
        )
        
        return {
            'role': role,
            'all_permissions': all_perms_for_service,
            'used_permission_ids': used_permission_ids,
            'users_with_role': users_with_role
        }

    def permission_remove(self, role: Role, perm_data: Permission):
        role.permissions.remove(perm_data)
        self.db.commit()
        self.db.refresh(role)
        return role

    def delete(self, role_id: str):
        """Удаляет роль по ID"""
        role = self.db.query(Role).filter(Role.id == role_id).first()
        if role:
            self.db.delete(role)
            self.db.commit()
        return role
