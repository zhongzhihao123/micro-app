"""
异常定义
=======
统一的异常类层次结构，用于 API 错误响应和业务逻辑错误处理。
所有自定义异常继承自 AppException，FastAPI 全局异常处理器会自动捕获并返回 JSON 响应。

异常层级：
  AppException (500)          基础异常
  ├── NotFoundException (404) 资源未找到
  ├── ValidationException (422) 参数校验失败
  ├── UnauthorizedException (401) 未认证
  ├── ForbiddenException (403) 无权限
  ├── RateLimitException (429) 请求频率限制
  └── ServiceUnavailableException (503) 服务不可用
"""
from typing import Any, Optional


class AppException(Exception):
    """应用基础异常"""

    def __init__(self, message: str, status_code: int = 500, detail: Optional[Any] = None):
        self.message = message
        self.status_code = status_code
        self.detail = detail
        super().__init__(message)


class NotFoundException(AppException):
    """资源未找到"""

    def __init__(self, resource: str, resource_id: str):
        super().__init__(
            message=f"{resource} not found: {resource_id}",
            status_code=404,
        )


class ValidationException(AppException):
    """参数验证失败"""

    def __init__(self, message: str, detail: Optional[Any] = None):
        super().__init__(message=message, status_code=422, detail=detail)


class UnauthorizedException(AppException):
    """未授权"""

    def __init__(self, message: str = "Unauthorized"):
        super().__init__(message=message, status_code=401)


class ForbiddenException(AppException):
    """无权限"""

    def __init__(self, message: str = "Forbidden"):
        super().__init__(message=message, status_code=403)


class RateLimitException(AppException):
    """请求频率限制"""

    def __init__(self, retry_after: int = 60):
        super().__init__(
            message=f"Rate limit exceeded. Retry after {retry_after}s",
            status_code=429,
        )


class ServiceUnavailableException(AppException):
    """服务不可用"""

    def __init__(self, service: str):
        super().__init__(
            message=f"Service unavailable: {service}",
            status_code=503,
        )
