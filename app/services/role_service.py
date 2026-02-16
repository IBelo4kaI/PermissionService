from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models import RoleResponse
from app.models.role import RoleAddPermission, RoleCreate
from app.repositories.permission_repository import PermissionRepository
from app.repositories.role_repository import RoleRepository
from app.utils.pagination_utils import PageResponse


class RoleService:
    def __init__(self, db: Session) -> None:
        self.repo = RoleRepository(db)
        self.perm_repo = PermissionRepository(db)

    def get_all(self, page: int, limit: int) -> PageResponse[RoleResponse]:
        from pydantic import BaseModel
        page_data = self.repo.get_all_with_counts(page, limit)

        items = []
        for item in page_data.items:
            # Извлекаем роль и количество пользователей и разрешений из результата запроса
            if hasattr(item, 'Role'):
                role_data = item.Role
                user_count = item.user_count
                permission_count = item.permission_count
            else:
                # Если результат не содержит подсчеты, то это обычная роль
                role_data = item
                user_count = 0
                permission_count = 0
            
            # Подготовим словарь атрибутов роли
            role_dict = {}
            for column in role_data.__table__.columns:
                role_dict[column.name] = getattr(role_data, column.name)
            
            # Добавим поля, которые не являются колонками, но нужны для Pydantic модели
            role_dict['permissions'] = []  # добавляем пустой список для permissions
            role_dict['user_count'] = user_count  # добавляем user_count
            role_dict['permissions_count'] = permission_count  # добавляем permissions_count
            
            # Создаем RoleResponse из словаря
            role_response = RoleResponse.model_validate(role_dict)
            items.append(role_response)

        return PageResponse(
            items=items,
            total=page_data.total,
            page=page_data.page,
            limit=page_data.limit,
            pages=page_data.pages,
        )

    def get_all_by_service_id(
        self, service_id: str, page: int, limit: int
    ) -> PageResponse[RoleResponse]:
        page_data = self.repo.get_all_with_counts_by_service_id(page, limit, service_id)

        items = []
        for item in page_data.items:
            if hasattr(item, 'Role'):
                role_data = item.Role
                user_count = item.user_count
                permission_count = item.permission_count
            else:
                role_data = item
                user_count = 0
                permission_count = 0

            role_dict = {}
            for column in role_data.__table__.columns:
                role_dict[column.name] = getattr(role_data, column.name)

            role_dict['permissions'] = []
            role_dict['user_count'] = user_count
            role_dict['permissions_count'] = permission_count

            role_response = RoleResponse.model_validate(role_dict)
            items.append(role_response)

        return PageResponse(
            items=items,
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

        if perm not in role.permissions:
            raise HTTPException(status_code=400, detail="Роль не имеет это разрешение")

        role = self.repo.permission_remove(role, perm)
        return RoleResponse.model_validate(role)

    def create(self, role_data):
        """Создает новую роль"""
        role = self.repo.create(role_data)
        return RoleResponse.model_validate(role)

    def update(self, role_id: str, role_data):
        """Обновляет роль по ID"""
        role = self.repo.update(role_id, role_data)
        if not role:
            raise HTTPException(status_code=404, detail="Роль не найдена")
        return RoleResponse.model_validate(role)

    def delete(self, role_id: str):
        """Удаляет роль по ID"""
        role = self.repo.delete(role_id)
        if not role:
            raise HTTPException(status_code=404, detail="Роль не найдена")
        return {"message": "Роль успешно удалена"}

    def get_role_detailed(self, role_id: str):
        """Получает подробную информацию о роли с разрешениями, сгруппированными по сервисам"""
        from datetime import datetime
        from app.models.permission import PermissionWithUse, RoleDetailedResponse, UserRoleInfo
        
        # Получаем роль и всю информацию о разрешениях
        role_info = self.repo.get_role_with_all_permissions_info(role_id)
        if not role_info:
            raise HTTPException(status_code=404, detail="Роль не найдена")
        
        role = role_info['role']
        all_permissions = role_info['all_permissions']
        used_permission_ids = role_info['used_permission_ids']
        users_with_role = role_info.get('users_with_role', [])
        
        # Форматируем дату создания роли
        formatted_created_at = role.created_at.strftime("%d.%m.%Y %H:%M") if role.created_at else ""
        
        # Группируем разрешения по service_id
        permissions_by_service = {}
        
        # Подсчитываем количество используемых разрешений
        used_permissions_count = 0
        
        for perm in all_permissions:
            # Форматируем дату создания разрешения
            formatted_perm_created_at = perm.created_at.strftime("%d.%m.%Y %H:%M") if perm.created_at else ""
            
            # Определяем, используется ли разрешение в этой роли
            is_used = perm.id in used_permission_ids
            
            if is_used:
                used_permissions_count += 1
            
            # Получаем название сервиса
            service_name = perm.service.name if perm.service else None
            
            # Создаем объект PermissionWithUse
            perm_with_use = PermissionWithUse(
                id=perm.id,
                service_id=perm.service_id,
                code=perm.code,
                name=perm.name,
                description=perm.description,
                created_at=formatted_perm_created_at,
                service_name=service_name,
                use=is_used
            )
            
            # Используем специальный ключ для случая, когда service_id равен None
            service_key = perm.service_id if perm.service_id is not None else "global"
            
            # Добавляем в группу по service_id
            if service_key not in permissions_by_service:
                permissions_by_service[service_key] = []
            
            permissions_by_service[service_key].append(perm_with_use)
        
        # Создаем информацию о пользователях
        users_info = [
            UserRoleInfo(
                id=user.id,
                name=getattr(user, 'name', ''),
                surname=getattr(user, 'surname', ''),
                username=getattr(user, 'username', '')
            )
            for user in users_with_role
        ]
        
        # Создаем и возвращаем объект ответа
        return RoleDetailedResponse(
            id=role.id,
            name=role.name,
            description=role.description,
            is_global=role.is_global,
            created_at=formatted_created_at,
            used_permissions_count=used_permissions_count,
            permissions_by_service=permissions_by_service,
            users=users_info
        )
