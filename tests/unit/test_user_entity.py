import pytest
from grpc_tutorial.domain.models.user import User
import time


def test_create_user_happy_path():
    now = int(time.time())
    u = User(name="Alice", email="alice@example.com")
    assert u.id is not None and isinstance(u.id, str)
    assert u.name == "Alice"
    assert u.email == "alice@example.com"
    assert u.created_at >= now - 1  # допускаем небольшую погрешность


@pytest.mark.parametrize("bad_email", ["", "no-at.com", "a@b", " spaced@a.com", "a@.com"])
def test_user_invalid_email_raises(bad_email):
    with pytest.raises(ValueError):
        User(name="Bob", email=bad_email)


def test_user_empty_name_raises():
    with pytest.raises(ValueError):
        User(name="", email="ok@example.com")