"""
Интеграционные тесты для gRPC сервиса.

Запускают реальный gRPC сервер и тестируют через клиент.
"""
import pytest
import grpc
import time
from threading import Thread

from grpc_tutorial.infrastructure.grpc.server.grpc_server import GrpcServer
from grpc_tutorial.infrastructure.grpc.client.user_client import UserClient
from grpc_tutorial.infrastructure.persistence.in_memory_user_repository import (
    InMemoryUserRepository
)


@pytest.fixture(scope="module")
def grpc_server():
    """
    Фикстура: запускает gRPC сервер в отдельном потоке.
    """
    # Создаем репозиторий и сервер
    repository = InMemoryUserRepository()
    server = GrpcServer(
        user_repository=repository,
        host="localhost",
        port=50052  # Используем другой порт для тестов
    )
    
    # Запускаем сервер в отдельном потоке
    server.start()
    
    # Даем серверу время на запуск
    time.sleep(0.5)
    
    yield server
    
    # Останавливаем сервер после тестов
    server.stop()


@pytest.fixture
def user_client(grpc_server):
    """
    Фикстура: создает gRPC клиента для тестов.
    """
    with UserClient(host="localhost", port=50052) as client:
        yield client


class TestUserServiceIntegration:
    """Интеграционные тесты UserService через gRPC."""
    
    def test_create_user_success(self, user_client):
        """Тест: создание пользователя через gRPC."""
        user = user_client.create_user(
            name="Integration Test User",
            email="integration@test.com"
        )
        
        assert user.id is not None
        assert user.name == "Integration Test User"
        assert user.email == "integration@test.com"
        assert user.created_at > 0
    
    def test_create_user_invalid_email(self, user_client):
        """Тест: создание с невалидным email возвращает ошибку."""
        with pytest.raises(grpc.RpcError) as exc_info:
            user_client.create_user(name="Test", email="invalid")
        
        assert exc_info.value.code() == grpc.StatusCode.INVALID_ARGUMENT
        assert "email is invalid" in exc_info.value.details()
    
    def test_get_user_found(self, user_client):
        """Тест: получение существующего пользователя."""
        # Сначала создаем пользователя
        created = user_client.create_user(
            name="Get Test",
            email="get@test.com"
        )
        
        # Получаем его по ID
        fetched = user_client.get_user(created.id)
        
        assert fetched is not None
        assert fetched.id == created.id
        assert fetched.name == created.name
        assert fetched.email == created.email
    
    def test_get_user_not_found(self, user_client):
        """Тест: получение несуществующего пользователя."""
        result = user_client.get_user("nonexistent-id")
        assert result is None
    
    def test_list_users_pagination(self, user_client):
        """Тест: получение списка пользователей с пагинацией."""
        # Создаем несколько пользователей
        for i in range(5):
            user_client.create_user(
                name=f"List User {i}",
                email=f"list{i}@test.com"
            )
        
        # Получаем первую страницу (3 элемента)
        users, total = user_client.list_users(page=1, page_size=3)
        
        assert len(users) == 3
        assert total >= 5  # Могут быть пользователи из других тестов
    
    def test_list_users_empty(self, user_client):
        """Тест: список пользователей на пустой странице."""
        users, total = user_client.list_users(page=999, page_size=10)
        assert len(users) == 0