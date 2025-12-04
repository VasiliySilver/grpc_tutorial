"""Use Case: Получение списка пользователей с пагинацией."""
from typing import Tuple, Sequence
from ...domain.models.user import User
from ...domain.repositories.user_repository import UserRepository


class ListUsersUseCase:
    """
    Use Case для получения списка пользователей с пагинацией.
    
    Поддерживает:
    - Пагинацию (page, page_size)
    - Возврат общего количества для расчета страниц
    """
    
    def __init__(self, user_repository: UserRepository):
        self._user_repository = user_repository
    
    def execute(
        self, 
        page: int = 1, 
        page_size: int = 20
    ) -> Tuple[Sequence[User], int]:
        """
        Получить список пользователей.
        
        Args:
            page: Номер страницы (начинается с 1)
            page_size: Количество элементов на странице
        
        Returns:
            Tuple[Sequence[User], int]: (список пользователей, общее количество)
        
        Raises:
            ValueError: Если page или page_size < 1
        """
        return self._user_repository.list(page=page, page_size=page_size)