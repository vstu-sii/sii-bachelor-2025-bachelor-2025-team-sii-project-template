"""
Бизнес-исключения для конкретных доменных ошибок.
"""
from typing import Optional
from .base import (
    APIException,
    NotFoundException,
    ConflictException,
    ValidationException
)

class UserAlreadyExistsException(ConflictException):
    """Пользователь с таким email уже существует."""
    
    def __init__(self, email: str):
        super().__init__(
            detail=f"Пользователь с email {email} уже существует",
            error_code="USER_ALREADY_EXISTS"
        )

class InvalidCredentialsException(ValidationException):
    """Неверные учетные данные."""
    
    def __init__(self):
        super().__init__(
            detail="Неверный email или пароль",
            error_code="INVALID_CREDENTIALS"
        )

class DishNotFoundException(NotFoundException):
    """Блюдо не найдено."""
    
    def __init__(self, dish_id: int):
        super().__init__(
            detail=f"Блюдо с ID {dish_id} не найдено",
            error_code="DISH_NOT_FOUND"
        )

class DishAlreadyAnalyzedException(ConflictException):
    """Блюдо уже проанализировано."""
    
    def __init__(self, dish_id: int):
        super().__init__(
            detail=f"Блюдо с ID {dish_id} уже проанализировано",
            error_code="DISH_ALREADY_ANALYZED"
        )

class AnalysisNotFoundException(NotFoundException):
    """Анализ не найден."""
    
    def __init__(self, dish_id: int):
        super().__init__(
            detail=f"Анализ для блюда с ID {dish_id} не найден",
            error_code="ANALYSIS_NOT_FOUND"
        )

class FileTooLargeException(ValidationException):
    """Файл слишком большой."""
    
    def __init__(self, max_size_mb: int):
        super().__init__(
            detail=f"Файл слишком большой. Максимальный размер: {max_size_mb}MB",
            error_code="FILE_TOO_LARGE"
        )

class InvalidImageFormatException(ValidationException):
    """Неверный формат изображения."""
    
    def __init__(self, allowed_formats: Optional[list] = None):
        if allowed_formats:
            detail = f"Неверный формат изображения. Разрешены: {', '.join(allowed_formats)}"
        else:
            detail = "Неверный формат изображения"
            
        super().__init__(
            detail=detail,
            error_code="INVALID_IMAGE_FORMAT"
        )

class RecipeTooShortException(ValidationException):
    """Рецепт слишком короткий."""
    
    def __init__(self, min_length: int):
        super().__init__(
            detail=f"Рецепт слишком короткий. Минимум {min_length} символов",
            error_code="RECIPE_TOO_SHORT"
        )

class AIAnalysisFailedException(APIException):
    """Ошибка AI анализа."""
    
    def __init__(self, reason: str = "Не удалось проанализировать блюдо"):
        from fastapi import status
        
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка AI анализа: {reason}",
            error_code="AI_ANALYSIS_FAILED"
        )

class DatabaseConnectionException(APIException):
    """Ошибка подключения к базе данных."""
    
    def __init__(self):
        from fastapi import status
        
        super().__init__(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Ошибка подключения к базе данных. Попробуйте позже",
            error_code="DATABASE_CONNECTION_ERROR"
        )

class ExternalServiceException(APIException):
    """Ошибка внешнего сервиса."""
    
    def __init__(self, service_name: str):
        from fastapi import status
        
        super().__init__(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Ошибка сервиса {service_name}. Попробуйте позже",
            error_code="EXTERNAL_SERVICE_ERROR"
        )
