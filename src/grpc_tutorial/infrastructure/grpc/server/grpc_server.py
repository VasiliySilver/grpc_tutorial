"""
gRPC сервер для UserService.

Infrastructure Layer - технические детали запуска сервера.
"""
import grpc
from concurrent import futures
import logging
from typing import Optional

from ....presentation.grpc_handlers.user_handler import UserServiceHandler
from ....domain.repositories.user_repository import UserRepository
from ..proto import user_service_pb2_grpc


# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class GrpcServer:
    """
    Обертка для gRPC сервера.
    
    Ответственность:
    - Запуск и остановка gRPC сервера
    - Регистрация сервисов
    - Конфигурация (порт, workers, etc.)
    """
    
    def __init__(
        self,
        user_repository: UserRepository,
        host: str = "localhost",
        port: int = 50051,
        max_workers: int = 10
    ):
        """
        Args:
            user_repository: Репозиторий для работы с пользователями
            host: Хост для прослушивания (localhost, 0.0.0.0, etc.)
            port: Порт для прослушивания (по умолчанию 50051 - стандартный для gRPC)
            max_workers: Максимальное количество worker threads
        """
        self._host = host
        self._port = port
        self._user_repository = user_repository
        
        # Создаем gRPC сервер с ThreadPool
        self._server = grpc.server(
            futures.ThreadPoolExecutor(max_workers=max_workers)
        )
        
        # Регистрируем UserService handler
        user_handler = UserServiceHandler(user_repository)
        user_service_pb2_grpc.add_UserServiceServicer_to_server(
            user_handler,
            self._server
        )
        
        # Добавляем insecure порт (без TLS - только для разработки!)
        self._server.add_insecure_port(f"{self._host}:{self._port}")
        
        logger.info(f"gRPC server initialized on {self._host}:{self._port}")
    
    def start(self) -> None:
        """Запустить сервер (неблокирующий)."""
        self._server.start()
        logger.info(f"🚀 gRPC server started on {self._host}:{self._port}")
        logger.info("Services:")
        logger.info("  - UserService (CreateUser, GetUser, ListUsers)")
    
    def stop(self, grace: Optional[int] = 5) -> None:
        """
        Остановить сервер.
        
        Args:
            grace: Время ожидания (в секундах) для graceful shutdown
        """
        logger.info("Stopping gRPC server...")
        self._server.stop(grace)
        logger.info("✅ gRPC server stopped")
    
    def wait_for_termination(self) -> None:
        """Блокировать текущий поток до остановки сервера."""
        self._server.wait_for_termination()


def main():
    """
    Точка входа для запуска сервера.
    
    Использование:
        python -m grpc_tutorial.infrastructure.grpc.server.grpc_server
    """
    from ....infrastructure.persistence.in_memory_user_repository import (
        InMemoryUserRepository
    )
    
    # Создаем репозиторий (в production это будет PostgreSQL, MongoDB, etc.)
    user_repository = InMemoryUserRepository()
    
    # Создаем и запускаем сервер
    server = GrpcServer(user_repository=user_repository)
    
    try:
        server.start()
        logger.info("Press Ctrl+C to stop")
        server.wait_for_termination()
    except KeyboardInterrupt:
        logger.info("Received shutdown signal")
        server.stop()


if __name__ == "__main__":
    main()