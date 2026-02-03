import grpc

from app.database import get_db
from app.repositories.permission_repository import PermissionRepository
from app.repositories.session_repository import SessionRepository
from generated.auth_pb2 import PermissionRequest, PermissionResponse
from generated.auth_pb2_grpc import PermissionServiceServicer


class PermissionGrpcService(PermissionServiceServicer):
    def ValidatePermission(
        self, request: PermissionRequest, context: grpc.ServicerContext
    ) -> PermissionResponse:
        """
        Валидация разрешений пользователя

        Args:
            request: PermissionRequest с полями session_token, service, entity, action
            context: gRPC context

        Returns:
            PermissionResponse с полями is_access, message, code
        """
        db = None
        try:
            db = next(get_db())  # pyright: ignore[reportArgumentType]

            perm_repo = PermissionRepository(db)
            session_repo = SessionRepository(db)

            session = session_repo.get_by_token(request.session_token)

            if not session:
                return PermissionResponse(
                    is_access=False,
                    message="Сессия не действительная",
                    code=401,
                )

            exist = perm_repo.exist_by_user_id(
                str(session.user_id),
                request.service,
                request.entity,
                request.action,
            )

            if not exist:
                return PermissionResponse(is_access=False, message="Нет разрешения", code=403)

            return PermissionResponse(is_access=True, message="Разрешение получено", code=200)

        except StopIteration:
            # Не удалось получить сессию БД
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details("Database connection failed")

            return PermissionResponse(
                is_access=False, message="Ошибка подключения к базе данных", code=500
            )

        except Exception as e:
            # Логирование ошибки
            print(f"Error in ValidatePermission: {e}")

            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"Internal server error: {str(e)}")

            return PermissionResponse(
                is_access=False, message=f"Внутренняя ошибка сервера: {str(e)}", code=500
            )

        finally:
            # ✅ Закрываем соединение с БД
            if db is not None:
                db.close()
