from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.user import UserAddRole, UserCreate, UserResponse
from app.repositories.gender_repository import GenderRepositry
from app.repositories.role_repository import RoleRepository
from app.repositories.user_repository import UserRepository
from app.utils.pagination_utils import PageResponse
from app.utils.password_utils import hash_password


class UserService:
    def __init__(self, db: Session) -> None:
        self.repo = UserRepository(db)
        self.gender_repo = GenderRepositry(db)
        self.role_repo = RoleRepository(db)

    def get_all(self, page: int = 1, limit: int = 10) -> PageResponse[UserResponse]:
        page_data = self.repo.get_all(page, limit)

        return PageResponse(
            items=[UserResponse.model_validate(u) for u in page_data.items],
            total=page_data.total,
            page=page_data.page,
            limit=page_data.limit,
            pages=page_data.pages,
        )

    def get_by_id(self, user_id: str) -> UserResponse:
        user = self.repo.get_by_id(user_id)
        return UserResponse.model_validate(user)

    def create(self, user_data: UserCreate) -> UserResponse:
        gender_exist = self.gender_repo.get_by_id(user_data.gender_id)
        if not gender_exist:
            raise HTTPException(
                status.HTTP_400_BAD_REQUEST, "Не существующий идентитификатор Gender"
            )

        user_exist = self.repo.get_by_username(user_data.username)
        if user_exist:
            raise HTTPException(
                status.HTTP_400_BAD_REQUEST, "Пользователь с такой почтой уже сушествует"
            )

        user_data.password = hash_password(user_data.password)

        user = self.repo.create(user_data)
        return UserResponse.model_validate(user)

    def role_add(self, user_add_data: UserAddRole):
        user = self.repo.get_by_id(user_add_data.user_id)
        if not user:
            raise HTTPException(status_code=404, detail="Пользователь не найден")

        role = self.role_repo.get_by_id(user_add_data.role_id)
        if not role:
            raise HTTPException(status_code=404, detail="Роль не найдена")

        if role in user.roles:
            raise HTTPException(status_code=400, detail="Пользователь уже имеет эту роль")

        user = self.repo.role_add(user, role)
        return UserResponse.model_validate(user)

    def role_remove(self, user_remove_data: UserAddRole):
        user = self.repo.get_by_id(user_remove_data.user_id)
        if not user:
            raise HTTPException(status_code=404, detail="Пользователь не найден")

        role = self.role_repo.get_by_id(user_remove_data.role_id)
        if not role:
            raise HTTPException(status_code=404, detail="Роль не найдена")

        if role not in user.roles:
            raise HTTPException(status_code=400, detail="Пользователь не имеет этой роли")

        user = self.repo.role_remove(user, role)
        return UserResponse.model_validate(user)
