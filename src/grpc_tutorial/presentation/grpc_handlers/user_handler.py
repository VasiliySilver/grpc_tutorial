"""
gRPC Handler для UserService.

Presentation Layer - преобразует gRPC запросы в вызовы Use Cases
и результаты Use Cases в gRPC ответы.
"""
import grpc
from typing import Optional

# Импорты сгенерированных proto классов
from ...infrastructure.grpc.proto import user_service_pb2
from ...infrastructure.grpc.proto import user_service_pb2_grpc

# Импорты Use Cases
from ...application.use_cases.create_user_use_case import CreateUserUseCase
from ...application.use_cases.get_user_use_case import GetUserUseCase
from ...application.use_cases.list_users_use_case import ListUsersUseCase

# Импорты Domain
from ...domain.models.user import User
from ...domain.repositories.user_repository import UserRepository


class UserServiceHandler(user_service_pb2_grpc.UserServiceServicer):
    """
    Реализация UserService gRPC сервиса.
    
    Паттерн: Adapter (адаптирует gRPC к Use Cases)
    
    Ответственность:
    - Получить gRPC запрос (protobuf объект)
    - Извлечь данные из запроса
    - Вызвать соответствующий Use Case
    - Преобразовать результат Use Case в gRPC ответ (protobuf)
    - Обработать ошибки и вернуть соответствующий gRPC статус
    """
    
    def __init__(self, user_repository: UserRepository):
        """
        Args:
            user_repository: Репозиторий пользователей (dependency injection)
        """
        # Инициализируем Use Cases
        self._create_user_use_case = CreateUserUseCase(user_repository)
        self._get_user_use_case = GetUserUseCase(user_repository)
        self._list_users_use_case = ListUsersUseCase(user_repository)
    
    def CreateUser(
        self, 
        request: user_service_pb2.CreateUserRequest,
        context: grpc.ServicerContext
    ) -> user_service_pb2.CreateUserResponse:
        """
        gRPC метод: Создать нового пользователя.
        
        Args:
            request: gRPC запрос с данными пользователя
            context: gRPC контекст (для установки статусов, metadata, etc.)
        
        Returns:
            CreateUserResponse: gRPC ответ с созданным пользователем
        """
        try:
            # Вызываем Use Case
            user = self._create_user_use_case.execute(
                name=request.name,
                email=request.email
            )
            
            # Преобразуем Domain модель в protobuf
            user_pb = self._user_to_proto(user)
            
            # Возвращаем успешный ответ
            return user_service_pb2.CreateUserResponse(
                user=user_pb,
                message="User created successfully"
            )
            
        except ValueError as e:
            # Ошибка валидации - возвращаем INVALID_ARGUMENT
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            context.set_details(str(e))
            return user_service_pb2.CreateUserResponse()
        
        except Exception as e:
            # Неожиданная ошибка - возвращаем INTERNAL
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"Internal error: {str(e)}")
            return user_service_pb2.CreateUserResponse()
    
    def GetUser(
        self,
        request: user_service_pb2.GetUserRequest,
        context: grpc.ServicerContext
    ) -> user_service_pb2.GetUserResponse:
        """
        gRPC метод: Получить пользователя по ID.
        """
        try:
            user = self._get_user_use_case.execute(user_id=request.id)
            
            if user is None:
                # Пользователь не найден - возвращаем NOT_FOUND
                context.set_code(grpc.StatusCode.NOT_FOUND)
                context.set_details(f"User with id '{request.id}' not found")
                return user_service_pb2.GetUserResponse()
            
            # Преобразуем в protobuf и возвращаем
            user_pb = self._user_to_proto(user)
            return user_service_pb2.GetUserResponse(user=user_pb)
            
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"Internal error: {str(e)}")
            return user_service_pb2.GetUserResponse()
    
    def ListUsers(
        self,
        request: user_service_pb2.ListUsersRequest,
        context: grpc.ServicerContext
    ) -> user_service_pb2.ListUsersResponse:
        """
        gRPC метод: Получить список пользователей с пагинацией.
        """
        try:
            # Используем дефолтные значения если не указаны
            page = request.page if request.page > 0 else 1
            page_size = request.page_size if request.page_size > 0 else 20
            
            users, total = self._list_users_use_case.execute(
                page=page,
                page_size=page_size
            )
            
            # Преобразуем список Domain моделей в protobuf
            users_pb = [self._user_to_proto(user) for user in users]
            
            return user_service_pb2.ListUsersResponse(
                users=users_pb,
                total=total
            )
            
        except ValueError as e:
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            context.set_details(str(e))
            return user_service_pb2.ListUsersResponse()
        
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"Internal error: {str(e)}")
            return user_service_pb2.ListUsersResponse()
    
    @staticmethod
    def _user_to_proto(user: User) -> user_service_pb2.User:
        """
        Преобразует Domain модель User в protobuf User.
        
        Это mapping layer между внутренним представлением и внешним API.
        """
        return user_service_pb2.User(
            id=user.id,
            name=user.name,
            email=user.email,
            created_at=user.created_at
        )