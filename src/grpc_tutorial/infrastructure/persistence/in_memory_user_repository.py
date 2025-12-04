from __future__ import annotations
from typing import Optional, Tuple, List
from ...domain.models.user import User
from ...domain.repositories.user_repository import UserRepository
from threading import RLock


class InMemoryUserRepository(UserRepository):
    """
    Простая потокобезопасная in-memory реализация для тестов и локальной разработки.
    Использует dict: id -> User (immutable dataclass).
    """
    def __init__(self) -> None:
        self._store: dict[str, User] = {}
        self._lock = RLock()

    def save(self, user: User) -> None:
        with self._lock:
            self._store[user.id] = user

    def get_by_id(self, user_id: str) -> Optional[User]:
        with self._lock:
            return self._store.get(user_id)

    def list(self, page: int = 1, page_size: int = 20) -> Tuple[List[User], int]:
        if page < 1 or page_size < 1:
            raise ValueError("page and page_size must be positive integers")
        with self._lock:
            items = list(self._store.values())
            total = len(items)
            start = (page - 1) * page_size
            end = start + page_size
            return items[start:end], total