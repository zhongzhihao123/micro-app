"""
RabbitMQ 客户端 - 异步消息队列
==============================
基于 aio-pika 实现，支持：
1. 消息发布到指定 Topic Exchange
2. 消息消费与回调处理
3. 业务任务快捷方法（文档处理、向量化、CV 任务、训练任务）

Exchange 设计：
  - ai.tasks（topic）: 异步任务分发
  - ai.events（topic）: 事件通知
  - ai.dlq（topic）: 死信队列
"""
import json
import asyncio
from typing import Optional, Callable, Any
import aio_pika
from aio_pika.abc import AbstractRobustConnection, AbstractRobustChannel
from .config import get_settings

settings = get_settings()


class RabbitMQClient:
    """异步 RabbitMQ 客户端，支持发布/订阅/延迟队列"""

    def __init__(self, url: Optional[str] = None):
        self._url = url or settings.RABBITMQ_URL
        self._connection: Optional[AbstractRobustConnection] = None
        self._channel: Optional[AbstractRobustChannel] = None
        self._consumer_tasks: list[asyncio.Task] = []

    async def connect(self):
        if self._connection is None:
            self._connection = await aio_pika.connect_robust(self._url)
            self._channel = await self._connection.channel()
            await self._channel.set_qos(prefetch_count=settings.RABBITMQ_PREFETCH_COUNT)

    async def disconnect(self):
        for task in self._consumer_tasks:
            task.cancel()
        if self._channel:
            await self._channel.close()
        if self._connection:
            await self._connection.close()
        self._channel = None
        self._connection = None

    @property
    def channel(self) -> AbstractRobustChannel:
        if self._channel is None:
            raise RuntimeError("RabbitMQ not connected. Call connect() first.")
        return self._channel

    # ---- Publish ----

    async def publish(
        self,
        routing_key: str,
        message: dict[str, Any],
        exchange: str = "ai.tasks",
        priority: int = 0,
    ):
        """发布消息到指定路由"""
        body = json.dumps(message, default=str).encode()
        msg = aio_pika.Message(
            body=body,
            content_type="application/json",
            priority=priority,
            delivery_mode=aio_pika.DeliveryMode.PERSISTENT,
        )
        exchange_obj = await self.channel.get_exchange(exchange)
        await exchange_obj.publish(msg, routing_key=routing_key)

    async def publish_event(self, event_type: str, data: dict[str, Any]):
        """发布事件通知"""
        await self.publish(
            routing_key=f"notify.{event_type}",
            message={"type": event_type, "data": data, "timestamp": None},
            exchange="ai.events",
        )

    # ---- Consume ----

    async def consume(
        self,
        queue_name: str,
        callback: Callable[[dict], Any],
        prefetch_count: int = 10,
    ):
        """订阅队列消息"""
        await self.channel.set_qos(prefetch_count=prefetch_count)
        queue = await self.channel.declare_queue(queue_name, durable=True)

        async def _on_message(message: aio_pika.IncomingMessage):
            async with message.process():
                try:
                    body = json.loads(message.body.decode())
                    await callback(body)
                except Exception as e:
                    # 消息处理失败，进入 DLQ
                    print(f"Message processing failed: {e}")
                    await message.reject(requeue=False)

        await queue.consume(_on_message)

    # ---- Task Helpers ----

    async def submit_nlp_document_task(self, document_id: str, file_path: str):
        """提交文档处理任务"""
        await self.publish(
            routing_key="nlp.document.process",
            message={
                "task_type": "document_process",
                "document_id": document_id,
                "file_path": file_path,
            },
        )

    async def submit_embedding_task(self, document_id: str, chunk_ids: list[str]):
        """提交向量化任务"""
        await self.publish(
            routing_key="nlp.embedding.generate",
            message={
                "task_type": "embedding_generate",
                "document_id": document_id,
                "chunk_ids": chunk_ids,
            },
        )

    async def submit_cv_task(self, task_id: str, image_url: str, task_type: str):
        """提交计算机视觉任务"""
        await self.publish(
            routing_key=f"cv.{task_type}",
            message={
                "task_type": task_type,
                "task_id": task_id,
                "image_url": image_url,
            },
        )

    async def submit_training_job(self, job_id: str, config: dict):
        """提交模型训练任务"""
        await self.publish(
            routing_key="mlops.training.job",
            message={
                "task_type": "training",
                "job_id": job_id,
                "config": config,
            },
        )


# 全局实例
_rabbitmq_client = RabbitMQClient()


async def get_rabbitmq() -> RabbitMQClient:
    if _rabbitmq_client._connection is None:
        await _rabbitmq_client.connect()
    return _rabbitmq_client
