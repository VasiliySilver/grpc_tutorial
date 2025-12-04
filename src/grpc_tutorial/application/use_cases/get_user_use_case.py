"""Use Case: Получение пользователя по ID."""
from typing import Optional
from ...domain.models.user import User
from ...domain.repositories.user_repository import UserRepository


class GetUserUseCase:
    """
    Use Case для получения пользователя по его ID.
    
    Простой use case - просто делегирует вызов репозиторию.
    В реальном приложении здесь может быть дополнительная логика:
    - Проверка прав доступа
    - Логирование
    - Кэширование
    """
    
    def __init__(self, user_repository: UserRepository):
        self._user_repository = user_repository
    
    def execute(self, user_id: str) -> Optional[User]:
        """
        Получить пользователя по ID.
        
        Args:
            user_id: Уникальный идентификатор пользователя
        
        Returns:
            User если найден, None если не существует
        """
        return self._user_repository.get_by_id(user_id)