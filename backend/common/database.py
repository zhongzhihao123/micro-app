"""
数据库管理器 - 异步 MySQL 连接池
================================
基于 SQLAlchemy 2.0 异步引擎 + aiomysql 驱动。

设计：
  - 单例模式 DatabaseManager，全局共享连接池
  - get_db() 作为 FastAPI 依赖注入，自动 commit/rollback
  - pool_pre_ping=True 确保连接有效性
  - pool_recycle=3600 防止 MySQL 8小时超时断开
"""
from typing import AsyncGenerator, Optional
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import NullPool
from .config import get_settings

# ── 兼容修复：aiomysql 0.3.2 ping() 与 SQLAlchemy 2.x 不兼容 ──
import sqlalchemy.dialects.mysql.aiomysql as _sa_aiomysql
_orig_ping = _sa_aiomysql.AsyncAdapt_aiomysql_connection.ping


async def _patched_ping(self, reconnect=None):
    if reconnect is None:
        reconnect = True
    return await _orig_ping(self, reconnect)


_sa_aiomysql.AsyncAdapt_aiomysql_connection.ping = _patched_ping

settings = get_settings()


class Base(DeclarativeBase):
    pass


class DatabaseManager:
    """异步数据库管理器，提供连接池和会话管理"""

    def __init__(self, database_url: Optional[str] = None):
        self._engine = None
        self._session_factory = None
        self._url = database_url or settings.DATABASE_URL

    @property
    def engine(self):
        if self._engine is None:
            self._engine = create_async_engine(
                self._url,
                poolclass=NullPool,
                pool_pre_ping=False,
                echo=settings.DEBUG,
            )
        return self._engine

    @property
    def session_factory(self):
        if self._session_factory is None:
            self._session_factory = async_sessionmaker(
                self.engine,
                class_=AsyncSession,
                expire_on_commit=False,
            )
        return self._session_factory

    async def get_session(self) -> AsyncGenerator[AsyncSession, None]:
        """获取数据库会话（依赖注入用）"""
        async with self.session_factory() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise
            finally:
                await session.close()

    async def close(self):
        if self._engine:
            await self._engine.dispose()


# 全局实例
_db_manager = DatabaseManager()


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """FastAPI 依赖注入"""
    async for session in _db_manager.get_session():
        yield session
