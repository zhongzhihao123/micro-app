"""
NLP 知识库问答服务
=================
核心功能：
  1. POST /api/documents/upload — 上传文档，提交到 RabbitMQ 异步处理
  2. POST /api/search — 语义向量检索（Embedding → Milvus 搜索）
  3. POST /api/chat — RAG 知识库问答（检索 + LLM 生成）
  4. POST /api/chat/stream — RAG 流式问答（SSE 流式输出）
  5. GET/POST/DELETE /api/collections — 知识库集合管理

技术栈：OpenAI Embedding API + Milvus 向量检索 + LLM Chat Completion

流程：文档上传 → 分块 → 向量化(Embedding) → 存入 Milvus → 用户提问 → 向量检索 → RAG 生成
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi import FastAPI, UploadFile, File, Depends, HTTPException, BackgroundTasks
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from typing import Optional, List
from openai import AsyncOpenAI
import uuid

from common.config import get_settings
from common.milvus_client import get_milvus
from common.rabbitmq_client import get_rabbitmq
from common.auth import get_current_user
from common.exceptions import AppException, NotFoundException

settings = get_settings()

app = FastAPI(title="NLP Knowledge Base Service", version="1.0.0")

# OpenAI 客户端（兼容接口）
llm_client = AsyncOpenAI(
    api_key=settings.OPENAI_API_KEY or "sk-placeholder",
    base_url=settings.OPENAI_BASE_URL,
)


# ---- Models ----

class DocumentUploadResponse(BaseModel):
    document_id: str
    title: str
    status: str
    message: str


class SearchRequest(BaseModel):
    query: str
    top_k: int = Field(default=10, ge=1, le=100)
    collection_name: str = "default_kb"


class SearchResult(BaseModel):
    chunk_id: str
    document_id: str
    content: str
    score: float
    chunk_index: int


class SearchResponse(BaseModel):
    query: str
    results: List[SearchResult]
    total: int


class ChatRequest(BaseModel):
    query: str
    collection_name: str = "default_kb"
    conversation_id: Optional[str] = None
    top_k: int = Field(default=5, ge=1, le=20)
    stream: bool = False


class ChatResponse(BaseModel):
    answer: str
    sources: List[SearchResult]
    conversation_id: str


# ---- Routes ----

@app.get("/api/health")
async def health():
    return {"status": "healthy", "service": "nlp"}


@app.post("/api/documents/upload", response_model=DocumentUploadResponse)
async def upload_document(
    file: UploadFile = File(...),
    current_user: dict = Depends(get_current_user),
):
    """上传文档并触发异步处理"""
    document_id = str(uuid.uuid4())

    # 保存文件
    upload_dir = settings.UPLOAD_DIR
    os.makedirs(upload_dir, exist_ok=True)
    file_path = os.path.join(upload_dir, f"{document_id}_{file.filename}")
    content = await file.read()
    with open(file_path, "wb") as f:
        f.write(content)

    # 提交到消息队列异步处理
    rabbitmq = await get_rabbitmq()
    await rabbitmq.submit_nlp_document_task(
        document_id=document_id,
        file_path=file_path,
    )

    return DocumentUploadResponse(
        document_id=document_id,
        title=file.filename,
        status="processing",
        message="Document uploaded and queued for processing",
    )


@app.post("/api/search", response_model=SearchResponse)
async def semantic_search(
    request: SearchRequest,
    current_user: dict = Depends(get_current_user),
):
    """语义向量检索"""
    milvus = await get_milvus()

    # 生成查询向量
    embedding_response = await llm_client.embeddings.create(
        model=settings.EMBEDDING_MODEL,
        input=request.query,
    )
    query_vector = embedding_response.data[0].embedding

    # Milvus 向量检索
    try:
        results = milvus.search_vectors(
            collection_name=request.collection_name,
            query_vector=query_vector,
            top_k=request.top_k,
        )
    except ValueError:
        # 集合不存在时返回空结果
        return SearchResponse(query=request.query, results=[], total=0)

    return SearchResponse(
        query=request.query,
        results=[
            SearchResult(
                chunk_id=r["chunk_id"],
                document_id=r["document_id"],
                content=r["content"][:500],
                score=r["score"],
                chunk_index=r["chunk_index"],
            )
            for r in results
        ],
        total=len(results),
    )


@app.post("/api/chat", response_model=ChatResponse)
async def rag_chat(
    request: ChatRequest,
    current_user: dict = Depends(get_current_user),
):
    """RAG 知识库问答"""
    milvus = await get_milvus()

    # 1. 检索相关文档
    embedding_response = await llm_client.embeddings.create(
        model=settings.EMBEDDING_MODEL,
        input=request.query,
    )
    query_vector = embedding_response.data[0].embedding

    try:
        search_results = milvus.search_vectors(
            collection_name=request.collection_name,
            query_vector=query_vector,
            top_k=request.top_k,
        )
    except ValueError:
        search_results = []

    # 2. 构建上下文
    context = "\n\n---\n\n".join([
        f"[来源 {i+1}] {r['content']}"
        for i, r in enumerate(search_results)
    ]) if search_results else "暂无相关文档"

    # 3. LLM 生成回答
    system_prompt = f"""你是一个企业知识库助手。基于以下参考文档回答用户问题。
如果文档中没有相关信息，请如实告知，不要编造。

参考文档：
{context}"""

    response = await llm_client.chat.completions.create(
        model=settings.LLM_MODEL,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": request.query},
        ],
        temperature=0.3,
        max_tokens=2000,
    )

    conversation_id = request.conversation_id or str(uuid.uuid4())
    answer = response.choices[0].message.content

    return ChatResponse(
        answer=answer,
        sources=[
            SearchResult(
                chunk_id=r["chunk_id"],
                document_id=r["document_id"],
                content=r["content"][:300],
                score=r["score"],
                chunk_index=r["chunk_index"],
            )
            for r in search_results
        ],
        conversation_id=conversation_id,
    )


@app.post("/api/chat/stream")
async def rag_chat_stream(
    request: ChatRequest,
    current_user: dict = Depends(get_current_user),
):
    """RAG 流式问答"""
    milvus = await get_milvus()

    # 检索
    embedding_response = await llm_client.embeddings.create(
        model=settings.EMBEDDING_MODEL,
        input=request.query,
    )
    query_vector = embedding_response.data[0].embedding

    try:
        search_results = milvus.search_vectors(
            collection_name=request.collection_name,
            query_vector=query_vector,
            top_k=request.top_k,
        )
    except ValueError:
        search_results = []

    context = "\n\n---\n\n".join([
        f"[来源 {i+1}] {r['content']}"
        for i, r in enumerate(search_results)
    ]) if search_results else "暂无相关文档"

    system_prompt = f"你是企业知识库助手。基于以下文档回答：\n\n{context}"

    async def generate():
        stream = await llm_client.chat.completions.create(
            model=settings.LLM_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": request.query},
            ],
            temperature=0.3,
            max_tokens=2000,
            stream=True,
        )
        async for chunk in stream:
            if chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content

    return StreamingResponse(generate(), media_type="text/plain")


@app.get("/api/collections")
async def list_collections(current_user: dict = Depends(get_current_user)):
    """列出所有知识库集合"""
    milvus = await get_milvus()
    collections = milvus.list_collections()
    return {"collections": collections, "total": len(collections)}


@app.post("/api/collections/{name}")
async def create_collection(
    name: str,
    dim: int = 1536,
    current_user: dict = Depends(get_current_user),
):
    """创建知识库集合"""
    milvus = await get_milvus()
    collection = milvus.create_knowledge_collection(name, dim=dim)
    return {"name": collection.name, "message": "Collection created successfully"}


@app.delete("/api/collections/{name}")
async def delete_collection(
    name: str,
    current_user: dict = Depends(get_current_user),
):
    """删除知识库集合"""
    milvus = await get_milvus()
    milvus.drop_collection(name)
    return {"message": f"Collection {name} deleted"}
