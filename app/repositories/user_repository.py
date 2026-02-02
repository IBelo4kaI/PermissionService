from sqlalchemy.orm import Session

from app.models.role import Role
from app.models.user import User, UserCreate
from app.utils.pagination_utils import Page, paginate


class UserRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def get_all(self, page: int, limit: int) -> Page[User]:
        users = self.db.query(User)
        return paginate(users, page, limit)

    def get_by_id(self, user_id: str) -> User | None:
        user = self.db.query(User).filter(User.id == user_id).first()
        return user

    def get_by_username(self, username: str) -> User | None:
        user = self.db.query(User).filter(User.username == username).first()
        return user

    def create(self, user_data: UserCreate) -> User:
        user = User(**user_data.model_dump())
        self.db.add(user)
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
