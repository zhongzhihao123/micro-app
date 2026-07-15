"""
AI System Platform - Common Library
====================================
共享模块：配置、数据库、缓存、消息队列、向量数据库、认证、异常

所有微服务通过此包导入公共能力，避免重复代码。
每个模块提供全局单例 + FastAPI 依赖注入函数。

使用示例：
  from common.config import get_settings
  from common.database import get_db
  from common.redis_client import get_redis
  from common.auth import get_current_user
  from common.exceptions import NotFoundException
"""
__version__ = "1.0.0"

from .config import Settings, get_settings
from .database import DatabaseManager, get_db
from .redis_client import RedisClient, get_redis
from .rabbitmq_client import RabbitMQClient, get_rabbitmq
from .milvus_client import MilvusClient, get_milvus
from .auth import create_access_token, verify_token, get_current_user
from .models import BaseModel, User, ApiKey
from .exceptions import AppException, NotFoundException, ValidationException

__all__ = [
    "Settings", "get_settings",
    "DatabaseManager", "get_db",
    "RedisClient", "get_redis",
    "RabbitMQClient", "get_rabbitmq",
    "MilvusClient", "get_milvus",
    "create_access_token", "verify_token", "get_current_user",
    "BaseModel", "User", "ApiKey",
    "AppException", "NotFoundException", "ValidationException",
]
