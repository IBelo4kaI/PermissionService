import hashlib
from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.models.session import SessionCreate, SessionDB


class SessionRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def get_by_token(self, token: str):
        current_time = datetime.now(timezone.utc)

        session = (
            self.db.query(SessionDB)
            .filter(
                SessionDB.token_hash == hashlib.sha256(token.encode()).hexdigest(),
                SessionDB.expires_at > current_time,
            )
            .first()
        )
        return session

    def create(self, session_data: SessionCreate) -> SessionDB:
        session = SessionDB(**session_data.model_dump())
        self.db.add(session)
        self.db.commit()
        self.db.refresh(session)
        return session
