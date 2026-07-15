#!/usr/bin/env python3
"""
============================================================
AI System Platform - 数据生成方案
生成模拟数据用于开发测试和演示
============================================================
"""
import json
import random
import uuid
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

DATA_DIR = Path(__file__).parent
random.seed(42)

# ============================================================
# 配置
# ============================================================
NUM_USERS = 500
NUM_ITEMS = 1000
NUM_DOCUMENTS = 50
NUM_BEHAVIORS = 10000
NUM_CV_TASKS = 200
NUM_MODELS = 30
NUM_TRAINING_JOBS = 50
NUM_EXPERIMENTS = 20
NUM_INFERENCE_LOGS = 5000

CATEGORIES = ["电子产品", "图书", "服装", "食品", "家居", "运动", "美妆", "汽车", "医疗", "教育"]
BEHAVIOR_TYPES = ["view", "click", "like", "purchase", "share", "comment"]
MODEL_TYPES = ["classification", "regression", "detection", "nlp", "recommendation", "custom"]
FRAMEWORKS = ["pytorch", "tensorflow", "onnx", "sklearn", "jax"]
CV_TASK_TYPES = ["detection", "classification", "ocr", "segmentation", "face_recognition"]
DOC_TYPES = ["PDF", "DOCX", "MD", "TXT", "HTML"]

OBJECTS = ["person", "car", "bicycle", "motorcycle", "bus", "truck", "traffic light",
           "bench", "bird", "cat", "dog", "horse", "laptop", "cell phone",
           "book", "bottle", "cup", "chair", "table", "keyboard", "mouse", "remote"]

MODEL_NAMES = [
    "bert-text-classifier", "roberta-sentiment", "gpt-rag-assistant",
    "resnet-image-classifier", "yolo-object-detector", "efficientnet-classifier",
    "xgboost-ranker", "lightgbm-ctr-predictor", "deepfm-recommender",
    "lstm-time-series", "transformer-forecaster", "t5-summarizer",
    "whisper-transcriber", "clip-encoder", "dalle-image-gen",
    "stable-diffusion-v2", "llama-chat-v2", "mistral-instruct",
    "embedding-ada-v3", "reranker-cross-encoder",
]


def generate_users(num: int) -> list[dict]:
    """生成用户数据"""
    users = []
    roles = ["admin"] + ["user"] * 9
    for i in range(num):
        users.append({
            "id": str(uuid.uuid4()),
            "username": f"user_{i+1:04d}",
            "email": f"user{i+1:04d}@ai-platform.local",
            "role": random.choice(roles),
            "is_active": random.random() > 0.05,
            "created_at": (datetime.now(timezone.utc) - timedelta(days=random.randint(1, 365))).isoformat(),
        })
    return users


def generate_items(num: int) -> list[dict]:
    """生成商品/内容数据"""
    items = []
    for i in range(num):
        category = random.choice(CATEGORIES)
        items.append({
            "id": str(uuid.uuid4()),
            "title": f"{category}-产品-{i+1:04d}",
            "description": f"这是{category}分类下的第{i+1}个产品，具有高品质和优良性能。",
            "category": category,
            "tags": random.sample(["热销", "新品", "推荐", "限时", "精选", "爆款", "经典", "高端"], k=random.randint(1, 4)),
            "price": round(random.uniform(9.9, 9999.9), 2),
            "is_active": random.random() > 0.1,
            "created_at": (datetime.now(timezone.utc) - timedelta(days=random.randint(1, 180))).isoformat(),
        })
    return items


def generate_behaviors(num: int, user_ids: list[str], item_ids: list[str]) -> list[dict]:
    """生成用户行为数据"""
    behaviors = []
    behavior_weights = {"view": 1.0, "click": 2.0, "like": 3.0, "purchase": 5.0, "share": 4.0, "comment": 3.0}
    for _ in range(num):
        btype = random.choices(BEHAVIOR_TYPES, weights=[40, 25, 15, 5, 5, 10])[0]
        behaviors.append({
            "id": str(uuid.uuid4()),
            "user_id": random.choice(user_ids),
            "item_id": random.choice(item_ids),
            "behavior_type": btype,
            "weight": behavior_weights[btype],
            "session_id": f"sess_{random.randint(100000, 999999)}",
            "created_at": (datetime.now(timezone.utc) - timedelta(
                days=random.randint(0, 30),
                hours=random.randint(0, 23),
                minutes=random.randint(0, 59)
            )).isoformat(),
        })
    return behaviors


def generate_documents(num: int, user_ids: list[str]) -> list[dict]:
    """生成知识库文档数据"""
    doc_templates = [
        {"title": "AI平台架构设计文档_v{version}.pdf", "content_preview": "本文档详细描述了AI平台的系统架构设计..."},
        {"title": "产品需求规格说明书_{version}.docx", "content_preview": "本规格说明书定义了产品的功能需求..."},
        {"title": "系统运维手册_{version}.md", "content_preview": "本手册包含系统运维的标准操作流程..."},
        {"title": "API接口文档_v{version}.html", "content_preview": "本文档描述了平台所有API接口的定义..."},
        {"title": "数据库设计文档_v{version}.txt", "content_preview": "本文档包含数据库表结构和关系设计..."},
        {"title": "安全审计报告_{version}.pdf", "content_preview": "本报告记录了系统安全审计的发现..."},
        {"title": "性能测试报告_v{version}.docx", "content_preview": "本报告包含系统性能测试的结果..."},
        {"title": "部署手册_{version}.md", "content_preview": "本手册描述了系统的部署流程..."},
        {"title": "用户手册_v{version}.html", "content_preview": "本手册面向最终用户，介绍系统使用方法..."},
        {"title": "变更记录_{version}.txt", "content_preview": "本文档记录了系统的所有变更历史..."},
    ]

    documents = []
    for i in range(num):
        template = random.choice(doc_templates)
        version = f"{random.randint(1,5)}.{random.randint(0,9)}"
        doc_type = random.choice(DOC_TYPES)
        status = random.choices(["completed", "processing", "failed", "pending"], weights=[70, 15, 5, 10])[0]

        documents.append({
            "id": str(uuid.uuid4()),
            "user_id": random.choice(user_ids),
            "title": template["title"].format(version=version),
            "content": template["content_preview"] + f"\n\n这是第{i+1}号文档的正文内容。包含系统的详细说明、配置参数、操作步骤等信息。" * random.randint(3, 10),
            "file_type": doc_type,
            "file_size": random.randint(50000, 10000000),
            "chunk_count": random.randint(5, 200),
            "status": status,
            "created_at": (datetime.now(timezone.utc) - timedelta(days=random.randint(1, 90))).isoformat(),
            "updated_at": (datetime.now(timezone.utc) - timedelta(hours=random.randint(1, 72))).isoformat(),
        })
    return documents


def generate_cv_tasks(num: int, user_ids: list[str]) -> list[dict]:
    """生成计算机视觉任务数据"""
    tasks = []
    for _ in range(num):
        task_type = random.choice(CV_TASK_TYPES)
        status = random.choices(["completed", "processing", "failed", "pending"], weights=[75, 10, 5, 10])[0]

        result = None
        if status == "completed":
            if task_type == "detection":
                result = {
                    "objects": [{"label": random.choice(OBJECTS), "confidence": round(random.uniform(0.7, 0.99), 4),
                                 "bbox": {"x": round(random.uniform(0, 0.8), 2), "y": round(random.uniform(0, 0.8), 2),
                                          "w": round(random.uniform(0.05, 0.3), 2), "h": round(random.uniform(0.05, 0.3), 2)}}
                                for _ in range(random.randint(1, 8))],
                    "count": random.randint(1, 8),
                }
            elif task_type == "classification":
                result = {
                    "top_predictions": [{"label": random.choice(CATEGORIES), "confidence": round(random.uniform(0.5, 0.99), 4)}
                                        for _ in range(5)],
                }
            elif task_type == "ocr":
                result = {
                    "full_text": f"识别结果示例文本_{random.randint(1000, 9999)}",
                    "blocks": [{"text": f"第{i}行文本内容", "confidence": round(random.uniform(0.8, 0.99), 4)}
                               for i in range(random.randint(1, 5))],
                }

        tasks.append({
            "id": str(uuid.uuid4()),
            "user_id": random.choice(user_ids),
            "task_type": task_type,
            "status": status,
            "result": result,
            "processing_time_ms": random.randint(30, 500) if status == "completed" else None,
            "created_at": (datetime.now(timezone.utc) - timedelta(days=random.randint(0, 30))).isoformat(),
            "completed_at": (datetime.now(timezone.utc) - timedelta(days=random.randint(0, 30))).isoformat() if status == "completed" else None,
        })
    return tasks


def generate_models(num: int, user_ids: list[str]) -> list[dict]:
    """生成模型注册数据"""
    models = []
    for i in range(num):
        name = random.choice(MODEL_NAMES)
        status = random.choices(["development", "staging", "production", "archived"], weights=[20, 15, 50, 15])[0]
        models.append({
            "id": str(uuid.uuid4()),
            "name": name,
            "version": f"v{random.randint(1,5)}.{random.randint(0,9)}.{random.randint(0,9)}",
            "model_type": random.choice(MODEL_TYPES),
            "framework": random.choice(FRAMEWORKS),
            "description": f"{name} model for {random.choice(MODEL_TYPES)} tasks",
            "status": status,
            "metrics": {
                "accuracy": round(random.uniform(0.82, 0.98), 4),
                "precision": round(random.uniform(0.80, 0.97), 4),
                "recall": round(random.uniform(0.78, 0.96), 4),
                "f1_score": round(random.uniform(0.80, 0.97), 4),
                "latency_p50_ms": round(random.uniform(5, 100), 2),
                "latency_p99_ms": round(random.uniform(20, 500), 2),
            },
            "created_by": random.choice(user_ids),
            "created_at": (datetime.now(timezone.utc) - timedelta(days=random.randint(1, 365))).isoformat(),
        })
    return models


def generate_training_jobs(num: int, model_ids: list[str]) -> list[dict]:
    """生成训练任务数据"""
    jobs = []
    for i in range(num):
        status = random.choices(["completed", "running", "failed", "queued", "cancelled"], weights=[55, 15, 10, 15, 5])[0]
        jobs.append({
            "id": str(uuid.uuid4()),
            "model_id": random.choice(model_ids) if random.random() > 0.3 else None,
            "job_name": f"training-run-{i+1:04d}",
            "status": status,
            "config": {
                "epochs": random.choice([10, 20, 30, 50, 100]),
                "batch_size": random.choice([16, 32, 64, 128]),
                "learning_rate": round(random.uniform(1e-5, 1e-3), 6),
                "optimizer": random.choice(["adam", "sgd", "adamw"]),
                "early_stopping": random.random() > 0.3,
            },
            "metrics": {
                "train_loss": round(random.uniform(0.05, 2.0), 4),
                "val_loss": round(random.uniform(0.1, 2.5), 4),
                "val_accuracy": round(random.uniform(0.7, 0.98), 4),
            } if status == "completed" else {},
            "started_at": (datetime.now(timezone.utc) - timedelta(hours=random.randint(1, 168))).isoformat() if status != "queued" else None,
            "completed_at": (datetime.now(timezone.utc) - timedelta(minutes=random.randint(1, 120))).isoformat() if status == "completed" else None,
            "error_message": "CUDA out of memory" if status == "failed" and random.random() > 0.5 else ("Training diverged" if status == "failed" else None),
            "created_at": (datetime.now(timezone.utc) - timedelta(days=random.randint(1, 30))).isoformat(),
        })
    return jobs


def generate_experiments(num: int, model_ids: list[str]) -> list[dict]:
    """生成 A/B 实验数据"""
    experiments = []
    for i in range(num):
        status = random.choices(["running", "completed", "draft", "stopped"], weights=[30, 50, 10, 10])[0]
        model_a = random.choice(model_ids)
        model_b = random.choice([m for m in model_ids if m != model_a])
        experiments.append({
            "id": str(uuid.uuid4()),
            "name": f"实验-{random.choice(['推荐算法优化','模型压缩对比','特征工程','超参调优','架构对比','数据增强','损失函数对比','优化器对比'])}-{i+1:02d}",
            "model_a_id": model_a,
            "model_b_id": model_b,
            "traffic_split": round(random.uniform(0.1, 0.9), 2),
            "status": status,
            "metrics": {
                "accuracy_a": round(random.uniform(0.85, 0.97), 4),
                "accuracy_b": round(random.uniform(0.85, 0.97), 4),
                "latency_a_ms": round(random.uniform(5, 100), 2),
                "latency_b_ms": round(random.uniform(5, 100), 2),
                "p_value": round(random.uniform(0.001, 0.5), 4),
            },
            "started_at": (datetime.now(timezone.utc) - timedelta(days=random.randint(1, 30))).isoformat() if status != "draft" else None,
            "ended_at": (datetime.now(timezone.utc) - timedelta(hours=random.randint(1, 24))).isoformat() if status == "completed" else None,
            "created_at": (datetime.now(timezone.utc) - timedelta(days=random.randint(1, 60))).isoformat(),
        })
    return experiments


def generate_inference_logs(num: int, model_ids: list[str]) -> list[dict]:
    """生成推理日志"""
    logs = []
    for _ in range(num):
        logs.append({
            "id": str(uuid.uuid4()),
            "model_id": random.choice(model_ids),
            "request_id": f"req_{uuid.uuid4().hex[:12]}",
            "input_preview": f"输入内容预览_{random.randint(1000, 9999)}"[:100],
            "output_preview": f"输出结果预览_{random.randint(1000, 9999)}"[:100],
            "latency_ms": round(random.uniform(5, 500), 2),
            "token_count": random.randint(10, 4000),
            "cost": round(random.uniform(0.0001, 0.05), 6),
            "is_error": random.random() < 0.02,
            "error_message": "Timeout" if random.random() < 0.3 else "Rate limit exceeded" if random.random() < 0.3 else None,
            "created_at": (datetime.now(timezone.utc) - timedelta(
                days=random.randint(0, 7),
                hours=random.randint(0, 23),
                minutes=random.randint(0, 59),
                seconds=random.randint(0, 59),
            )).isoformat(),
        })
    return logs


def save_json(data: Any, filename: str):
    """保存 JSON 文件"""
    filepath = DATA_DIR / filename
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"✅ 已生成: {filepath} ({len(data)} 条记录)")


def main():
    print("=" * 60)
    print("🚀 AI System Platform - 数据生成")
    print("=" * 60)

    # 1. 用户
    users = generate_users(NUM_USERS)
    user_ids = [u["id"] for u in users]
    save_json(users, "users.json")

    # 2. 商品
    items = generate_items(NUM_ITEMS)
    item_ids = [it["id"] for it in items]
    save_json(items, "items.json")

    # 3. 用户行为
    behaviors = generate_behaviors(NUM_BEHAVIORS, user_ids, item_ids)
    save_json(behaviors, "behaviors.json")

    # 4. 知识库文档
    documents = generate_documents(NUM_DOCUMENTS, user_ids)
    save_json(documents, "documents.json")

    # 5. CV 任务
    cv_tasks = generate_cv_tasks(NUM_CV_TASKS, user_ids)
    save_json(cv_tasks, "cv_tasks.json")

    # 6. 模型
    models = generate_models(NUM_MODELS, user_ids)
    model_ids = [m["id"] for m in models]
    save_json(models, "models.json")

    # 7. 训练任务
    training_jobs = generate_training_jobs(NUM_TRAINING_JOBS, model_ids)
    save_json(training_jobs, "training_jobs.json")

    # 8. A/B 实验
    experiments = generate_experiments(NUM_EXPERIMENTS, model_ids)
    save_json(experiments, "experiments.json")

    # 9. 推理日志
    inference_logs = generate_inference_logs(NUM_INFERENCE_LOGS, model_ids)
    save_json(inference_logs, "inference_logs.json")

    # 10. 汇总统计
    summary = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "datasets": {
            "users": len(users),
            "items": len(items),
            "behaviors": len(behaviors),
            "documents": len(documents),
            "cv_tasks": len(cv_tasks),
            "models": len(models),
            "training_jobs": len(training_jobs),
            "experiments": len(experiments),
            "inference_logs": len(inference_logs),
        },
    }
    save_json(summary, "summary.json")

    print("=" * 60)
    print("✨ 数据生成完成！")
    print(f"📊 总计生成 {sum(summary['datasets'].values())} 条记录")
    print("=" * 60)


if __name__ == "__main__":
    main()
