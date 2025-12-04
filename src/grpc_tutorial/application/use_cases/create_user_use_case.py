"""
Use Case: Создание нового пользователя.

Следует принципам Clean Architecture:
- Не зависит от деталей инфраструктуры (gRPC, база данных)
- Использует абстракцию Repository
- Содержит бизнес-логику приложения
"""


from grpc_tutorial.domain.models.user import User
from grpc_tutorial.domain.repositories.user_repository import UserRepository


class CreateUserUseCase:
    """
    Use Case для создания нового пользователя.
    
    Шаги:
    1. Получить данные (name, email)
    2. Создать сущность User (валидация происходит автоматически)
    3. Сохранить через Repository
    4. Вернуть созданного пользователя
    """
    
    def __init__(self, user_repository: UserRepository):
        """
        Args:
            user_repository: Репозиторий для работы с пользователями.
                            Может быть любая реализация (InMemory, PostgreSQL, etc.)
        """
        self._user_repository = user_repository
    
    def execute(self, name: str, email: str) -> User:
        """
        Создать нового пользователя.
        
        Args:
            name: Имя пользователя (не пустое)
            email: Email адрес (валидный формат)
        
        Returns:
            User: Созданный пользователь с сгенерированным id и timestamp
        
        Raises:
            ValueError: Если данные не валидны (пустое имя, невалидный email)
        """
        # Создаем сущность User - валидация происходит в __post_init__
        user = User(name=name, email=email)
        
        # Сохраняем через репозиторий
        self._user_repository.save(user)
        
        return user