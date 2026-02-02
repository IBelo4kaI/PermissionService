"""
Запуск gRPC и FastAPI серверов одновременно
"""

import threading
from concurrent import futures

import grpc
import uvicorn

from app.services.permission_grpc_service import PermissionGrpcService
from generated.auth_pb2_grpc import add_PermissionServiceServicer_to_server


def run_grpc_server():
    """Запуск gRPC сервера в отдельном потоке"""
    print("🚀 Starting gRPC server on localhost:8383...")

    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    add_PermissionServiceServicer_to_server(PermissionGrpcService(), server)
    server.add_insecure_port("0.0.0.0:8383")

    server.start()
    print("✅ gRPC server started successfully on localhost:8383")

    try:
        server.wait_for_termination()
    except KeyboardInterrupt:
        print("🛑 Stopping gRPC server...")
        server.stop(0)


def run_fastapi_server():
    """Запуск FastAPI сервера"""
    print("🚀 Starting FastAPI server on 0.0.0.0:8382...")

    uvicorn.run(
        "app.api:app",
        host="0.0.0.0",
        port=8382,
        reload=True,  # ⚠️ Отключаем reload при многопоточном запуске
        log_level="info",
    )


if __name__ == "__main__":
    print("=" * 60)
    print("🔥 STARTING SERVERS")
    print("=" * 60)

    # Создаём поток для gRPC сервера
    grpc_thread = threading.Thread(target=run_grpc_server, daemon=True)
    grpc_thread.start()

    # Запускаем FastAPI в основном потоке
    # (uvicorn должен быть в основном потоке для правильной работы)
    try:
        run_fastapi_server()
    except KeyboardInterrupt:
        print("\n🛑 Shutting down servers...")
        print("✅ Servers stopped")
