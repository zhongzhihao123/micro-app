# ============================================================
# AI System Platform - Makefile
# ============================================================

DOCKER = docker compose

.PHONY: help up down restart logs status clean data install dev

help:
	@echo "AI System Platform - 命令列表"
	@echo ""
	@echo "  make up         启动所有服务"
	@echo "  make down       停止所有服务"
	@echo "  make restart    重启所有服务"
	@echo "  make logs       查看日志 (service=gateway)"
	@echo "  make status     查看服务状态"
	@echo "  make data       生成模拟数据"
	@echo "  make install    安装依赖"
	@echo "  make clean      清理容器和数据"
	@echo "  make dev        启动开发环境"
	@echo ""

up:
	$(DOCKER) up -d
	@echo "✅ 所有服务已启动"
	@echo "  API 网关:    http://localhost:8000"
	@echo "  API 文档:    http://localhost:8000/api/docs"
	@echo "  RabbitMQ:    http://localhost:15672"
	@echo "  MinIO:       http://localhost:9001"

down:
	$(DOCKER) down
	@echo "✅ 所有服务已停止"

restart: down up

logs:
	$(DOCKER) logs -f $(or $(service),gateway)

status:
	$(DOCKER) ps

data:
	cd data && python3 generate_data.py

install:
	@echo "📦 安装后端依赖..."
	cd backend && pip3 install -r requirements.txt
	@echo "📦 安装前端基座依赖..."
	cd frontend/base && npm install
	@echo "📦 安装子应用依赖..."
	cd frontend/sub-nlp && npm install
	cd frontend/sub-recommend && npm install
	cd frontend/sub-cv && npm install
	cd frontend/sub-mlops && npm install
	@echo "✅ 依赖安装完成"

dev:
	@echo "🚀 启动基础设施..."
	$(DOCKER) up -d mysql redis rabbitmq etcd minio milvus
	@echo "⏳ 等待服务就绪..."
	@sleep 10
	@echo "✅ 基础设施已启动"
	@echo ""
	@echo "📋 启动后端（新终端）:"
	@echo "  cd backend && python3 -m uvicorn gateway.main:app --host 0.0.0.0 --port 8000 --reload"
	@echo ""
	@echo "📋 启动前端（5个终端）:"
	@echo "  cd frontend/base && npm run dev          # 基座 → http://localhost:3000"
	@echo "  cd frontend/sub-nlp && npm run dev       # NLP → http://localhost:3001"
	@echo "  cd frontend/sub-recommend && npm run dev # 推荐 → http://localhost:3002"
	@echo "  cd frontend/sub-cv && npm run dev        # CV → http://localhost:3003"
	@echo "  cd frontend/sub-mlops && npm run dev     # MLOps → http://localhost:3004"

clean:
	$(DOCKER) down -v
	@echo "✅ 清理完成"
