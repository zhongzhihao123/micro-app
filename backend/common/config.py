"""
全局配置管理
===========
基于 pydantic-settings，所有配置支持：
1. 环境变量覆盖（前缀无，大小写敏感）
2. .env 文件加载
3. 类型验证与默认值

配置分类：
  - 应用基础：APP_NAME, APP_VERSION, ENV, DEBUG, SECRET_KEY
  - 数据库：DATABASE_URL, DATABASE_POOL_SIZE, DATABASE_MAX_OVERFLOW
  - Redis：REDIS_URL, REDIS_POOL_SIZE
  - RabbitMQ：RABBITMQ_URL, RABBITMQ_PREFETCH_COUNT
  - Milvus：MILVUS_HOST, MILVUS_PORT, MILVUS_COLLECTION_PREFIX
  - LLM：OPENAI_API_KEY, OPENAI_BASE_URL, LLM_MODEL, EMBEDDING_MODEL, EMBEDDING_DIM
  - JWT：JWT_ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES, REFRESH_TOKEN_EXPIRE_DAYS
  - 服务发现：NLP_SERVICE_URL, RECOMMEND_SERVICE_URL, CV_SERVICE_URL, MLOPS_SERVICE_URL
"""
import os
from functools import lru_cache
from typing import Optional
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """应用配置，支持环境变量和 .env 文件"""

    # 应用
    APP_NAME: str = "AI System Platform"
    APP_VERSION: str = "1.0.0"
    ENV: str = "development"
    DEBUG: bool = True
    SECRET_KEY: str = "aisys-secret-key-change-in-production-2024"

    # 数据库
    DATABASE_URL: str = "mysql+aiomysql://aisys:aisys123@localhost:3307/ai_platform"
    DATABASE_POOL_SIZE: int = 20
    DATABASE_MAX_OVERFLOW: int = 10

    # Redis
    REDIS_URL: str = "redis://:aisys_redis_2024@localhost:6379/0"
    REDIS_POOL_SIZE: int = 10

    # RabbitMQ
    RABBITMQ_URL: str = "amqp://aisys:aisys123@localhost:5672/ai_platform"
    RABBITMQ_PREFETCH_COUNT: int = 10

    # Milvus
    MILVUS_HOST: str = "localhost"
    MILVUS_PORT: int = 19530
    MILVUS_COLLECTION_PREFIX: str = "aisys_"

    # LLM
    OPENAI_API_KEY: Optional[str] = None
    OPENAI_BASE_URL: str = "https://api.openai.com/v1"
    LLM_MODEL: str = "gpt-4o-mini"
    EMBEDDING_MODEL: str = "text-embedding-3-small"
    EMBEDDING_DIM: int = 1536

    # 认证
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # 文件上传
    MAX_UPLOAD_SIZE_MB: int = 50
    UPLOAD_DIR: str = "./uploads"

    # 服务发现
    NLP_SERVICE_URL: str = "http://nlp-service:8000"
    RECOMMEND_SERVICE_URL: str = "http://recommend-service:8000"
    CV_SERVICE_URL: str = "http://cv-service:8000"
    MLOPS_SERVICE_URL: str = "http://mlops-service:8000"

    # 监控
    PROMETHEUS_ENABLED: bool = True
    LOG_LEVEL: str = "INFO"

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "case_sensitive": True,
    }


@lru_cache()
def get_settings() -> Settings:
    return Settings()
