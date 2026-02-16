from sqlalchemy.orm import Session

from app.models.role import Role
from app.models.session import SessionDB
from app.models.user import User, UserCreate
from app.utils.pagination_utils import Page, paginate


class UserRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def get_all(self, page: int, limit: int) -> Page[User]:
        users = self.db.query(User)
        return paginate(users, page, limit)

    def get_all_without_pages(self) -> list[User]:
        users = self.db.query(User)
        return users.all()

    def get_by_id(self, user_id: str) -> User | None:
        user = self.db.query(User).filter(User.id == user_id).first()
        return user

    def get_by_username(self, username: str) -> User | None:
        user = self.db.query(User).filter(User.username == username).first()
        return user

    def get_by_service_id(self, page: int, limit: int, service_id: str) -> Page[User]:
        from app.models.role import Role

        users = (
            self.db.query(User)
            .join(User.roles)
            .filter(Role.service_id == service_id)
            .distinct()
        )
        return paginate(users, page, limit)

    def create(self, user_data: UserCreate) -> User:
        user = User(**user_data.model_dump())
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user

    def delete(self, user_id: str):
        """Удаляет пользователя по ID"""
        user = self.db.query(User).filter(User.id == user_id).first()
        if user:
            # Сначала удаляем сессии пользователя, иначе FK (sessions.user_id -> users.id) блокирует удаление.
            self.db.query(SessionDB).filter(SessionDB.user_id == user_id).delete(
                synchronize_session=False
            )
            self.db.delete(user)
            self.db.commit()
        return user

    def update(self, user_id: str, user_data):
        """Обновляет пользователя по ID"""
        user = self.db.query(User).filter(User.id == user_id).first()
        if user:
            for field, value in user_data.model_dump(exclude_unset=True).items():
                setattr(user, field, value)
            self.db.commit()
            self.db.refresh(user)
        return user

    def role_add(self, user: User, role_data: Role):
        user.roles.append(role_data)
        self.db.commit()
        self.db.refresh(user)
        return user

    def role_remove(self, user: User, role_data: Role):
        user.roles.remove(role_data)
        self.db.commit()
        self.db.refresh(user)
        return user
