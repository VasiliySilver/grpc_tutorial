"""
Демонстрация работы с gRPC клиентом.

Запуск:
    1. Запустите сервер: python -m grpc_tutorial.infrastructure.grpc.server.grpc_server
    2. Запустите этот скрипт: python examples/demo_client.py
"""
import sys
from pathlib import Path

# Добавляем src в PYTHONPATH
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from grpc_tutorial.infrastructure.grpc.client.user_client import UserClient
import grpc


def main():
    print("=" * 60)
    print("🚀 gRPC User Service Demo Client")
    print("=" * 60 + "\n")
    
    # Подключаемся к серверу
    with UserClient(host="localhost", port=50051) as client:
        
        # 1. Создаем пользователя
        print("📝 Creating user...")
        try:
            user = client.create_user(
                name="Alice Smith",
                email="alice@example.com"
            )
            print(f"✅ User created:")
            print(f"   ID: {user.id}")
            print(f"   Name: {user.name}")
            print(f"   Email: {user.email}")
            print(f"   Created: {user.created_at}\n")
            
            # 2. Получаем пользователя по ID
            print(f"🔍 Getting user by ID: {user.id}...")
            fetched = client.get_user(user.id)
            if fetched:
                print(f"✅ User found: {fetched.name}\n")
            
            # 3. Создаем еще пользователей
            print("📝 Creating more users...")
            for i in range(1, 4):
                client.create_user(
                    name=f"User {i}",
                    email=f"user{i}@example.com"
                )
            print(f"✅ Created 3 more users\n")
            
            # 4. Получаем список пользователей
            print("📋 Listing users (page 1, size 5)...")
            users, total = client.list_users(page=1, page_size=5)
            print(f"✅ Found {len(users)} users (total: {total}):")
            for u in users:
                print(f"   - {u.name} ({u.email})")
            print()
            
            # 5. Пытаемся создать невалидного пользователя
            print("❌ Trying to create user with invalid email...")
            try:
                client.create_user(name="Invalid", email="not-an-email")
            except grpc.RpcError as e:
                print(f"✅ Expected error: {e.details()}\n")
            
            # 6. Пытаемся получить несуществующего пользователя
            print("❌ Trying to get non-existent user...")
            result = client.get_user("nonexistent-id")
            if result is None:
                print("✅ User not found (as expected)\n")
        
        except grpc.RpcError as e:
            print(f"❌ gRPC Error: {e.code()} - {e.details()}")
            return 1
    
    print("=" * 60)
    print("✨ Demo completed successfully!")
    print("=" * 60)
    return 0


if __name__ == "__main__":
    sys.exit(main())