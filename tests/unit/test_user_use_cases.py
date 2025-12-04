"""
Тесты для Use Cases (Application Layer).
Используем mock репозиторий для изоляции от инфраструктуры.
"""
import pytest
from unittest.mock import Mock
from grpc_tutorial.domain.models.user import User
from grpc_tutorial.application.use_cases.create_user_use_case import CreateUserUseCase
from grpc_tutorial.application.use_cases.get_user_use_case import GetUserUseCase
from grpc_tutorial.application.use_cases.list_users_use_case import ListUsersUseCase


class TestCreateUserUseCase:
    """Тесты для создания пользователя."""
    
    def test_create_user_success(self):
        # Arrange: создаем mock репозитория
        mock_repo = Mock()
        use_case = CreateUserUseCase(user_repository=mock_repo)
        
        # Act: выполняем use case
        result = use_case.execute(name="Alice", email="alice@example.com")
        
        # Assert: проверяем результат
        assert isinstance(result, User)
        assert result.name == "Alice"
        assert result.email == "alice@example.com"
        assert result.id is not None
        
        # Проверяем что репозиторий был вызван один раз
        mock_repo.save.assert_called_once()
        saved_user = mock_repo.save.call_args[0][0]
        assert saved_user == result
    
    def test_create_user_invalid_email_raises(self):
        mock_repo = Mock()
        use_case = CreateUserUseCase(user_repository=mock_repo)
        
        # Должна возникнуть ошибка валидации
        with pytest.raises(ValueError, match="email is invalid"):
            use_case.execute(name="Bob", email="invalid-email")
        
        # Репозиторий не должен быть вызван при ошибке валидации
        mock_repo.save.assert_not_called()
    
    def test_create_user_empty_name_raises(self):
        mock_repo = Mock()
        use_case = CreateUserUseCase(user_repository=mock_repo)
        
        with pytest.raises(ValueError, match="name must be a non-empty string"):
            use_case.execute(name="", email="test@example.com")
        
        mock_repo.save.assert_not_called()


class TestGetUserUseCase:
    """Тесты для получения пользователя по ID."""
    
    def test_get_user_found(self):
        # Arrange
        mock_repo = Mock()
        expected_user = User(id="123", name="Test", email="test@example.com")
        mock_repo.get_by_id.return_value = expected_user
        use_case = GetUserUseCase(user_repository=mock_repo)
        
        # Act
        result = use_case.execute(user_id="123")
        
        # Assert
        assert result == expected_user
        mock_repo.get_by_id.assert_called_once_with("123")
    
    def test_get_user_not_found(self):
        mock_repo = Mock()
        mock_repo.get_by_id.return_value = None
        use_case = GetUserUseCase(user_repository=mock_repo)
        
        result = use_case.execute(user_id="nonexistent")
        
        assert result is None
        mock_repo.get_by_id.assert_called_once_with("nonexistent")


class TestListUsersUseCase:
    """Тесты для получения списка пользователей."""
    
    def test_list_users_with_pagination(self):
        # Arrange
        mock_repo = Mock()
        users = [
            User(name=f"User{i}", email=f"user{i}@example.com")
            for i in range(1, 6)
        ]
        mock_repo.list.return_value = (users, 50)  # (users, total_count)
        use_case = ListUsersUseCase(user_repository=mock_repo)
        
        # Act
        result_users, total = use_case.execute(page=1, page_size=5)
        
        # Assert
        assert len(result_users) == 5
        assert total == 50
        mock_repo.list.assert_called_once_with(page=1, page_size=5)
    
    def test_list_users_default_pagination(self):
        mock_repo = Mock()
        mock_repo.list.return_value = ([], 0)
        use_case = ListUsersUseCase(user_repository=mock_repo)
        
        use_case.execute()
        
        # Проверяем дефолтные значения пагинации
        mock_repo.list.assert_called_once_with(page=1, page_size=20)