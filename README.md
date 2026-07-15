# AI System Platform

企业级 AI 平台，基于微前端 + 微服务架构，集成 NLP 知识库、推荐系统、计算机视觉、MLOps 四大 AI 能力模块。

## 技术栈

| 层级 | 技术 | 说明 |
|------|------|------|
| 前端基座 | Vue3 + TypeScript + Vite + Element Plus | qiankun 微前端主应用 |
| 子应用 | Vue3 + vite-plugin-qiankun | 4 个独立子应用 |
| 后端 | Python FastAPI | 异步微服务 |
| 数据库 | MySQL 8.4 | 业务数据存储 |
| 缓存 | Redis 7 | 缓存 & 限流 |
| 消息队列 | RabbitMQ 3.13 | 异步任务分发 |
| 向量数据库 | Milvus 2.4 | 语义检索 |
| 对象存储 | MinIO | 文件存储（Milvus 依赖） |
| 服务注册 | etcd | Milvus 元数据 |
| LLM | OpenAI 兼容 API | 大模型 & Embedding |

## 项目结构

```
AI-system/
├── README.md                          # 项目文档（本文件）
├── Makefile                           # 一键命令（make dev / make up / make data）
├── docker-compose.yml                 # Docker 编排（MySQL, Redis, RabbitMQ, Milvus 等）
├── .env.example                       # 环境变量模板
│
├── backend/                           # ===== 后端 =====
│   ├── requirements.txt               # Python 依赖
│   ├── common/                        # 共享库（所有微服务复用）
│   │   ├── __init__.py                # 包说明
│   │   ├── config.py                  # 全局配置（环境变量 + 默认值）
│   │   ├── database.py                # MySQL 异步连接池（aiomysql + SQLAlchemy）
│   │   ├── models.py                  # ORM 基础模型（User, ApiKey）
│   │   ├── auth.py                    # JWT 认证（签发/验证/依赖注入）
│   │   ├── redis_client.py            # Redis 客户端（缓存/限流/分布式锁）
│   │   ├── rabbitmq_client.py         # RabbitMQ 客户端（发布/消费）
│   │   ├── milvus_client.py           # Milvus 向量数据库客户端
│   │   └── exceptions.py              # 统一异常类（404/401/403/422/429/503）
│   │
│   ├── gateway/                       # API 网关（端口 8000）
│   │   ├── main.py                    # 路由分发、JWT 端点、CORS、请求日志
│   │   └── Dockerfile                 # 网关 Docker 镜像
│   │
│   └── services/                      # 4 个微服务
│       ├── nlp/                       # NLP 知识库问答服务（端口 8001）
│       │   ├── main.py                # 文档上传、语义检索、RAG 问答、集合管理
│       │   └── Dockerfile
│       ├── recommend/                 # 推荐系统服务（端口 8002）
│       │   ├── main.py                # 5种推荐算法、行为记录、A/B测试
│       │   └── Dockerfile
│       ├── cv/                        # 计算机视觉服务（端口 8003）
│       │   ├── main.py                # 检测/分类/OCR/人脸分析
│       │   └── Dockerfile
│       └── mlops/                     # MLOps 平台服务（端口 8004）
│           ├── main.py                # 模型注册/训练/实验/部署/监控
│           └── Dockerfile
│
├── frontend/                          # ===== 前端 =====
│   ├── base/                          # 基座应用（端口 3000）
│   │   ├── package.json
│   │   ├── vite.config.ts             # Vite 配置（API 代理 + @ 别名）
│   │   ├── index.html
│   │   ├── public/vite.svg
│   │   └── src/
│   │       ├── main.ts                # 入口：Pinia/Router/qiankun 注册
│   │       ├── App.vue                # 布局：侧边栏 + 顶栏 + 子应用容器
│   │       ├── router/index.ts        # 路由：首页 + 4个子应用路由
│   │       └── views/
│   │           ├── Home.vue           # 平台首页（仪表盘）
│   │           └── MicroAppPlaceholder.vue  # 子应用占位组件
│   │
│   ├── sub-nlp/                       # NLP 子应用（端口 3001）
│   │   ├── vite.config.ts
│   │   └── src/
│   │       ├── main.ts                # qiankun 生命周期钩子
│   │       ├── router/index.ts        # 路由：知识库/聊天/集合管理
│   │       └── views/
│   │           ├── KnowledgeBase.vue  # 文档上传 & 管理
│   │           ├── Chat.vue           # RAG 对话（含来源引用）
│   │           └── Collections.vue    # 知识库集合管理
│   │
│   ├── sub-recommend/                 # 推荐子应用（端口 3002）
│   │   ├── vite.config.ts
│   │   └── src/
│   │       ├── main.ts
│   │       ├── router/index.ts
│   │       └── views/
│   │           ├── Dashboard.vue      # 推荐仪表盘（KPI + 图表）
│   │           ├── Items.vue          # 商品/内容管理
│   │           ├── Behavior.vue       # 用户行为日志
│   │           └── ABTest.vue         # A/B 实验管理
│   │
│   ├── sub-cv/                        # CV 子应用（端口 3003）
│   │   ├── vite.config.ts
│   │   └── src/
│   │       ├── main.ts
│   │       ├── router/index.ts
│   │       └── views/
│   │           ├── Detect.vue         # 目标检测
│   │           ├── Classify.vue       # 图像分类
│   │           ├── OCR.vue            # 文字识别
│   │           └── FaceAnalysis.vue   # 人脸分析
│   │
│   └── sub-mlops/                     # MLOps 子应用（端口 3004）
│       ├── vite.config.ts
│       └── src/
│           ├── main.ts
│           ├── router/index.ts
│           └── views/
│               ├── Models.vue         # 模型注册表
│               ├── Training.vue       # 训练任务管理
│               ├── Experiments.vue    # A/B 实验
│               └── Monitor.vue        # 监控仪表盘
│
├── infrastructure/                    # ===== 基础设施 =====
│   ├── mysql/
│   │   └── init.sql                   # MySQL 初始化（建表 + 索引 + 默认管理员）
│   ├── rabbitmq/
│   │   └── definitions.json           # RabbitMQ 定义（Exchange/Queue/Binding/DLQ）
│   └── k8s/
│       └── deployment.yaml            # Kubernetes 部署配置
│
└── data/                              # ===== 数据 =====
    ├── generate_data.py               # 数据生成脚本（9类数据，16850+条）
    ├── users.json                     # 500 用户
    ├── items.json                     # 1000 商品
    ├── behaviors.json                 # 10000 用户行为
    ├── documents.json                 # 50 知识库文档
    ├── cv_tasks.json                  # 200 CV 任务
    ├── models.json                    # 30 模型
    ├── training_jobs.json             # 50 训练任务
    ├── experiments.json               # 20 A/B 实验
    ├── inference_logs.json            # 5000 推理日志
    └── summary.json                   # 数据汇总
```

## 快速启动

### 前置要求

- Docker Desktop（已安装并运行）
- Python 3.11+
- Node.js 18+
- npm 9+

### 1. 配置环境变量

```bash
cp .env.example .env
# 编辑 .env，设置 OPENAI_API_KEY（可选，不设置则使用模拟数据）
```

### 2. 一键启动

```bash
# 安装所有依赖
make install

# 启动基础设施 + 后端网关
make dev

# 启动前端基座
cd frontend/base && npm install && npx vite --port 3000 --host 0.0.0.0

# 启动 4 个子应用（各开一个终端）
cd frontend/sub-nlp && npx vite --port 3001 --host 0.0.0.0
cd frontend/sub-recommend && npx vite --port 3002 --host 0.0.0.0
cd frontend/sub-cv && npx vite --port 3003 --host 0.0.0.0
cd frontend/sub-mlops && npx vite --port 3004 --host 0.0.0.0
```

### 3. 访问

| 服务 | 地址 |
|------|------|
| 前端平台 | http://localhost:3000 |
| API 文档 (Swagger) | http://localhost:8000/api/docs |
| RabbitMQ 管理 | http://localhost:15672 (aisys/aisys123) |

### 4. 默认账号

- 用户名：`admin`
- 密码：`admin123`

### 5. 生成模拟数据

```bash
make data
```

## Makefile 命令

| 命令 | 说明 |
|------|------|
| `make install` | 安装 Python + Node 依赖 |
| `make dev` | 启动基础设施容器 (MySQL, Redis, RabbitMQ, etcd, MinIO, Milvus) |
| `make up` | 启动全部服务（含后端微服务容器） |
| `make down` | 停止所有服务 |
| `make restart` | 重启所有服务 |
| `make logs` | 查看所有容器日志 |
| `make status` | 查看容器运行状态 |
| `make data` | 重新生成模拟数据 |
| `make clean` | 清理容器和数据卷 |

## 架构说明

### 微前端架构

```
┌─────────────────────────────────────────────────┐
│              Base App (localhost:3000)            │
│  ┌──────────┐  ┌──────────────────────────────┐  │
│  │ Sidebar  │  │   #sub-app-container          │  │
│  │          │  │   ┌────────────────────────┐  │  │
│  │ 首页     │  │   │  sub-nlp (3001)        │  │  │
│  │ NLP      │──│   │  sub-recommend (3002)  │  │  │
│  │ 推荐     │  │   │  sub-cv (3003)         │  │  │
│  │ CV       │  │   │  sub-mlops (3004)      │  │  │
│  │ MLOps    │  │   └────────────────────────┘  │  │
│  └──────────┘  └──────────────────────────────┘  │
└─────────────────────────────────────────────────┘
```

- 基座使用 **qiankun** 管理子应用生命周期
- 子应用通过 `vite-plugin-qiankun` 导出 `mount/unmount/update` 钩子
- `experimentalStyleIsolation: true` 实现 CSS 隔离
- 路由匹配：`/nlp/*` → sub-nlp，`/recommend/*` → sub-recommend 等

### 微服务架构

```
Browser (localhost:3000)
    │
    ▼
API Gateway (localhost:8000)
    ├── /api/auth/*     → JWT 认证
    ├── /api/nlp/*      → NLP 服务 (8001)
    ├── /api/recommend/* → 推荐服务 (8002)
    ├── /api/cv/*       → CV 服务 (8003)
    └── /api/mlops/*    → MLOps 服务 (8004)
            │
            ├── MySQL (3307)    — 业务数据
            ├── Redis (6379)    — 缓存/限流
            ├── RabbitMQ (5672) — 异步任务
            └── Milvus (19530)  — 向量检索
```

### RAG 问答流程

```
用户提问
  → Embedding 模型（OpenAI text-embedding-3-small）
  → Milvus 向量检索（COSINE 相似度 Top-K）
  → 拼接上下文 Prompt
  → LLM 生成回答（OpenAI GPT-4o-mini）
  → 返回答案 + 引用来源
```

### 推荐系统流程

```
用户行为（view/click/like/purchase）
  → RabbitMQ 异步消费
  → 行为权重计算
  → 5种算法并行计算
  → 结果融合排序
  → Redis 缓存（TTL 5分钟）
  → 返回推荐列表
```

## 各文件详解

### 后端核心

#### `backend/common/config.py` — 全局配置
基于 pydantic-settings，所有配置可从环境变量覆盖。包含数据库连接、Redis、RabbitMQ、Milvus、OpenAI API、JWT 等所有配置项。

#### `backend/common/database.py` — 数据库管理器
单例模式 MySQL 异步连接池。`get_db()` 作为 FastAPI 依赖注入，自动管理事务 commit/rollback。

#### `backend/common/models.py` — ORM 模型
定义 `BaseModel`（UUID 主键 + 自动时间戳）和 `User`、`ApiKey` 两个基础模型。业务表在 `infrastructure/mysql/init.sql`。

#### `backend/common/auth.py` — JWT 认证
- `create_access_token()` — 签发 Access Token（60分钟过期）
- `get_current_user()` — FastAPI 依赖，从 Header 提取用户
- `get_current_admin()` — 要求 admin 角色

#### `backend/common/redis_client.py` — Redis 客户端
- `get/set` — 基础 KV 操作
- `check_rate_limit()` — 滑动窗口限流
- `acquire_lock/release_lock` — 分布式锁

#### `backend/common/rabbitmq_client.py` — 消息队列
- `publish()` — 发布消息到指定 routing_key
- `consume()` — 消费消息并回调
- 快捷方法：`submit_document_processing`、`submit_embedding_task`、`submit_cv_task`、`submit_training_job`

#### `backend/common/milvus_client.py` — 向量数据库
- `create_collection()` — 创建向量集合（IVF_FLAT + COSINE）
- `insert_vectors()` — 批量写入 embedding
- `search()` — Top-K 相似度检索

#### `backend/common/exceptions.py` — 异常类
统一的异常层次：`AppException(500)` → `NotFoundException(404)` / `UnauthorizedException(401)` / `ForbiddenException(403)` / `ValidationException(422)` / `RateLimitException(429)` / `ServiceUnavailableException(503)`

### 后端服务

#### `backend/gateway/main.py` — API 网关
- **路由代理**：将 `/api/{service}/*` 转发到对应微服务
- **认证端点**：`/api/auth/login`、`/api/auth/register`、`/api/auth/me`
- **中间件**：CORS、GZip 压缩、请求计时（X-Process-Time）
- **异常处理**：全局捕获并返回统一 JSON 错误格式

#### `backend/services/nlp/main.py` — NLP 知识库
- **文档上传**：接收文件 → RabbitMQ 异步处理
- **语义搜索**：Embedding 查询 → Milvus 向量检索
- **RAG 问答**：检索相关文档 → 拼接 Prompt → LLM 生成
- **流式问答**：SSE 流式输出（`text/event-stream`）

#### `backend/services/recommend/main.py` — 推荐系统
- **5种算法**：协同过滤 / 内容推荐 / 混合推荐 / 热门 / 最新
- **行为记录**：异步写入 RabbitMQ
- **A/B 测试**：流量分配 + 分组推荐
- **缓存**：Redis 缓存推荐结果

#### `backend/services/cv/main.py` — 计算机视觉
- **目标检测**：YOLO 模拟，返回 bbox + label + confidence
- **图像分类**：ResNet 模拟，返回 Top-5 分类
- **OCR**：PaddleOCR 模拟，返回文字 + 位置
- **人脸分析**：RetinaFace 模拟，返回年龄/性别/情绪
- **综合分析**：一次请求执行多个 CV 任务

#### `backend/services/mlops/main.py` — MLOps 平台
- **模型注册表**：CRUD + 状态流转（development → staging → production → archived）
- **训练任务**：提交到 RabbitMQ 异步执行
- **A/B 实验**：创建、流量分配、指标对比
- **部署**：部署到 staging/production 环境
- **监控**：推理日志、漂移检测、资源仪表盘

### 前端核心

#### `frontend/base/src/main.ts` — 基座入口
初始化 Vue3 + Pinia + Router + Element Plus，注册 4 个子应用到 qiankun，配置生命周期钩子，启动 CSS 沙箱隔离。

#### `frontend/base/src/App.vue` — 基座布局
侧边栏导航 + 顶部栏 + `#sub-app-container` 子应用挂载区。侧边栏菜单项对应 4 个子应用路由。

#### `frontend/base/vite.config.ts` — 基座 Vite 配置
- `@` 别名 → `src/`
- API 代理 `/api` → `http://localhost:8000`

### 子应用

每个子应用结构相同：
- `main.ts` — qiankun 生命周期钩子（`renderWithQiankun`）
- `router/index.ts` — 子应用内部路由
- `views/*.vue` — 业务页面
- `vite.config.ts` — Vite + qiankun 插件配置

### 基础设施

#### `docker-compose.yml`
编排 6 个基础设施容器：MySQL、Redis、RabbitMQ、etcd、MinIO、Milvus。健康检查 + 启动依赖顺序。

#### `infrastructure/mysql/init.sql`
建表语句（users, api_keys, knowledge_documents, document_chunks, conversations, messages, items, user_behaviors, recommendations, cv_tasks, detection_results, models, training_jobs, ab_experiments, inference_logs）+ 索引 + 默认管理员。

#### `infrastructure/rabbitmq/definitions.json`
RabbitMQ 定义：`ai.tasks`（任务分发）、`ai.events`（事件通知）、`ai.dlq`（死信队列）三个 Topic Exchange，以及对应的 Queue 和 Binding。

### 数据生成

#### `data/generate_data.py`
生成 9 类共 16850+ 条模拟数据，`random.seed(42)` 保证可复现。

## API 接口速查

### 认证
| 方法 | 路径 | 说明 |
|------|------|------|
| POST | /api/auth/login | 用户登录 |
| POST | /api/auth/register | 用户注册 |
| GET | /api/auth/me | 当前用户信息 |

### NLP
| 方法 | 路径 | 说明 |
|------|------|------|
| POST | /api/nlp/documents/upload | 上传文档 |
| POST | /api/nlp/search | 语义搜索 |
| POST | /api/nlp/chat | RAG 问答 |
| POST | /api/nlp/chat/stream | 流式问答 |
| GET | /api/nlp/collections | 集合列表 |

### 推荐
| 方法 | 路径 | 说明 |
|------|------|------|
| POST | /api/recommend/recommend | 个性化推荐 |
| POST | /api/recommend/behavior | 记录行为 |
| POST | /api/recommend/batch | 批量推荐 |
| POST | /api/recommend/ab-test/assign | A/B 分配 |

### CV
| 方法 | 路径 | 说明 |
|------|------|------|
| POST | /api/cv/detect | 目标检测 |
| POST | /api/cv/classify | 图像分类 |
| POST | /api/cv/ocr | 文字识别 |
| POST | /api/cv/face | 人脸分析 |
| POST | /api/cv/analyze | 综合分析 |

### MLOps
| 方法 | 路径 | 说明 |
|------|------|------|
| GET/POST | /api/mlops/models | 模型注册表 |
| GET/POST | /api/mlops/training/jobs | 训练任务 |
| GET/POST | /api/mlops/experiments | A/B 实验 |
| POST | /api/mlops/deploy | 模型部署 |
| GET | /api/mlops/monitoring/dashboard | 监控仪表盘 |
| GET | /api/mlops/monitoring/drift/:id | 漂移检测 |

## 环境变量

| 变量 | 默认值 | 说明 |
|------|--------|------|
| DATABASE_URL | mysql+aiomysql://aisys:aisys123@localhost:3307/ai_platform | 数据库连接 |
| REDIS_URL | redis://:aisys_redis_2024@localhost:6379/0 | Redis 连接 |
| RABBITMQ_URL | amqp://aisys:aisys123@localhost:5672/ai_platform | RabbitMQ 连接 |
| MILVUS_HOST | localhost | Milvus 地址 |
| OPENAI_API_KEY | (空) | OpenAI API Key |
| OPENAI_BASE_URL | https://api.openai.com/v1 | OpenAI API 地址 |
| LLM_MODEL | gpt-4o-mini | 对话模型 |
| EMBEDDING_MODEL | text-embedding-3-small | Embedding 模型 |
| SECRET_KEY | (自动生成) | JWT 签名密钥 |
| ACCESS_TOKEN_EXPIRE_MINUTES | 60 | Access Token 有效期（分钟） |

## 生产部署

```bash
# 构建 Docker 镜像
docker compose build

# 推送镜像到仓库
docker tag aisys-gateway your-registry/aisys-gateway:latest
docker push your-registry/aisys-gateway:latest

# K8s 部署
kubectl apply -f infrastructure/k8s/deployment.yaml
```

## License

MIT
