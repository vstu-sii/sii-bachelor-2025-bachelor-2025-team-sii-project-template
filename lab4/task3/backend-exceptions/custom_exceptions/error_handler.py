"""
Обработчики ошибок для FastAPI.
"""
import logging
import traceback
from typing import Any, Dict, Union
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import SQLAlchemyError
from pydantic import ValidationError

from ..custom_exceptions.base import APIException
from ..custom_exceptions.business import (
    DatabaseConnectionException,
    ExternalServiceException
)

logger = logging.getLogger(__name__)

def setup_exception_handlers(app: FastAPI) -> None:
    """Настройка обработчиков исключений для приложения."""
    
    # Обработчик кастомных исключений API
    @app.exception_handler(APIException)
    async def api_exception_handler(request: Request, exc: APIException) -> JSONResponse:
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "detail": exc.detail,
                "error_code": exc.error_code,
                "errors": exc.errors,
                "path": request.url.path,
                "method": request.method
            },
            headers=exc.headers
        )
    
    # Обработчик ошибок валидации FastAPI
    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(
        request: Request, 
        exc: RequestValidationError
    ) -> JSONResponse:
        errors = []
        
        for error in exc.errors():
            field = " -> ".join(str(loc) for loc in error["loc"] if loc != "body")
            errors.append({
                "field": field or "body",
                "message": error["msg"],
                "type": error["type"]
            })
        
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={
                "detail": "Ошибка валидации данных",
                "error_code": "VALIDATION_ERROR",
                "errors": errors,
                "path": request.url.path,
                "method": request.method
            }
        )
    
    # Обработчик ошибок валидации Pydantic
    @app.exception_handler(ValidationError)
    async def pydantic_validation_exception_handler(
        request: Request, 
        exc: ValidationError
    ) -> JSONResponse:
        errors = []
        
        for error in exc.errors():
            field = " -> ".join(str(loc) for loc in error["loc"])
            errors.append({
                "field": field,
                "message": error["msg"],
                "type": error["type"]
            })
        
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={
                "detail": "Ошибка валидации данных",
                "error_code": "VALIDATION_ERROR",
                "errors": errors,
                "path": request.url.path,
                "method": request.method
            }
        )
    
    # Обработчик ошибок SQLAlchemy
    @app.exception_handler(SQLAlchemyError)
    async def sqlalchemy_exception_handler(
        request: Request, 
        exc: SQLAlchemyError
    ) -> JSONResponse:
        logger.error(f"Database error: {exc}", exc_info=True)
        
        # Преобразуем в более понятное для пользователя исключение
        db_exc = DatabaseConnectionException()
        
        return JSONResponse(
            status_code=db_exc.status_code,
            content={
                "detail": db_exc.detail,
                "error_code": db_exc.error_code,
                "path": request.url.path,
                "method": request.method
            }
        )
    
    # Обработчик всех остальных исключений
    @app.exception_handler(Exception)
    async def global_exception_handler(
        request: Request, 
        exc: Exception
    ) -> JSONResponse:
        logger.error(f"Unhandled exception: {exc}", exc_info=True)
        
        # Логируем полный traceback
        tb = traceback.format_exc()
        logger.error(f"Traceback: {tb}")
        
        # Определяем тип ошибки
        error_type = type(exc).__name__
        
        # Для определенных типов исключений возвращаем специфичные ответы
        if "ConnectionError" in error_type or "Timeout" in error_type:
            service_exc = ExternalServiceException("внешнего API")
            status_code = service_exc.status_code
            detail = service_exc.detail
            error_code = service_exc.error_code
        else:
            status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
            detail = "Внутренняя ошибка сервера"
            error_code = "INTERNAL_SERVER_ERROR"
        
        # В development режиме показываем больше деталей
        content: Dict[str, Any] = {
            "detail": detail,
            "error_code": error_code,
            "path": request.url.path,
            "method": request.method
        }
        
        # В development добавляем детали ошибки
        if request.app.debug:
            content.update({
                "exception_type": error_type,
                "exception_message": str(exc),
                "traceback": tb.split("\n") if request.app.debug else None
            })
        
        return JSONResponse(
            status_code=status_code,
            content=content
        )
    
    # Обработчик 404 ошибок
    @app.exception_handler(404)
    async def not_found_exception_handler(
        request: Request, 
        exc: Exception
    ) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={
                "detail": "Запрашиваемый ресурс не найден",
                "error_code": "NOT_FOUND",
                "path": request.url.path,
                "method": request.method
            }
        )
    
    # Обработчик 405 ошибок
    @app.exception_handler(405)
    async def method_not_allowed_handler(
        request: Request, 
        exc: Exception
    ) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_405_METHOD_NOT_ALLOWED,
            content={
                "detail": "Метод не разрешен для данного URL",
                "error_code": "METHOD_NOT_ALLOWED",
                "path": request.url.path,
                "method": request.method
            }
        )

def create_error_response(
    status_code: int,
    detail: str,
    error_code: str = None,
    errors: list = None,
    path: str = None,
    method: str = None
) -> Dict[str, Any]:
    """Создание стандартизированного ответа с ошибкой."""
    
    response = {
        "detail": detail,
        "error_code": error_code or "UNKNOWN_ERROR",
    }
    
    if errors:
        response["errors"] = errors
    
    if path:
        response["path"] = path
    
    if method:
        response["method"] = method
    
    return response
