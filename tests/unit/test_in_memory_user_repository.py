import pytest
from grpc_tutorial.domain.models.user import User
from grpc_tutorial.infrastructure.persistence.in_memory_user_repository import InMemoryUserRepository


def test_save_and_get_by_id():
    repo = InMemoryUserRepository()
    u = User(name="Test", email="t@example.com")
    repo.save(u)
    got = repo.get_by_id(u.id)
    assert got == u


def test_list_pagination_and_total():
    repo = InMemoryUserRepository()
    users = [User(name=f"u{i}", email=f"user{i}@ex.com") for i in range(1, 11)]
    for u in users:
        repo.save(u)

    page1, total = repo.list(page=1, page_size=3)
    assert total == 10
    assert len(page1) == 3
    page4, _ = repo.list(page=4, page_size=3)
    # pages: 3+3+3+1
    assert len(page4) == 1


def test_invalid_pagination_raises():
    repo = InMemoryUserRepository()
    with pytest.raises(ValueError):
        repo.list(page=0, page_size=10)
    with pytest.raises(ValueError):
        repo.list(page=1, page_size=0)