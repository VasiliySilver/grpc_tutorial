from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional
from uuid import uuid4
import time
import re


EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


@dataclass(frozen=True)
class User:
    """
    Domain entity: User.

    Правила:
    - id: автоматически генерируется, если не передан (uuid4 hex).
    - name: непустая строка.
    - email: проверяется простым regex.
    - created_at: unix timestamp (секунды); если не задан - текущий.
    """
    id: str = field(default_factory=lambda: uuid4().hex)
    name: str = field(default="")
    email: str = field(default="")
    created_at: int = field(default_factory=lambda: int(time.time()))

    def __post_init__(self):
        # В dataclass с frozen=True для валидации используем object.__setattr__ только при необходимости,
        # но тут валидации без изменения полей — просто бросаем ошибки.
        if not self.name or not isinstance(self.name, str):
            raise ValueError("User.name must be a non-empty string")
        if not isinstance(self.email, str) or not EMAIL_RE.match(self.email):
            raise ValueError(f"User.email is invalid: {self.email!r}")
        if not isinstance(self.created_at, int) or self.created_at <= 0:
            raise ValueError("User.created_at must be a positive int (unix timestamp)")