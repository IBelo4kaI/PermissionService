from fastapi import FastAPI, Header, HTTPException, Query
from sqlalchemy import create_engine, Column, String, DateTime, Integer, func
from sqlalchemy.dialects.mysql import CHAR
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from pydantic import BaseModel
from typing import Optional
import os
from dotenv import load_dotenv
import uuid
from datetime import datetime

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
    prefix = Column(String(5))
    created_at = Column(DateTime, default=datetime.utcnow)

class ApiKey(Base):
    __tablename__ = "api_keys"

    api_key = Column(String(255), primary_key=True)
    is_active = Column(Integer)

class Permission(Base):
    __tablename__ = "permissions"

    id = Column(CHAR(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    service_id = Column(CHAR(36))
    code = Column(String(255))
    name = Column(String(255))
    description = Column(String(500))
    created_at = Column(DateTime, default=datetime.utcnow)

class Gender(Base):
    __tablename__ = "genders"

    id = Column(Integer, primary_key=True)
    name = Column(String(50))

class Role(Base):
    __tablename__ = "roles"

    id = Column(Integer, primary_key=True)
    name = Column(String(100))

class UserRole(Base):
    __tablename__ = "user_roles"

    id = Column(Integer, primary_key=True)
    user_id = Column(CHAR(36))
    role_id = Column(Integer)

class User(Base):
    __tablename__ = "users"

    id = Column(CHAR(36), primary_key=True)
    name = Column(String(100))
    surname = Column(String(100))
    patronymic = Column(String(100))
    username = Column(String(100))
    gender_id = Column(Integer)
    birthday = Column(DateTime)
    status = Column(String(50))

class ServiceCreate(BaseModel):
    name: str
    description: str
    prefix: str

class ServiceResponse(BaseModel):
    id: str
    name: str
    description: str
    prefix: str
    image_url: Optional[str]
    created_at: str
    permissions_count: int

class PermissionCreate(BaseModel):
    service_id: str
    code: str
    name: str
    description: str

class PermissionResponse(BaseModel):
    id: str
    service_id: str
    service_name: str
    code: str
    name: str
    description: str
    created_at: str

class UserResponse(BaseModel):
    id: str
    name: str
    surname: str
    patronymic: str
    username: str
    gender: str
    birthday: str
    status: str
    roles: list[str]
    roles_count: int

app = FastAPI()

@app.get("/api/as/services", summary="Получить список сервисов")
def get_services(api_key: str = Header(..., alias="api-key")):
    db = SessionLocal()
    try:
        if not api_key.startswith("as_"):
            raise HTTPException(status_code=401, detail="API ключ должен начинаться с префикса 'as_'")

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
                "prefix": s.prefix,
                "image_url": s.image_url,
                "created_at": s.created_at.strftime('%d.%m.%Y') if s.created_at else None,
                "permissions_count": permissions_count
            })
        return result
    finally:
        db.close()

@app.post("/api/as/permissions/create", summary="Создать разрешение", response_model=PermissionResponse)
def create_permission(permission: PermissionCreate, api_key: str = Header(..., alias="api-key")):
    db = SessionLocal()
    try:
        if not api_key.startswith("as_"):
            raise HTTPException(status_code=401, detail="API ключ должен начинаться с префикса 'as_'")

        key_record = db.query(ApiKey).filter(ApiKey.api_key == api_key, ApiKey.is_active == 1).first()
        if not key_record:
            raise HTTPException(status_code=401, detail="Недействительный или неактивный API ключ")

        # Check if service exists
        service = db.query(Service).filter(Service.id == permission.service_id).first()
        if not service:
            raise HTTPException(status_code=404, detail="Сервис не найден")

        new_permission = Permission(
            service_id=permission.service_id,
            code=permission.code,
            name=permission.name,
            description=permission.description
        )
        db.add(new_permission)
        db.commit()
        db.refresh(new_permission)

        return PermissionResponse(
            id=new_permission.id,
            service_id=new_permission.service_id,
            service_name=service.name,
            code=new_permission.code,
            name=new_permission.name,
            description=new_permission.description,
            created_at=new_permission.created_at.strftime('%d.%m.%Y') if new_permission.created_at else None
        )
    finally:
        db.close()

@app.get("/api/as/users", summary="Получить список пользователей")
def get_users(api_key: str = Header(..., alias="api-key"), page: int = Query(1, ge=1), limit: int = Query(10, ge=1, le=100)):
    db = SessionLocal()
    try:
        if not api_key.startswith("as_"):
            raise HTTPException(status_code=401, detail="API ключ должен начинаться с префикса 'as_'")

        key_record = db.query(ApiKey).filter(ApiKey.api_key == api_key, ApiKey.is_active == 1).first()
        if not key_record:
            raise HTTPException(status_code=401, detail="Недействительный или неактивный API ключ")

        offset = (page - 1) * limit
        users = db.query(User).offset(offset).limit(limit).all()
        result = []
        for u in users:
            gender = db.query(Gender.name).filter(Gender.id == u.gender_id).scalar()
            roles = db.query(Role.name).join(UserRole, UserRole.role_id == Role.id).filter(UserRole.user_id == u.id).all()
            roles_list = [r[0] for r in roles]
            result.append({
                "id": u.id,
                "name": u.name,
                "surname": u.surname,
                "patronymic": u.patronymic,
                "username": u.username,
                "gender": gender,
                "birthday": u.birthday.strftime('%d.%m.%Y') if u.birthday else None,
                "status": u.status,
                "roles": roles_list,
                "roles_count": len(roles_list)
            })
        return result
    finally:
        db.close()

@app.get("/api/as/permissions", summary="Получить список всех разрешений")
def get_permissions(api_key: str = Header(..., alias="api-key"), page: int = Query(1, ge=1), limit: int = Query(10, ge=1, le=100)):
    db = SessionLocal()
    try:
        if not api_key.startswith("as_"):
            raise HTTPException(status_code=401, detail="API ключ должен начинаться с префикса 'as_'")

        key_record = db.query(ApiKey).filter(ApiKey.api_key == api_key, ApiKey.is_active == 1).first()
        if not key_record:
            raise HTTPException(status_code=401, detail="Недействительный или неактивный API ключ")

        offset = (page - 1) * limit
        permissions = db.query(Permission, Service.name.label('service_name')).join(Service, Permission.service_id == Service.id).offset(offset).limit(limit).all()
        result = []
        for p, service_name in permissions:
            result.append({
                "id": p.id,
                "service_id": p.service_id,
                "service_name": service_name,
                "code": p.code,
                "name": p.name,
                "description": p.description,
                "created_at": p.created_at.strftime('%d.%m.%Y') if p.created_at else None
            })
        return result
    finally:
        db.close()

@app.get("/api/as/permissions/{service_id}", summary="Получить разрешения для конкретного сервиса")
def get_permissions_by_service(service_id: str, api_key: str = Header(..., alias="api-key")):
    db = SessionLocal()
    try:
        if not api_key.startswith("as_"):
            raise HTTPException(status_code=401, detail="API ключ должен начинаться с префикса 'as_'")

        key_record = db.query(ApiKey).filter(ApiKey.api_key == api_key, ApiKey.is_active == 1).first()
        if not key_record:
            raise HTTPException(status_code=401, detail="Недействительный или неактивный API ключ")

        permissions = db.query(Permission, Service.name.label('service_name')).join(Service, Permission.service_id == Service.id).filter(Permission.service_id == service_id).all()
        result = []
        for p, service_name in permissions:
            result.append({
                "id": p.id,
                "service_id": p.service_id,
                "service_name": service_name,
                "code": p.code,
                "name": p.name,
                "description": p.description,
                "created_at": p.created_at.strftime('%d.%m.%Y') if p.created_at else None
            })
        return result
    finally:
        db.close()

@app.post("/api/as/services/create", summary="Создать сервис", response_model=ServiceResponse)
def create_service(service: ServiceCreate, api_key: str = Header(..., alias="api-key")):
    db = SessionLocal()
    try:
        if not api_key.startswith("as_"):
            raise HTTPException(status_code=401, detail="API ключ должен начинаться с префикса 'as_'")

        key_record = db.query(ApiKey).filter(ApiKey.api_key == api_key, ApiKey.is_active == 1).first()
        if not key_record:
            raise HTTPException(status_code=401, detail="Недействительный или неактивный API ключ")

        new_service = Service(
            name=service.name,
            description=service.description,
            prefix=service.prefix
        )
        db.add(new_service)
        db.commit()
        db.refresh(new_service)

        permissions_count = db.query(func.count(Permission.id)).filter(Permission.service_id == new_service.id).scalar()

        return ServiceResponse(
            id=new_service.id,
            name=new_service.name,
            description=new_service.description,
            prefix=new_service.prefix,
            image_url=new_service.image_url,
            created_at=new_service.created_at.strftime('%d.%m.%Y') if new_service.created_at else None,
            permissions_count=permissions_count
        )
    finally:
        db.close()