# AI System Platform

企业级 AI 平台，基于微前端 + 微服务架构，集成 NLP 知识库、推荐系统、计算机视觉、MLOps 四大 AI 能力模块，以及 OA 审批系统、CI/CD 流水线、SQL 数据管理、系统管理等企业级功能。

## 技术栈

| 层级 | 技术 | 说明 |
|------|------|------|
| 前端基座 | Vue3 + TypeScript + Vite + Element Plus | qiankun 微前端主应用（macOS/Windows 桌面风格） |
| 子应用 | Vue3 + vite-plugin-qiankun | 8 个独立子应用 |
| Python 后端 | Python FastAPI | 4 个 AI 微服务 |
| Java 后端 | Spring Boot 3.2 + Spring Cloud Gateway | 6 个 Java 微服务 + 统一网关 |
| 数据库 | MySQL 8.0 | 业务数据存储 |
| 缓存 | Redis 7 | 缓存 & 限流 |
| 消息队列 | RabbitMQ 3.13 | 异步任务分发 |
| 向量数据库 | Milvus 2.4 | 语义检索 |
| 对象存储 | MinIO | 文件存储（Milvus 依赖） |
| LLM | OpenAI 兼容 API | 大模型 & Embedding |
| 企业微信 | WeCom Webhook | 审批通知推送 |

## 项目结构

```
AI-system/
├── README.md                          # 项目文档（本文件）
├── Makefile                           # 一键命令
├── docker-compose.yml                 # Docker 编排
├── .env.example                       # 环境变量模板
│
├── backend/                           # ===== Python 后端 =====
│   ├── requirements.txt               # Python 依赖
│   ├── common/                        # 共享库
│   └── services/                      # 4 个 AI 微服务
│       ├── nlp/                       # NLP 知识库问答服务（端口 8001）
│       ├── recommend/                 # 推荐系统服务（端口 8002）
│       ├── cv/                        # 计算机视觉服务（端口 8003）
│       └── mlops/                     # MLOps 平台服务（端口 8004）
│
├── frontend/                          # ===== 前端 =====
│   ├── base/                          # 基座应用（端口 3000）桌面风格
│   ├── sub-nlp/                       # NLP 子应用（端口 3001）
│   ├── sub-recommend/                 # 推荐子应用（端口 3002）
│   ├── sub-cv/                        # CV 子应用（端口 3003）
│   ├── sub-mlops/                     # MLOps 子应用（端口 3004）
│   └── sub-sql/                       # SQL 数据管理（端口 3005）
│
├── java-spring-project/               # ===== Java 后端 =====
│   ├── common/                        # 公共库
│   ├── gateway-service/               # 统一网关（端口 8000）
│   ├── user-service/                  # 用户服务（端口 8101）
│   ├── business-service/              # 业务服务（端口 8102）
│   ├── notification-service/          # 通知服务（端口 8103）
│   ├── cicd-service/                  # CI/CD 服务（端口 8104）
│   └── oa-service/                    # OA 审批服务（端口 8105）
│
├── infrastructure/                    # ===== 基础设施 =====
│   ├── mysql/init.sql                 # MySQL 初始化
│   ├── rabbitmq/definitions.json      # RabbitMQ 定义
│   └── k8s/deployment.yaml            # K8s 部署配置
│
└── data/                              # ===== 数据 =====
    └── generate_data.py               # 数据生成脚本（16850+ 条）
```

## 快速启动

### 前置要求

- Docker Desktop（已安装并运行）
- Python 3.11+
- Node.js 18+
- Java 21+
- Maven 3.9+

### 1. 配置环境变量

```bash
cp .env.example .env
# 编辑 .env，设置 OPENAI_API_KEY（可选）
```

### 2. 启动基础设施

```bash
# 启动 MySQL、Redis、RabbitMQ 等容器
make dev
```

### 3. 启动 Java 后端

```bash
cd java-spring-project

# 编译所有模块
./mvnw clean package -DskipTests

# 启动网关
cd gateway-service && java -jar target/gateway-service-1.0.0-SNAPSHOT.jar &

# 启动各微服务
cd user-service && java -jar target/user-service-1.0.0-SNAPSHOT.jar &
cd business-service && java -jar target/business-service-1.0.0-SNAPSHOT.jar &
cd cicd-service && java -jar target/cicd-service-1.0.0-SNAPSHOT.jar &
cd oa-service && java -jar target/oa-service-1.0.0-SNAPSHOT.jar &
```

### 4. 启动 Python 后端

```bash
cd backend
pip install -r requirements.txt

# 启动 AI 微服务
python services/nlp/main.py &
python services/recommend/main.py &
python services/cv/main.py &
python services/mlops/main.py &
```

### 5. 启动前端

```bash
# 基座
cd frontend/base && npm install && npm run dev &

# 子应用
cd frontend/sub-nlp && npm install && npm run dev &
cd frontend/sub-recommend && npm install && npm run dev &
cd frontend/sub-cv && npm install && npm run dev &
cd frontend/sub-mlops && npm install && npm run dev &
```

### 6. 访问

| 服务 | 地址 |
|------|------|
| 前端平台 | http://localhost:3000 |
| Java 统一网关 | http://localhost:8000 |
| RabbitMQ 管理 | http://localhost:15672 (aisys/aisys123) |

### 7. 登录账号

| 用户名 | 密码 | 角色 |
|--------|------|------|
| admin | admin123 | 管理员（全部权限） |
| zhangsan | test123 | 普通用户 |
| lisi | test123 | 普通用户 |
| wangwu | test123 | 普通用户 |
| zhaoliu | test123 | 普通用户 |

## 前端子应用

### 桌面风格基座

基座采用 macOS/Windows 桌面风格设计：
- 🖥️ 桌面图标（支持权限过滤）
- 📋 任务栏（显示已打开应用、快捷按钮）
- 🪟 窗口管理（拖拽、最大化、最小化）
- 🔐 登录对话框（登录/注册/忘记密码）
- 👤 用户信息弹窗（头像、角色、权限）

### 8 个子应用

| 应用 | 端口 | 权限 | 功能 |
|------|------|------|------|
| 🧠 NLP 知识库 | 3001 | nlp | 文档上传、语义检索、RAG 问答 |
| 🎯 推荐系统 | 3002 | recommend | 推荐算法、行为记录、A/B 测试 |
| 👁️ 计算机视觉 | 3003 | cv | 目标检测、图像分类、OCR、人脸分析 |
| ⚙️ MLOps 平台 | 3004 | mlops | 模型管理、训练任务、监控 |
| 🗄️ SQL 数据 | 3005 | dbadmin | 数据库管理、SQL 查询 |
| 🔐 系统管理 | 3006 | system-manager | 用户管理、权限管理 |
| 🚀 CI/CD 流水线 | 3007 | cicd | 流水线管理、构建历史 |
| 📋 OA 审批 | 3008 | oa | 请假审批、企业微信通知 |

## 后端服务

### Java 微服务架构

```
Browser (localhost:3000)
    │
    ▼
Java 统一网关 (localhost:8000)
    ├── /api/users/**       → 用户服务 (8101)
    ├── /api/admin/**       → 用户服务 (8101)
    ├── /api/business/**    → 业务服务 (8102)
    ├── /api/dbadmin/**     → 业务服务 (8102)
    ├── /api/notifications/** → 通知服务 (8103)
    ├── /api/cicd/**        → CI/CD 服务 (8104)
    ├── /api/oa/**          → OA 审批服务 (8105)
    ├── /api/nlp/**         → Python NLP (8001)
    ├── /api/recommend/**   → Python 推荐 (8002)
    ├── /api/cv/**          → Python CV (8003)
    └── /api/mlops/**       → Python MLOps (8004)
```

### OA 审批系统

#### 功能特性

- ✅ 请假申请（年假、事假、病假、婚假、产假、调休）
- ✅ 审批流程（一级审批，直属领导）
- ✅ 审批人自动匹配（oa_approvers 表配置）
- ✅ 企业微信通知（群机器人 Webhook）
- ✅ 仪表盘统计（待处理、已申请、已使用年假）
- ✅ 审批详情（时间线、审批记录）

#### 企业微信集成

审批系统通过企业微信群机器人 Webhook 发送通知：

- **提交申请** → 通知审批人
- **审批通过/驳回** → 通知申请人

配置文件：`java-spring-project/oa-service/src/main/resources/application.yml`

```yaml
wecom:
  enabled: true
  webhook-url: https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=YOUR_KEY
```

#### 审批人配置

审批人通过 `oa_approvers` 表配置：

| 申请人 | 审批人 |
|--------|--------|
| admin | 张三 |
| 张三 | 管理员 |
| 李四 | 张三 |
| 王五 | 管理员 |
| 赵六 | 李四 |

#### OA API 接口

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | /api/oa/leave-types | 假期类型列表 |
| POST | /api/oa/applications | 提交申请 |
| GET | /api/oa/applications | 我的申请 |
| GET | /api/oa/applications/{id} | 申请详情 |
| POST | /api/oa/applications/{id}/approve | 审批通过 |
| POST | /api/oa/applications/{id}/reject | 审批驳回 |
| POST | /api/oa/applications/{id}/cancel | 撤回申请 |
| GET | /api/oa/applications/pending | 待我审批 |
| GET | /api/oa/dashboard | 审批仪表盘 |
| GET | /api/oa/wecom/contacts | 企业微信联系人 |
| GET | /api/oa/wecom/approver | 我的审批人 |
| POST | /api/oa/wecom/test-notify | 测试企微通知 |

### CI/CD 流水线

#### 功能特性

- ✅ 流水线管理（创建、编辑、删除）
- ✅ 流水线模板（前端、后端、全栈）
- ✅ 阶段管理（构建、测试、部署）
- ✅ 步骤配置（命令、环境变量）
- ✅ 执行历史（状态、日志、耗时）
- ✅ 仪表盘统计

#### CI/CD API 接口

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | /api/cicd/pipelines | 流水线列表 |
| POST | /api/cicd/pipelines | 创建流水线 |
| GET | /api/cicd/pipelines/{id} | 流水线详情 |
| PUT | /api/cicd/pipelines/{id} | 更新流水线 |
| DELETE | /api/cicd/pipelines/{id} | 删除流水线 |
| POST | /api/cicd/pipelines/{id}/execute | 执行流水线 |
| GET | /api/cicd/executions | 执行历史 |
| GET | /api/cicd/executions/{id} | 执行详情 |
| GET | /api/cicd/dashboard | 仪表盘统计 |

## 架构说明

### 微前端架构

```
┌─────────────────────────────────────────────────────────┐
│              Base App (localhost:3000)                    │
│              macOS/Windows 桌面风格                       │
│  ┌────────────────────────────────────────────────────┐  │
│  │  🖥️ 桌面                                           │  │
│  │  ┌──────┐ ┌──────┐ ┌──────┐ ┌──────┐             │  │
│  │  │ 🧠   │ │ 🎯   │ │ 👁️   │ │ ⚙️   │             │  │
│  │  │ NLP  │ │ 推荐  │ │ CV   │ │MLOps │             │  │
│  │  └──────┘ └──────┘ └──────┘ └──────┘             │  │
│  │  ┌──────┐ ┌──────┐ ┌──────┐ ┌──────┐             │  │
│  │  │ 🗄️   │ │ 🔐   │ │ 🚀   │ │ 📋   │             │  │
│  │  │ SQL  │ │ 系统  │ │CI/CD │ │ OA   │             │  │
│  │  └──────┘ └──────┘ └──────┘ └──────┘             │  │
│  └────────────────────────────────────────────────────┘  │
│  ┌────────────────────────────────────────────────────┐  │
│  │  📋 任务栏                                          │  │
│  └────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────┘
```

- 基座使用 **qiankun** 管理子应用生命周期
- 子应用通过 `vite-plugin-qiankun` 导出生命周期钩子
- `experimentalStyleIsolation: true` 实现 CSS 隔离
- 桌面图标支持权限过滤（基于用户角色）

### RAG 问答流程

```
用户提问
  → Embedding 模型（OpenAI text-embedding-3-small）
  → Milvus 向量检索（COSINE 相似度 Top-K）
  → 拼接上下文 Prompt
  → LLM 生成回答（OpenAI GPT-4o-mini）
  → 返回答案 + 引用来源
```

## 环境变量

| 变量 | 默认值 | 说明 |
|------|--------|------|
| DATABASE_URL | mysql+aiomysql://root:root123@localhost:3307/ai_platform | 数据库连接 |
| REDIS_URL | redis://localhost:6379/0 | Redis 连接 |
| RABBITMQ_URL | amqp://aisys:aisys123@localhost:5672/ai_platform | RabbitMQ 连接 |
| MILVUS_HOST | localhost | Milvus 地址 |
| OPENAI_API_KEY | (空) | OpenAI API Key |
| OPENAI_BASE_URL | https://api.openai.com/v1 | OpenAI API 地址 |
| LLM_MODEL | gpt-4o-mini | 对话模型 |
| EMBEDDING_MODEL | text-embedding-3-small | Embedding 模型 |

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
