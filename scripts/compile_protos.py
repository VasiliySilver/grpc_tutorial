"""
Скрипт для компиляции Protocol Buffer файлов (.proto) в Python код.

Protocol Buffers компилируются в два файла:
1. *_pb2.py - содержит классы для работы с данными (messages)
2. *_pb2_grpc.py - содержит классы для сервера и клиента (services)

Пример:
    user_service.proto → user_service_pb2.py + user_service_pb2_grpc.py
"""
import subprocess
from pathlib import Path


def compile_protos():
    """
    Компилирует все .proto файлы в директории proto.

    Процесс:
    1. Находит директорию с .proto файлами
    2. Ищет все файлы с расширением .proto
    3. Для каждого файла вызывает компилятор protoc
    4. Генерирует Python код в той же директории
    """
    # Определяем путь к директории с .proto файлами
    # Path(__file__).parent.parent - это корень проекта (на 2 уровня вверх от scripts/)
    proto_dir = (
        Path(__file__).parent.parent
        / "src"
        / "grpc_tutorial"
        / "infrastructure"
        / "grpc"
        / "proto"
    )

    # Находим все .proto файлы в директории
    proto_files = list(proto_dir.glob("*.proto"))

    # Если файлов нет - сообщаем и выходим
    if not proto_files:
        print("❌ No .proto files found")
        return

    print(f"📁 Found {len(proto_files)} proto file(s) to compile\n")

    # Компилируем каждый .proto файл
    for proto_file in proto_files:
        print(f"🔨 Compiling {proto_file.name}...")

        # Формируем команду для компиляции
        # python -m grpc_tools.protoc - запускает компилятор protoc через Python
        cmd = [
            "python", "-m", "grpc_tools.protoc",

            # --proto_path - где искать .proto файлы и их импорты
            f"--proto_path={proto_dir}",

            # --python_out - куда сохранить сгенерированные *_pb2.py файлы (messages)
            f"--python_out={proto_dir}",

            # --grpc_python_out - куда сохранить *_pb2_grpc.py файлы (services)
            f"--grpc_python_out={proto_dir}",

            # Путь к компилируемому файлу
            str(proto_file)
        ]

        # Выполняем команду компиляции
        result = subprocess.run(cmd, capture_output=True, text=True)

        # Проверяем результат
        if result.returncode != 0:
            print(f"❌ Error compiling {proto_file.name}:")
            print(result.stderr)
        else:
            print(f"✅ Successfully compiled {proto_file.name}")
            print(f"   Generated: {proto_file.stem}_pb2.py")
            print(f"   Generated: {proto_file.stem}_pb2_grpc.py\n")


if __name__ == "__main__":
    print("=" * 60)
    print("🚀 Protocol Buffers Compilation Script")
    print("=" * 60 + "\n")
    compile_protos()
    print("\n" + "=" * 60)
    print("✨ Compilation completed!")
    print("=" * 60)