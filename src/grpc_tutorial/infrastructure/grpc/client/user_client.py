"""
gRPC клиент для UserService.

Используется для тестирования и как пример использования API.
"""
import grpc
from typing import List, Tuple, Optional

from ..proto import user_service_pb2
from ..proto import user_service_pb2_grpc


class UserClient:
    """
    Клиент для работы с UserService через gRPC.
    
    Пример использования:
        client = UserClient(host="localhost", port=50051)
        user = client.create_user(name="Alice", email="alice@example.com")
        print(f"Created user: {user.id}")
    """
    
    def __init__(self, host: str = "localhost", port: int = 50051):
        """
        Args:
            host: Хост gRPC сервера
            port: Порт gRPC сервера
        """
        self._channel = grpc.insecure_channel(f"{host}:{port}")
        self._stub = user_service_pb2_grpc.UserServiceStub(self._channel)
    
    def create_user(self, name: str, email: str) -> user_service_pb2.User:
        """
        Создать нового пользователя.
        
        Args:
            name: Имя пользователя
            email: Email пользователя
        
        Returns:
            User: Созданный пользователь
        
        Raises:
            grpc.RpcError: При ошибке gRPC (валидация, сеть, etc.)
        """
        request = user_service_pb2.CreateUserRequest(name=name, email=email)
        response = self._stub.CreateUser(request)
        return response.user
    
    def get_user(self, user_id: str) -> Optional[user_service_pb2.User]:
        """
        Получить пользователя по ID.
        
        Args:
            user_id: ID пользователя
        
        Returns:
            User если найден, None если не найден
        
        Raises:
            grpc.RpcError: При ошибке gRPC
        """
        request = user_service_pb2.GetUserRequest(id=user_id)
        try:
            response = self._stub.GetUser(request)
            return response.user if response.user.id else None
        except grpc.RpcError as e:
            if e.code() == grpc.StatusCode.NOT_FOUND:
                return None
            raise
    
    def list_users(
        self, 
        page: int = 1, 
        page_size: int = 20
    ) -> Tuple[List[user_service_pb2.User], int]:
        """
        Получить список пользователей с пагинацией.
        
        Args:
            page: Номер страницы (начинается с 1)
            page_size: Размер страницы
        
        Returns:
            Tuple[List[User], int]: (список пользователей, общее количество)
        """
        request = user_service_pb2.ListUsersRequest(
            page=page,
            page_size=page_size
        )
        response = self._stub.ListUsers(request)
        return list(response.users), response.total
    
    def close(self):
        """Закрыть соединение с сервером."""
        self._channel.close()
    
    def __enter__(self):
        """Context manager support."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager support."""
        self.close()