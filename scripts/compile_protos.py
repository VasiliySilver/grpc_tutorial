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
import re


def compile_protos():
    """
    Компилирует все .proto файлы в директории proto.
    
    Процесс:
    1. Находит директорию с .proto файлами
    2. Ищет все файлы с расширением .proto
    3. Для каждого файла вызывает компилятор protoc
    4. Генерирует Python код в той же директории
    5. Исправляет импорты в сгенерированных файлах
    """
    # Определяем путь к директории с .proto файлами
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
        # Используем src/ как базовую директорию для proto_path
        src_dir = Path(__file__).parent.parent / "src"
        
        cmd = [
            "python", "-m", "grpc_tools.protoc",
            
            # --proto_path - где искать .proto файлы
            f"--proto_path={src_dir}",
            
            # --python_out - куда сохранить *_pb2.py файлы
            f"--python_out={src_dir}",
            
            # --grpc_python_out - куда сохранить *_pb2_grpc.py файлы
            f"--grpc_python_out={src_dir}",
            
            # Путь к компилируемому файлу (относительно proto_path)
            "grpc_tutorial/infrastructure/grpc/proto/" + proto_file.name
        ]
        
        # Выполняем команду компиляции
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        # Проверяем результат
        if result.returncode != 0:
            print(f"❌ Error compiling {proto_file.name}:")
            print(result.stderr)
        else:
            print(f"✅ Successfully compiled {proto_file.name}")
            
            # Исправляем импорты в сгенерированных файлах
            fix_imports(proto_dir, proto_file.stem)
            
            print(f"   Generated: {proto_file.stem}_pb2.py")
            print(f"   Generated: {proto_file.stem}_pb2_grpc.py")
            print(f"   Fixed imports ✓\n")


def fix_imports(proto_dir: Path, proto_name: str):
    """
    Исправляет импорты в сгенерированных файлах.
    
    Меняет:
        from src.grpc_tutorial.infrastructure.grpc.proto import user_service_pb2
    На:
        from . import user_service_pb2
    """
    # Исправляем импорты в _pb2_grpc.py файле
    grpc_file = proto_dir / f"{proto_name}_pb2_grpc.py"
    
    if grpc_file.exists():
        content = grpc_file.read_text()
        
        # Заменяем абсолютный импорт на относительный
        # Паттерн: from src.grpc_tutorial.infrastructure.grpc.proto import X
        # Замена: from . import X
        pattern = r'from src\.grpc_tutorial\.infrastructure\.grpc\.proto import (\w+)'
        replacement = r'from . import \1'
        
        fixed_content = re.sub(pattern, replacement, content)
        
        # Записываем исправленное содержимое
        grpc_file.write_text(fixed_content)


if __name__ == "__main__":
    print("=" * 60)
    print("🚀 Protocol Buffers Compilation Script")
    print("=" * 60 + "\n")
    compile_protos()
    print("\n" + "=" * 60)
    print("✨ Compilation completed!")
    print("=" * 60)