"""
Milvus 客户端 - 向量数据库操作
==============================
基于 pymilvus 实现，提供：
1. 向量集合 CRUD（创建知识库集合、获取、删除）
2. 向量插入（批量写入 embedding）
3. 向量检索（COSINE 相似度搜索，Top-K）
4. 按文档 ID 删除向量

索引策略：IVF_FLAT + COSINE 相似度
"""
from typing import Optional, Any
from pymilvus import (
    connections,
    Collection,
    CollectionSchema,
    FieldSchema,
    DataType,
    utility,
)
from .config import get_settings

settings = get_settings()


class MilvusClient:
    """Milvus 向量数据库客户端"""

    def __init__(self, host: Optional[str] = None, port: Optional[int] = None):
        self._host = host or settings.MILVUS_HOST
        self._port = port or settings.MILVUS_PORT
        self._connected = False
        self._alias = "default"

    def connect(self):
        if not self._connected:
            connections.connect(
                alias=self._alias,
                host=self._host,
                port=self._port,
            )
            self._connected = True

    def disconnect(self):
        if self._connected:
            connections.disconnect(self._alias)
            self._connected = False

    # ---- Collection Management ----

    def create_knowledge_collection(self, collection_name: str, dim: int = 1536):
        """创建知识库向量集合"""
        prefix = settings.MILVUS_COLLECTION_PREFIX
        full_name = f"{prefix}{collection_name}"

        if utility.has_collection(full_name):
            return Collection(full_name)

        fields = [
            FieldSchema(name="id", dtype=DataType.INT64, is_primary=True, auto_id=True),
            FieldSchema(name="document_id", dtype=DataType.VARCHAR, max_length=100),
            FieldSchema(name="chunk_id", dtype=DataType.VARCHAR, max_length=100),
            FieldSchema(name="chunk_index", dtype=DataType.INT64),
            FieldSchema(name="content", dtype=DataType.VARCHAR, max_length=65535),
            FieldSchema(name="embedding", dtype=DataType.FLOAT_VECTOR, dim=dim),
        ]
        schema = CollectionSchema(fields, description=f"Knowledge base: {collection_name}")
        collection = Collection(full_name, schema)

        # 创建索引
        index_params = {
            "metric_type": "COSINE",
            "index_type": "IVF_FLAT",
            "params": {"nlist": 1024},
        }
        collection.create_index(field_name="embedding", index_params=index_params)
        collection.load()

        return collection

    def get_collection(self, collection_name: str) -> Collection:
        """获取已有集合"""
        full_name = f"{settings.MILVUS_COLLECTION_PREFIX}{collection_name}"
        if not utility.has_collection(full_name):
            raise ValueError(f"Collection {full_name} not found")
        collection = Collection(full_name)
        collection.load()
        return collection

    def drop_collection(self, collection_name: str):
        """删除集合"""
        full_name = f"{settings.MILVUS_COLLECTION_PREFIX}{collection_name}"
        if utility.has_collection(full_name):
            utility.drop_collection(full_name)

    # ---- Vector Operations ----

    def insert_vectors(
        self,
        collection_name: str,
        vectors: list[list[float]],
        document_ids: list[str],
        chunk_ids: list[str],
        chunk_indices: list[int],
        contents: list[str],
    ) -> list[int]:
        """批量插入向量"""
        collection = self.get_collection(collection_name)
        entities = [document_ids, chunk_ids, chunk_indices, contents, vectors]
        result = collection.insert(entities)
        collection.flush()
        return result.primary_keys

    def search_vectors(
        self,
        collection_name: str,
        query_vector: list[float],
        top_k: int = 10,
        metric_type: str = "COSINE",
    ) -> list[dict]:
        """向量相似度搜索"""
        collection = self.get_collection(collection_name)
        search_params = {"metric_type": metric_type, "params": {"nprobe": 16}}

        results = collection.search(
            data=[query_vector],
            anns_field="embedding",
            param=search_params,
            limit=top_k,
            output_fields=["document_id", "chunk_id", "chunk_index", "content"],
        )

        return [
            {
                "id": hit.id,
                "document_id": hit.entity.get("document_id"),
                "chunk_id": hit.entity.get("chunk_id"),
                "chunk_index": hit.entity.get("chunk_index"),
                "content": hit.entity.get("content"),
                "score": float(hit.distance),
            }
            for hit in results[0]
        ]

    def delete_by_document(self, collection_name: str, document_id: str):
        """按文档ID删除向量"""
        collection = self.get_collection(collection_name)
        expr = f'document_id == "{document_id}"'
        collection.delete(expr)

    def get_collection_stats(self, collection_name: str) -> dict:
        """获取集合统计信息"""
        collection = self.get_collection(collection_name)
        return {
            "name": collection.name,
            "num_entities": collection.num_entities,
            "indexes": [idx.to_dict() for idx in collection.indexes],
        }

    def list_collections(self) -> list[str]:
        """列出所有集合"""
        prefix = settings.MILVUS_COLLECTION_PREFIX
        all_collections = utility.list_collections()
        return [c for c in all_collections if c.startswith(prefix)]


# 全局实例
_milvus_client = MilvusClient()


async def get_milvus() -> MilvusClient:
    if not _milvus_client._connected:
        _milvus_client.connect()
    return _milvus_client
