import grpc

from app.database import get_db
from app.repositories.permission_repository import PermissionRepository
from app.repositories.session_repository import SessionRepository
from app.repositories.user_repository import UserRepository
from generated.permission_pb2 import (
    GetUsersRequest,
    GetUsersResponse,
    UserResponse,
)
from generated.permission_pb2_grpc import UserServiceServicer


class UserGrpcService(UserServiceServicer):
    def GetUsers(self, request: GetUsersRequest, context: grpc.ServicerContext) -> GetUsersResponse:
        db = None
        try:
            db = next(get_db())  # pyright: ignore[reportArgumentType]

            perm_repo = PermissionRepository(db)
            session_repo = SessionRepository(db)
            user_repo = UserRepository(db)

            session = session_repo.get_by_token(request.permission_request.session_token)

            if not session:
                return GetUsersResponse(
                    message="Ошибка авторизации",
                    code=401,
                )

            exist = perm_repo.exist_by_user_id(
                str(session.user_id),
                request.permission_request.service,
                request.permission_request.entity,
                request.permission_request.action,
            )

            if not exist:
                return GetUsersResponse(
                    message="Нет доступа",
                    code=403,
                )

            users = user_repo.get_all_without_pages()

            users_response = [
                UserResponse(id=str(user.id), name=str(user.name), surname=str(user.surname))
                for user in users
            ]

            return GetUsersResponse(
                users=users_response,
                message="Разрешение получено",
                code=200,
            )

        except StopIteration:
            # Не удалось получить сессию БД
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details("Database connection failed")

            return GetUsersResponse(
                message="Ошибка подключения к базе данных",
                code=500,
            )

        except Exception as e:
            # Логирование ошибки
            print(f"Error in ValidatePermission: {e}")

            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"Internal server error: {str(e)}")
            return GetUsersResponse(
                message="Ошибка сервера",
                code=500,
            )

        finally:
            # ✅ Закрываем соединение с БД
            if db is not None:
                db.close()
