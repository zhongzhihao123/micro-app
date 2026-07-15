"""
推荐系统服务
===========
核心功能：
  1. POST /api/recommend — 个性化推荐（5种算法可选）
  2. POST /api/behavior — 记录用户行为（发布到 RabbitMQ 异步处理）
  3. POST /api/recommend/batch — 批量推荐
  4. POST /api/ab-test/assign — A/B 测试流量分配
  5. GET /api/items — 商品/内容列表
  6. GET /api/stats — 推荐系统统计

推荐算法：
  - collaborative：协同过滤（基于相似用户）
  - content：基于内容的推荐（基于物品属性）
  - hybrid：混合推荐（协同 + 内容）
  - hot：热门推荐（按基础分数排序）
  - latest：最新推荐（按上架时间排序）

缓存策略：推荐结果缓存到 Redis，TTL 5分钟
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi import FastAPI, Depends, Query
from pydantic import BaseModel, Field
from typing import Optional, List
import uuid
import random
from datetime import datetime, timedelta, timezone

from common.config import get_settings
from common.redis_client import get_redis
from common.rabbitmq_client import get_rabbitmq
from common.auth import get_current_user
from common.exceptions import AppException

settings = get_settings()

app = FastAPI(title="Recommendation Service", version="1.0.0")


# ---- Models ----

class ItemInfo(BaseModel):
    item_id: str
    title: str
    category: str
    score: float
    reason: str


class RecommendRequest(BaseModel):
    user_id: Optional[str] = None
    category: Optional[str] = None
    limit: int = Field(default=20, ge=1, le=100)
    algorithm: str = Field(default="hybrid", pattern="^(collaborative|content|hybrid|hot|latest)$")
    exclude_ids: List[str] = []


class RecommendResponse(BaseModel):
    user_id: str
    algorithm: str
    items: List[ItemInfo]
    generated_at: str


class BehaviorRequest(BaseModel):
    user_id: str
    item_id: str
    behavior_type: str = Field(pattern="^(view|click|like|purchase|share|comment)$")
    weight: float = Field(default=1.0, ge=0.0, le=5.0)


class ABTestRequest(BaseModel):
    experiment_name: str
    user_id: str
    variants: List[str] = ["model_a", "model_b"]
    traffic_split: float = Field(default=0.5, ge=0.0, le=1.0)


class BatchRecommendRequest(BaseModel):
    user_ids: List[str]
    limit: int = Field(default=20, ge=1, le=100)
    algorithm: str = "hybrid"


# ---- Mock Data ----

MOCK_ITEMS = [
    {"id": f"item_{i:04d}", "title": f"产品-{i:04d}", "category": random.choice(["电子产品", "图书", "服装", "食品", "家居"]), "base_score": round(random.uniform(0.3, 0.95), 4)}
    for i in range(1, 501)
]

RECOMMEND_REASONS = {
    "collaborative": "与你相似的用户也喜欢",
    "content": "与你浏览过的内容相似",
    "hybrid": "综合多维度推荐",
    "hot": "当前热门内容",
    "latest": "最新上架",
}


# ---- Recommendation Engine ----

class RecommendationEngine:
    """推荐引擎核心"""

    @staticmethod
    def collaborative_filtering(user_id: str, limit: int, exclude_ids: List[str]) -> List[ItemInfo]:
        """协同过滤推荐（模拟）"""
        seed = hash(user_id) % 10000
        random.seed(seed)
        candidates = [item for item in MOCK_ITEMS if item["id"] not in exclude_ids]
        selected = random.sample(candidates, min(limit, len(candidates)))
        return [
            ItemInfo(
                item_id=item["id"],
                title=item["title"],
                category=item["category"],
                score=round(item["base_score"] * random.uniform(0.8, 1.2), 4),
                reason=RECOMMEND_REASONS["collaborative"],
            )
            for item in selected
        ]

    @staticmethod
    def content_based(user_id: str, limit: int, exclude_ids: List[str]) -> List[ItemInfo]:
        """基于内容的推荐（模拟）"""
        seed = hash(user_id + "content") % 10000
        random.seed(seed)
        candidates = [item for item in MOCK_ITEMS if item["id"] not in exclude_ids]
        selected = random.sample(candidates, min(limit, len(candidates)))
        return [
            ItemInfo(
                item_id=item["id"],
                title=item["title"],
                category=item["category"],
                score=round(item["base_score"] * random.uniform(0.7, 1.3), 4),
                reason=RECOMMEND_REASONS["content"],
            )
            for item in selected
        ]

    @staticmethod
    def hybrid_recommend(user_id: str, limit: int, exclude_ids: List[str]) -> List[ItemInfo]:
        """混合推荐"""
        cf_items = RecommendationEngine.collaborative_filtering(user_id, limit // 2, exclude_ids)
        cb_items = RecommendationEngine.content_based(user_id, limit // 2, exclude_ids)
        combined = cf_items + cb_items
        random.shuffle(combined)
        for item in combined:
            item.reason = RECOMMEND_REASONS["hybrid"]
        return combined[:limit]

    @staticmethod
    def hot_items(limit: int, exclude_ids: List[str]) -> List[ItemInfo]:
        """热门推荐"""
        candidates = sorted(MOCK_ITEMS, key=lambda x: x["base_score"], reverse=True)
        candidates = [item for item in candidates if item["id"] not in exclude_ids]
        return [
            ItemInfo(
                item_id=item["id"],
                title=item["title"],
                category=item["category"],
                score=item["base_score"],
                reason=RECOMMEND_REASONS["hot"],
            )
            for item in candidates[:limit]
        ]

    @staticmethod
    def latest_items(limit: int, exclude_ids: List[str]) -> List[ItemInfo]:
        """最新推荐"""
        latest = list(reversed(MOCK_ITEMS))
        candidates = [item for item in latest if item["id"] not in exclude_ids]
        return [
            ItemInfo(
                item_id=item["id"],
                title=item["title"],
                category=item["category"],
                score=item["base_score"],
                reason=RECOMMEND_REASONS["latest"],
            )
            for item in candidates[:limit]
        ]


engine = RecommendationEngine()

ALGORITHM_MAP = {
    "collaborative": engine.collaborative_filtering,
    "content": engine.content_based,
    "hybrid": engine.hybrid_recommend,
    "hot": lambda uid, limit, exc: engine.hot_items(limit, exc),
    "latest": lambda uid, limit, exc: engine.latest_items(limit, exc),
}


# ---- Routes ----

@app.get("/api/health")
async def health():
    return {"status": "healthy", "service": "recommend"}


@app.post("/api/recommend", response_model=RecommendResponse)
async def get_recommendations(
    request: RecommendRequest,
    current_user: dict = Depends(get_current_user),
):
    """获取个性化推荐"""
    user_id = request.user_id or current_user.get("sub", "anonymous")

    # 尝试从缓存获取
    redis = await get_redis()
    cache_key = f"recommend:{user_id}:{request.algorithm}:{request.limit}"
    cached = await redis.get_json(cache_key)
    if cached:
        return RecommendResponse(**cached)

    # 生成推荐
    algo_fn = ALGORITHM_MAP.get(request.algorithm, engine.hybrid_recommend)
    items = algo_fn(user_id, request.limit, request.exclude_ids)

    response = RecommendResponse(
        user_id=user_id,
        algorithm=request.algorithm,
        items=items,
        generated_at=datetime.now(timezone.utc).isoformat(),
    )

    # 缓存结果（5分钟）
    await redis.set_json(cache_key, response.model_dump(), expire=300)

    return response


@app.post("/api/behavior")
async def record_behavior(
    request: BehaviorRequest,
    current_user: dict = Depends(get_current_user),
):
    """记录用户行为"""
    # 发布行为事件到消息队列，异步处理
    rabbitmq = await get_rabbitmq()
    await rabbitmq.publish_event("user_behavior", request.model_dump())

    return {
        "message": "Behavior recorded",
        "user_id": request.user_id,
        "item_id": request.item_id,
        "behavior_type": request.behavior_type,
    }


@app.post("/api/recommend/batch", response_model=List[RecommendResponse])
async def batch_recommend(
    request: BatchRecommendRequest,
    current_user: dict = Depends(get_current_user),
):
    """批量推荐（异步处理）"""
    rabbitmq = await get_rabbitmq()
    for user_id in request.user_ids:
        await rabbitmq.publish(
            routing_key="recommend.inference.batch",
            message={
                "user_id": user_id,
                "limit": request.limit,
                "algorithm": request.algorithm,
            },
        )

    return [
        RecommendResponse(
            user_id=uid,
            algorithm=request.algorithm,
            items=[],
            generated_at=datetime.now(timezone.utc).isoformat(),
        )
        for uid in request.user_ids
    ]


@app.post("/api/ab-test/assign")
async def ab_test_assign(
    request: ABTestRequest,
    current_user: dict = Depends(get_current_user),
):
    """A/B 测试分流"""
    seed = hash(request.user_id + request.experiment_name)
    random.seed(seed)
    variant = request.variants[0] if random.random() < request.traffic_split else request.variants[1]

    return {
        "user_id": request.user_id,
        "experiment": request.experiment_name,
        "assigned_variant": variant,
    }


@app.get("/api/items")
async def list_items(
    category: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
):
    """商品列表"""
    items = MOCK_ITEMS
    if category:
        items = [i for i in items if i["category"] == category]

    start = (page - 1) * page_size
    end = start + page_size

    return {
        "items": items[start:end],
        "total": len(items),
        "page": page,
        "page_size": page_size,
    }


@app.get("/api/items/{item_id}")
async def get_item(item_id: str):
    """商品详情"""
    for item in MOCK_ITEMS:
        if item["id"] == item_id:
            return item
    raise AppException(f"Item not found: {item_id}", status_code=404)


@app.get("/api/stats")
async def get_stats(current_user: dict = Depends(get_current_user)):
    """推荐系统统计"""
    return {
        "total_items": len(MOCK_ITEMS),
        "algorithms": list(ALGORITHM_MAP.keys()),
        "cache_hit_rate": round(random.uniform(0.6, 0.95), 2),
        "avg_latency_ms": round(random.uniform(5, 50), 2),
        "active_experiments": 2,
    }
