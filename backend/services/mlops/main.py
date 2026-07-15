"""
MLOps 平台服务
=============
核心功能：
  1. Model Registry — 模型注册、版本管理、状态流转（development → staging → production → archived）
  2. Training Jobs — 训练任务提交（RabbitMQ 异步）、任务列表、状态查询
  3. A/B Experiments — 实验创建、流量分配、指标对比、显著性检验
  4. Deployment — 模型部署到 staging/production 环境
  5. Monitoring — 推理日志查询、模型漂移检测、监控仪表盘

模型生命周期：注册 → 训练 → 实验 → 部署 → 监控 → 漂移检测 → 重训练
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi import FastAPI, Depends, Query, BackgroundTasks
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
import uuid
import random
from datetime import datetime, timedelta, timezone

from common.config import get_settings
from common.redis_client import get_redis
from common.rabbitmq_client import get_rabbitmq
from common.auth import get_current_user, get_current_admin
from common.exceptions import AppException, NotFoundException

settings = get_settings()

app = FastAPI(title="MLOps Platform Service", version="1.0.0")


# ---- Models ----

class ModelInfo(BaseModel):
    id: str
    name: str
    version: str
    model_type: str
    framework: str
    description: str
    status: str
    metrics: Dict[str, Any]
    created_at: str


class RegisterModelRequest(BaseModel):
    name: str = Field(min_length=1, max_length=200)
    version: str = Field(min_length=1, max_length=50)
    model_type: str = Field(pattern="^(classification|regression|detection|nlp|recommendation|custom)$")
    framework: str = Field(default="pytorch")
    description: str = ""
    parameters: Dict[str, Any] = {}
    metrics: Dict[str, Any] = {}


class TrainingJobRequest(BaseModel):
    model_name: str
    model_version: str
    config: Dict[str, Any] = {}
    priority: int = Field(default=0, ge=0, le=10)


class TrainingJobInfo(BaseModel):
    id: str
    job_name: str
    status: str
    config: Dict[str, Any]
    metrics: Dict[str, Any]
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    error_message: Optional[str] = None


class ABExperimentRequest(BaseModel):
    name: str
    model_a_id: str
    model_b_id: str
    traffic_split: float = Field(default=0.5, ge=0.0, le=1.0)
    metrics: List[str] = ["accuracy", "latency", "throughput"]


class ABExperimentInfo(BaseModel):
    id: str
    name: str
    model_a_id: str
    model_b_id: str
    traffic_split: float
    status: str
    metrics: Dict[str, Any]
    started_at: Optional[str] = None


class DeployRequest(BaseModel):
    model_id: str
    environment: str = Field(default="staging", pattern="^(staging|production)$")
    replicas: int = Field(default=2, ge=1, le=10)
    resources: Dict[str, str] = Field(default={"cpu": "2", "memory": "4Gi"})


class InferenceLog(BaseModel):
    id: str
    model_id: str
    latency_ms: float
    token_count: int
    cost: float
    is_error: bool
    created_at: str


class DriftReport(BaseModel):
    model_id: str
    model_name: str
    drift_detected: bool
    drift_score: float
    feature_drifts: Dict[str, float]
    recommendation: str
    checked_at: str


# ---- Mock Data Store ----

MOCK_MODELS: List[dict] = [
    {
        "id": f"model_{i:04d}",
        "name": random.choice(["bert-classifier", "resnet-detector", "xgboost-ranker", "gpt-rag", "lstm-forecaster"]),
        "version": f"v{random.randint(1,5)}.{random.randint(0,9)}.{random.randint(0,9)}",
        "model_type": random.choice(["classification", "detection", "nlp", "recommendation"]),
        "framework": random.choice(["pytorch", "tensorflow", "onnx", "sklearn"]),
        "description": f"Production model for {random.choice(['text classification', 'object detection', 'ranking', 'generation'])}",
        "status": random.choice(["development", "staging", "production", "archived"]),
        "metrics": {
            "accuracy": round(random.uniform(0.82, 0.98), 4),
            "precision": round(random.uniform(0.80, 0.97), 4),
            "recall": round(random.uniform(0.78, 0.96), 4),
            "f1_score": round(random.uniform(0.80, 0.97), 4),
            "latency_p50_ms": round(random.uniform(5, 100), 2),
            "latency_p99_ms": round(random.uniform(20, 500), 2),
        },
        "created_at": (datetime.now(timezone.utc) - timedelta(days=random.randint(1, 180))).isoformat(),
    }
    for i in range(1, 21)
]


# ---- Routes ----

@app.get("/api/health")
async def health():
    return {"status": "healthy", "service": "mlops"}


# ---- Model Registry ----

@app.get("/api/models", response_model=List[ModelInfo])
async def list_models(
    status: Optional[str] = Query(None),
    model_type: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
):
    """模型列表"""
    models = MOCK_MODELS
    if status:
        models = [m for m in models if m["status"] == status]
    if model_type:
        models = [m for m in models if m["model_type"] == model_type]

    start = (page - 1) * page_size
    return [ModelInfo(**m) for m in models[start:start + page_size]]


@app.get("/api/models/{model_id}", response_model=ModelInfo)
async def get_model(model_id: str):
    """模型详情"""
    for model in MOCK_MODELS:
        if model["id"] == model_id:
            return ModelInfo(**model)
    raise NotFoundException("Model", model_id)


@app.post("/api/models", response_model=ModelInfo)
async def register_model(
    request: RegisterModelRequest,
    current_user: dict = Depends(get_current_user),
):
    """注册新模型"""
    new_model = {
        "id": f"model_{uuid.uuid4().hex[:8]}",
        "name": request.name,
        "version": request.version,
        "model_type": request.model_type,
        "framework": request.framework,
        "description": request.description,
        "status": "development",
        "metrics": request.metrics,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    MOCK_MODELS.append(new_model)
    return ModelInfo(**new_model)


@app.put("/api/models/{model_id}/status")
async def update_model_status(
    model_id: str,
    status: str = Query(pattern="^(development|staging|production|archived)$"),
    current_user: dict = Depends(get_current_admin),
):
    """更新模型状态（管理员）"""
    for model in MOCK_MODELS:
        if model["id"] == model_id:
            model["status"] = status
            return {"message": f"Model {model_id} status updated to {status}"}
    raise NotFoundException("Model", model_id)


# ---- Training Jobs ----

@app.post("/api/training/jobs", response_model=TrainingJobInfo)
async def submit_training_job(
    request: TrainingJobRequest,
    background_tasks: BackgroundTasks,
    current_user: dict = Depends(get_current_user),
):
    """提交训练任务"""
    job_id = f"job_{uuid.uuid4().hex[:8]}"

    # 提交到消息队列
    rabbitmq = await get_rabbitmq()
    await rabbitmq.submit_training_job(
        job_id=job_id,
        config=request.config,
    )

    return TrainingJobInfo(
        id=job_id,
        job_name=f"{request.model_name}-{request.model_version}",
        status="queued",
        config=request.config,
        metrics={},
    )


@app.get("/api/training/jobs", response_model=List[TrainingJobInfo])
async def list_training_jobs(
    status: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
):
    """训练任务列表"""
    mock_jobs = [
        TrainingJobInfo(
            id=f"job_{i:04d}",
            job_name=f"training-run-{i:04d}",
            status=random.choice(["completed", "running", "failed", "queued"]),
            config={"epochs": random.randint(10, 100), "batch_size": random.choice([16, 32, 64]), "learning_rate": round(random.uniform(1e-5, 1e-3), 6)},
            metrics={"train_loss": round(random.uniform(0.1, 2.0), 4), "val_loss": round(random.uniform(0.1, 2.5), 4), "val_accuracy": round(random.uniform(0.7, 0.98), 4)} if random.random() > 0.3 else {},
            started_at=(datetime.now(timezone.utc) - timedelta(hours=random.randint(1, 72))).isoformat(),
            completed_at=(datetime.now(timezone.utc) - timedelta(minutes=random.randint(1, 120))).isoformat() if random.random() > 0.3 else None,
            error_message="Out of memory error" if random.random() < 0.1 else None,
        )
        for i in range(1, 21)
    ]
    if status:
        mock_jobs = [j for j in mock_jobs if j.status == status]
    start = (page - 1) * page_size
    return mock_jobs[start:start + page_size]


@app.get("/api/training/jobs/{job_id}", response_model=TrainingJobInfo)
async def get_training_job(job_id: str):
    """训练任务详情"""
    return TrainingJobInfo(
        id=job_id,
        job_name=f"training-{job_id}",
        status="completed",
        config={"epochs": 50, "batch_size": 32},
        metrics={"train_loss": 0.234, "val_loss": 0.451, "val_accuracy": 0.934},
        started_at=(datetime.now(timezone.utc) - timedelta(hours=2)).isoformat(),
        completed_at=datetime.now(timezone.utc).isoformat(),
    )


# ---- A/B Experiments ----

@app.post("/api/experiments", response_model=ABExperimentInfo)
async def create_experiment(
    request: ABExperimentRequest,
    current_user: dict = Depends(get_current_user),
):
    """创建 A/B 实验"""
    return ABExperimentInfo(
        id=f"exp_{uuid.uuid4().hex[:8]}",
        name=request.name,
        model_a_id=request.model_a_id,
        model_b_id=request.model_b_id,
        traffic_split=request.traffic_split,
        status="draft",
        metrics={m: 0.0 for m in request.metrics},
    )


@app.get("/api/experiments", response_model=List[ABExperimentInfo])
async def list_experiments(
    status: Optional[str] = Query(None),
):
    """A/B 实验列表"""
    mock_experiments = [
        ABExperimentInfo(
            id=f"exp_{i:04d}",
            name=f"experiment-{i:04d}",
            model_a_id=f"model_{random.randint(1,20):04d}",
            model_b_id=f"model_{random.randint(1,20):04d}",
            traffic_split=round(random.uniform(0.1, 0.9), 2),
            status=random.choice(["running", "completed", "draft"]),
            metrics={
                "accuracy_a": round(random.uniform(0.85, 0.97), 4),
                "accuracy_b": round(random.uniform(0.85, 0.97), 4),
                "latency_a_ms": round(random.uniform(10, 100), 2),
                "latency_b_ms": round(random.uniform(10, 100), 2),
                "p_value": round(random.uniform(0.001, 0.5), 4),
            },
            started_at=(datetime.now(timezone.utc) - timedelta(days=random.randint(1, 14))).isoformat(),
        )
        for i in range(1, 11)
    ]
    if status:
        mock_experiments = [e for e in mock_experiments if e.status == status]
    return mock_experiments


# ---- Deployment ----

@app.post("/api/deploy")
async def deploy_model(
    request: DeployRequest,
    current_user: dict = Depends(get_current_admin),
):
    """部署模型到指定环境"""
    return {
        "deployment_id": f"deploy_{uuid.uuid4().hex[:8]}",
        "model_id": request.model_id,
        "environment": request.environment,
        "replicas": request.replicas,
        "status": "deploying",
        "message": f"Model {request.model_id} is being deployed to {request.environment}",
    }


@app.get("/api/deployments")
async def list_deployments():
    """部署列表"""
    return {
        "deployments": [
            {
                "id": f"deploy_{i:04d}",
                "model_id": f"model_{i:04d}",
                "environment": random.choice(["staging", "production"]),
                "replicas": random.randint(1, 5),
                "status": random.choice(["running", "running", "running", "degraded"]),
                "uptime_hours": random.randint(1, 720),
            }
            for i in range(1, 6)
        ]
    }


# ---- Monitoring ----

@app.get("/api/monitoring/inference-logs", response_model=List[InferenceLog])
async def get_inference_logs(
    model_id: Optional[str] = Query(None),
    hours: int = Query(24, ge=1, le=168),
    limit: int = Query(50, ge=1, le=500),
):
    """推理日志"""
    return [
        InferenceLog(
            id=f"log_{uuid.uuid4().hex[:8]}",
            model_id=model_id or f"model_{random.randint(1,20):04d}",
            latency_ms=round(random.uniform(5, 500), 2),
            token_count=random.randint(10, 4000),
            cost=round(random.uniform(0.0001, 0.05), 6),
            is_error=random.random() < 0.02,
            created_at=(datetime.now(timezone.utc) - timedelta(minutes=random.randint(1, hours * 60))).isoformat(),
        )
        for _ in range(limit)
    ]


@app.get("/api/monitoring/drift/{model_id}", response_model=DriftReport)
async def check_model_drift(model_id: str):
    """模型漂移检测"""
    drift_score = round(random.uniform(0.0, 0.3), 4)
    return DriftReport(
        model_id=model_id,
        model_name=f"Model-{model_id}",
        drift_detected=drift_score > 0.15,
        drift_score=drift_score,
        feature_drifts={
            "feature_1": round(random.uniform(0.0, 0.4), 4),
            "feature_2": round(random.uniform(0.0, 0.4), 4),
            "feature_3": round(random.uniform(0.0, 0.4), 4),
            "feature_4": round(random.uniform(0.0, 0.4), 4),
        },
        recommendation="建议触发模型重训练" if drift_score > 0.15 else "模型表现稳定，无需操作",
        checked_at=datetime.now(timezone.utc).isoformat(),
    )


@app.get("/api/monitoring/dashboard")
async def monitoring_dashboard():
    """监控仪表盘数据"""
    return {
        "overview": {
            "total_models": len(MOCK_MODELS),
            "production_models": sum(1 for m in MOCK_MODELS if m["status"] == "production"),
            "active_experiments": random.randint(1, 5),
            "running_jobs": random.randint(0, 3),
        },
        "inference_stats": {
            "total_requests_24h": random.randint(10000, 1000000),
            "avg_latency_ms": round(random.uniform(10, 100), 2),
            "p99_latency_ms": round(random.uniform(50, 500), 2),
            "error_rate": round(random.uniform(0.001, 0.05), 4),
            "total_cost_24h": round(random.uniform(10, 500), 2),
        },
        "drift_alerts": [
            {
                "model_id": f"model_{i:04d}",
                "model_name": MOCK_MODELS[i]["name"],
                "drift_score": round(random.uniform(0.0, 0.35), 4),
                "status": "warning" if random.random() > 0.7 else "ok",
            }
            for i in range(min(5, len(MOCK_MODELS)))
        ],
        "resource_usage": {
            "cpu_percent": round(random.uniform(20, 80), 1),
            "memory_percent": round(random.uniform(30, 85), 1),
            "gpu_percent": round(random.uniform(10, 90), 1),
            "disk_percent": round(random.uniform(40, 70), 1),
        },
    }


@app.get("/api/stats")
async def get_stats():
    """MLOps 平台统计"""
    return {
        "models": {"total": len(MOCK_MODELS), "by_status": {"development": 5, "staging": 3, "production": 8, "archived": 4}},
        "training": {"total_jobs": 156, "success_rate": 0.92, "avg_duration_minutes": 45},
        "deployments": {"active": 4, "environments": ["staging", "production"]},
        "experiments": {"active": 2, "completed": 15, "significant_results": 8},
    }
