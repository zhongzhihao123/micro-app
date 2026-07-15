"""
数据模型 - SQLAlchemy ORM 基类
==============================
定义所有微服务共享的基础模型。

模型层级：
  BaseModel（抽象基类）
  ├── id: CHAR(36) UUID 主键
  ├── created_at: 自动创建时间
  ├── updated_at: 自动更新时间
  └── to_dict(): 转换为字典

  User: 用户表（username, email, hashed_password, role, is_active）
  ApiKey: API Key 表（user_id, key_hash, name, expires_at）

各微服务的业务表在 infrastructure/mysql/init.sql 中定义。
"""
import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Boolean, DateTime, func
from .database import Base


def gen_uuid():
    """生成 UUID 字符串（MySQL 兼容）"""
    return str(uuid.uuid4())


class BaseModel(Base):
    """所有模型的抽象基类"""
    __abstract__ = True

    id = Column(String(36), primary_key=True, default=gen_uuid)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    def to_dict(self) -> dict:
        """转换为字典"""
        return {
            column.name: getattr(self, column.name)
            for column in self.__table__.columns
        }


class User(BaseModel):
    """用户模型"""
    __tablename__ = "users"

    username = Column(String(100), unique=True, nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    role = Column(String(20), default="user")
    is_active = Column(Boolean, default=True)


class ApiKey(BaseModel):
    """API Key 模型"""
    __tablename__ = "api_keys"

    user_id = Column(String(36), nullable=False, index=True)
    key_hash = Column(String(255), unique=True, nullable=False)
    name = Column(String(100), nullable=False)
    is_active = Column(Boolean, default=True)
    last_used_at = Column(DateTime(timezone=True), nullable=True)
    expires_at = Column(DateTime(timezone=True), nullable=True)
