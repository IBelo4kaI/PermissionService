from fastapi import FastAPI, Header, HTTPException
from sqlalchemy import create_engine, Column, String, DateTime, Integer, func
from sqlalchemy.dialects.mysql import CHAR
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv
import uuid

load_dotenv()

DATABASE_URL = f"mysql+pymysql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

class Service(Base):
    __tablename__ = "services"

    id = Column(CHAR(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(255))
    description = Column(String(500))
    image_url = Column(String(500))
    created_at = Column(DateTime)

class ApiKey(Base):
    __tablename__ = "api_keys"

    api_key = Column(String(255), primary_key=True)
    is_active = Column(Integer)

class Permission(Base):
    __tablename__ = "permissions"

    id = Column(Integer, primary_key=True)
    service_id = Column(CHAR(36))

app = FastAPI()

@app.get("/api/as/services", summary="Получить список сервисов")
def get_services(api_key: str = Header(..., alias="api-key")):
    db = SessionLocal()
    try:
        # Validate API key
        if not api_key.startswith("as_"):
            raise HTTPException(status_code=401, detail="API клюс должен начинаться с префикса 'as_'")

        key_record = db.query(ApiKey).filter(ApiKey.api_key == api_key, ApiKey.is_active == 1).first()
        if not key_record:
            raise HTTPException(status_code=401, detail="Недействительный или неактивный API ключ")

        services = db.query(Service).all()
        result = []
        for s in services:
            permissions_count = db.query(func.count(Permission.id)).filter(Permission.service_id == s.id).scalar()
            result.append({
                "id": s.id,
                "name": s.name,
                "description": s.description,
                "image_url": s.image_url,
                "created_at": s.created_at.strftime('%d.%m.%Y') if s.created_at else None,
                "permissions_count": permissions_count
            })
        return result
    finally:
        db.close()