from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Optional, Tuple, Sequence
from ..models.user import User


class UserRepository(ABC):
    """
    Repository interface for Users (domain boundary).
    Реализации (in-memory, db) должны реализовать эти методы.
    """

    @abstractmethod
    def save(self, user: User) -> None:
        """Сохраняет или обновляет пользователя."""
        raise NotImplementedError

    @abstractmethod
    def get_by_id(self, user_id: str) -> Optional[User]:
        """Возвращает User по id или None если не найден."""
        raise NotImplementedError

    @abstractmethod
    def list(self, page: int = 1, page_size: int = 20) -> Tuple[Sequence[User], int]:
        """
        Возвращает (users, total_count) для пагинации.
        page: 1-based
        """
        raise NotImplementedError