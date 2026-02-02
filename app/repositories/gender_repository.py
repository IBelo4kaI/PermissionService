from sqlalchemy.orm import Session

from app.models.gender import Gender


class GenderRepositry:
    def __init__(self, db: Session) -> None:
        self.db = db

    def get_by_id(self, gender_id: int) -> Gender | None:
        gender = self.db.query(Gender).filter(Gender.id == gender_id).first()
        return gender

    def get_all(self) -> list[Gender]:
        genders = self.db.query(Gender).all()
        return genders
