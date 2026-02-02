from app.models.gender import Gender
from app.models.permission import PermissionBase, PermissionResponse
from app.models.role import RoleResponse
from app.models.service import Service, ServiceBase, ServiceCreate, ServiceResponse
from app.models.user import User
from app.models.user_roles import UserRole

RoleResponse.model_rebuild()
PermissionResponse.model_rebuild()
ServiceResponse.model_rebuild()
