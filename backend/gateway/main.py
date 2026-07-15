"""
AI System Platform - API 网关
==============================
统一入口 | 路由分发 | JWT 认证 | 请求日志 | 服务代理

职责：
1. 接收所有前端请求，转发到对应微服务
2. JWT Token 签发与验证（/api/auth/*）
3. 健康检查 & API 信息端点
4. CORS 跨域、GZip 压缩、请求计时
"""
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse
import httpx
import time
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from common.config import get_settings
from common.exceptions import AppException
from common.redis_client import get_redis
from common.database import _db_manager
from sqlalchemy import text
settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理：启动时连接 Redis，关闭时释放连接"""
    # Startup: 初始化 Redis 连接池
    redis = await get_redis()
    await redis.connect()
    print(f"🚀 {settings.APP_NAME} v{settings.APP_VERSION} Gateway started")
    yield
    # Shutdown: 释放 Redis 连接
    await redis.disconnect()
    print("👋 Gateway shutting down")


# FastAPI 应用实例
# - /api/docs → Swagger UI 交互式文档
# - /api/redoc → ReDoc 文档
# - /api/openapi.json → OpenAPI JSON Schema
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
    lifespan=lifespan,
)

# ---- Middleware ----

# CORS：允许前端跨域访问（开发环境开放所有来源）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# GZip：压缩大于1KB的响应体，减少网络传输
app.add_middleware(GZipMiddleware, minimum_size=1000)


@app.middleware("http")
async def request_middleware(request: Request, call_next):
    """请求计时中间件：记录每个 API 请求的处理时间，写入 X-Process-Time 响应头"""
    start_time = time.time()

    # 健康检查不记录计时
    if request.url.path == "/api/health":
        return await call_next(request)

    response = await call_next(request)

    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(round(process_time * 1000, 2))
    response.headers["X-API-Version"] = settings.APP_VERSION

    return response


# ---- Exception Handlers ----

# 自定义业务异常处理：AppException 及其子类
@app.exception_handler(AppException)
async def app_exception_handler(request: Request, exc: AppException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.message,
            "detail": exc.detail,
            "status_code": exc.status_code,
        },
    )


# 兜底异常处理：未预期的服务器错误
@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "detail": str(exc) if settings.DEBUG else None,
            "status_code": 500,
        },
    )


# ---- Health & Info ----

# 健康检查端点：K8s/Docker Compose 用于检测服务是否存活
@app.get("/api/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "gateway",
        "version": settings.APP_VERSION,
        "environment": settings.ENV,
    }


# API 信息端点：列出所有可用的微服务路由
@app.get("/api/info")
async def api_info():
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "services": {
            "nlp": {"url": "/api/nlp", "description": "NLP知识库问答"},
            "recommend": {"url": "/api/recommend", "description": "智能推荐系统"},
            "cv": {"url": "/api/cv", "description": "计算机视觉"},
            "mlops": {"url": "/api/mlops", "description": "MLOps平台"},
        },
    }


# ---- Auth Routes ----
# JWT 认证相关路由：登录、注册、获取当前用户信息

from common.auth import (
    hash_password,
    verify_password,
    create_access_token,
    create_refresh_token,
    get_current_user,
)

from pydantic import BaseModel, EmailStr


class LoginRequest(BaseModel):
    username: str
    password: str


class RegisterRequest(BaseModel):
    username: str
    email: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


@app.post("/api/auth/login", response_model=TokenResponse, tags=["Auth"])
async def login(request: LoginRequest):
    """用户登录：验证用户名密码，签发 JWT access_token + refresh_token"""
    # 简化版：直接返回 token（生产环境需查询数据库验证）
    if request.username == "admin" and request.password == "admin123":
        access_token = create_access_token(
            user_id="admin-id",
            username="admin",
            role="admin",
        )
        refresh_token = create_refresh_token(user_id="admin-id")
        return TokenResponse(access_token=access_token, refresh_token=refresh_token)
    raise AppException("Invalid credentials", status_code=401)


@app.post("/api/auth/register", tags=["Auth"])
async def register(request: RegisterRequest):
    """用户注册：创建新用户账号（需对接数据库）"""
    return {"message": "Registration endpoint - integrate with database", "username": request.username}


@app.get("/api/auth/me", tags=["Auth"])
async def get_me(current_user: dict = Depends(get_current_user)):
    """获取当前用户信息：从 JWT Token 中解析用户身份"""
    return {
        "user_id": current_user["sub"],
        "username": current_user["username"],
        "role": current_user["role"],
    }


# ---- Database Admin Routes ----
# 数据库管理面板后端 API：查看表、表结构、分页查询、自定义 SQL

from pydantic import Field


class QueryRequest(BaseModel):
    sql: str
    limit: int = Field(default=500, le=5000)


@app.get("/api/dbadmin/tables", tags=["DB Admin"])
async def db_list_tables():
    """获取所有业务表列表（排除系统表）"""
    async with _db_manager.engine.connect() as conn:
        result = await conn.execute(
            text("""
                SELECT TABLE_NAME FROM information_schema.TABLES
                WHERE TABLE_SCHEMA = DATABASE()
                  AND TABLE_TYPE = 'BASE TABLE'
                  AND TABLE_NAME NOT LIKE '\\_\\_%'
                ORDER BY TABLE_NAME
            """)
        )
        tables = [row[0] for row in result]
    return {"tables": tables}


@app.get("/api/dbadmin/tables/{table_name}", tags=["DB Admin"])
async def db_table_schema(table_name: str):
    """获取指定表的字段结构"""
    async with _db_manager.engine.connect() as conn:
        result = await conn.execute(
            text("""
                SELECT COLUMN_NAME AS `Field`,
                       COLUMN_TYPE AS `Type`,
                       IS_NULLABLE AS `Null`,
                       COLUMN_KEY AS `Key`,
                       COLUMN_DEFAULT AS `Default`,
                       EXTRA AS `Extra`
                FROM information_schema.COLUMNS
                WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = :tbl
                ORDER BY ORDINAL_POSITION
            """),
            {"tbl": table_name},
        )
        columns = [dict(row._mapping) for row in result]
    return {"table": table_name, "columns": columns}


@app.get("/api/dbadmin/tables/{table_name}/data", tags=["DB Admin"])
async def db_table_data(table_name: str, page: int = 1, page_size: int = 50):
    """获取表的分页数据"""
    offset = (page - 1) * page_size

    async with _db_manager.engine.connect() as conn:
        # 总数
        count_result = await conn.execute(
            text(f"SELECT COUNT(*) FROM `{table_name}`")
        )
        total = count_result.scalar() or 0

        # 列名
        col_result = await conn.execute(
            text("""
                SELECT COLUMN_NAME FROM information_schema.COLUMNS
                WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = :tbl
                ORDER BY ORDINAL_POSITION
            """),
            {"tbl": table_name},
        )
        columns = [row[0] for row in col_result]

        # 数据
        data_result = await conn.execute(
            text(f"SELECT * FROM `{table_name}` LIMIT :lim OFFSET :off"),
            {"lim": page_size, "off": offset},
        )
        rows = [dict(row._mapping) for row in data_result]

    return {
        "table": table_name,
        "columns": columns,
        "rows": rows,
        "total": total,
        "page": page,
        "page_size": page_size,
    }


@app.post("/api/dbadmin/query", tags=["DB Admin"])
async def db_run_query(req: QueryRequest):
    """执行自定义 SQL 查询（只允许 SELECT/EXPLAIN）"""
    sql_upper = req.sql.strip().upper()

    allowed_prefixes = ("SELECT", "EXPLAIN", "DESC", "DESCRIBE", "SHOW")
    if not any(sql_upper.startswith(p) for p in allowed_prefixes):
        raise AppException("只允许执行查询语句 (SELECT/EXPLAIN/DESC/SHOW)", status_code=403)

    async with _db_manager.engine.connect() as conn:
        try:
            result = await conn.execute(text(req.sql))
            if result.returns_rows:
                columns = list(result.keys())
                rows = [dict(row._mapping) for row in result]
                return {"columns": columns, "rows": rows, "row_count": len(rows)}
            else:
                return {"affected": result.rowcount}
        except Exception as e:
            raise AppException(f"SQL 执行错误: {str(e)}", status_code=400)


# ---- Service Proxy Routes ----
# 微服务路由表：将 /api/{service}/* 请求代理转发到对应的内部微服务

SERVICE_ROUTES = {
    "nlp": settings.NLP_SERVICE_URL,
    "recommend": settings.RECOMMEND_SERVICE_URL,
    "cv": settings.CV_SERVICE_URL,
    "mlops": settings.MLOPS_SERVICE_URL,
}


@app.api_route("/api/{service}/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
async def proxy_to_service(service: str, path: str, request: Request):
    """
    微服务代理：将请求转发到对应的内部微服务
    - 支持 GET/POST/PUT/DELETE/PATCH 方法
    - 透传请求头、Body 和查询参数
    - 服务不可用时返回 503
    """
    if service not in SERVICE_ROUTES:
        raise AppException(f"Unknown service: {service}", status_code=404)

    target_url = f"{SERVICE_ROUTES[service]}/api/{path}"
    body = await request.body() if request.method in ("POST", "PUT", "PATCH") else None

    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            response = await client.request(
                method=request.method,
                url=target_url,
                headers={k: v for k, v in request.headers.items() if k.lower() not in ("host", "content-length")},
                content=body,
                params=dict(request.query_params),
            )
            return JSONResponse(
                content=response.json() if response.headers.get("content-type", "").startswith("application/json") else {"data": response.text},
                status_code=response.status_code,
            )
        except httpx.ConnectError:
            raise AppException(f"Service {service} is unavailable", status_code=503)
        except Exception as e:
            raise AppException(f"Proxy error: {str(e)}", status_code=502)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
