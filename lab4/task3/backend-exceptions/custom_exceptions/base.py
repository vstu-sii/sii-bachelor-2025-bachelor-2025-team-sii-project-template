"""
Базовые классы исключений для API.
"""
from typing import Any, Dict, Optional, List
from fastapi import status

class APIException(Exception):
    """Базовое исключение для API ошибок."""
    
    def __init__(
        self,
        status_code: int,
        detail: str,
        error_code: Optional[str] = None,
        errors: Optional[List[Dict[str, Any]]] = None,
        headers: Optional[Dict[str, str]] = None
    ):
        self.status_code = status_code
        self.detail = detail
        self.error_code = error_code
        self.errors = errors or []
        self.headers = headers or {}
        super().__init__(self.detail)

class ValidationException(APIException):
    """Исключение для ошибок валидации."""
    
    def __init__(
        self,
        detail: str = "Ошибка валидации данных",
        errors: Optional[List[Dict[str, Any]]] = None,
        error_code: str = "VALIDATION_ERROR"
    ):
        super().__init__(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=detail,
            error_code=error_code,
            errors=errors
        )

class AuthenticationException(APIException):
    """Исключение для ошибок аутентификации."""
    
    def __init__(
        self,
        detail: str = "Ошибка аутентификации",
        error_code: str = "AUTHENTICATION_ERROR",
        headers: Optional[Dict[str, str]] = None
    ):
        if headers is None:
            headers = {"WWW-Authenticate": "Bearer"}
            
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail,
            error_code=error_code,
            headers=headers
        )

class AuthorizationException(APIException):
    """Исключение для ошибок авторизации."""
    
    def __init__(
        self,
        detail: str = "Недостаточно прав для выполнения операции",
        error_code: str = "AUTHORIZATION_ERROR"
    ):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=detail,
            error_code=error_code
        )

class NotFoundException(APIException):
    """Исключение для ошибок "Не найдено"."""
    
    def __init__(
        self,
        detail: str = "Запрошенный ресурс не найден",
        error_code: str = "NOT_FOUND"
    ):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=detail,
            error_code=error_code
        )

class ConflictException(APIException):
    """Исключение для конфликтующих операций."""
    
    def __init__(
        self,
        detail: str = "Конфликт при выполнении операции",
        error_code: str = "CONFLICT_ERROR"
    ):
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            detail=detail,
            error_code=error_code
        )

class RateLimitException(APIException):
    """Исключение для превышения лимита запросов."""
    
    def __init__(
        self,
        detail: str = "Превышен лимит запросов",
        error_code: str = "RATE_LIMIT_EXCEEDED",
        retry_after: Optional[int] = None
    ):
        headers = {}
        if retry_after:
            headers["Retry-After"] = str(retry_after)
            
        super().__init__(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=detail,
            error_code=error_code,
            headers=headers
        )

class InternalServerException(APIException):
    """Исключение для внутренних ошибок сервера."""
    
    def __init__(
        self,
        detail: str = "Внутренняя ошибка сервера",
        error_code: str = "INTERNAL_SERVER_ERROR"
    ):
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=detail,
            error_code=error_code
        )

class ServiceUnavailableException(APIException):
    """Исключение для недоступности сервиса."""
    
    def __init__(
        self,
        detail: str = "Сервис временно недоступен",
        error_code: str = "SERVICE_UNAVAILABLE",
        retry_after: Optional[int] = 30
    ):
        headers = {}
        if retry_after:
            headers["Retry-After"] = str(retry_after)
            
        super().__init__(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=detail,
            error_code=error_code,
            headers=headers
        )
