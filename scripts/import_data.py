"""
Mock 数据导入 MySQL
从 data/*.json 文件导入数据到 MySQL ai_platform 数据库
"""
import json
import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from common.database import _db_manager
from sqlalchemy import text
import asyncio

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')

# 各表需要补充的默认字段（JSON 数据中缺失的必填列）
DEFAULT_FIELDS = {
    'users': {'hashed_password': 'mock_hash_placeholder'},
    'items': {'metadata': '{}'},
}


def prepare_row(table: str, row: dict) -> dict:
    """处理单行数据：序列化 JSON、补充默认字段"""
    clean = {}
    for k, v in row.items():
        if v is None:
            clean[k] = None
        elif isinstance(v, (dict, list)):
            clean[k] = json.dumps(v, ensure_ascii=False)
        else:
            clean[k] = v
    # 补充默认字段
    for field, default in DEFAULT_FIELDS.get(table, {}).items():
        if field not in clean:
            clean[field] = default
    return clean


async def import_json(table: str, filepath: str, batch_size: int = 200):
    """将 JSON 文件数据导入指定 MySQL 表"""
    if not os.path.exists(filepath):
        print(f"  ⚠️  文件不存在: {filepath}")
        return 0

    with open(filepath, 'r', encoding='utf-8') as f:
        rows = json.load(f)

    if not rows:
        print(f"  ⚠️  空文件: {filepath}")
        return 0

    # 预处理第一行以确定字段
    first = prepare_row(table, rows[0])
    columns = list(first.keys())
    cols_comma = ', '.join([f'`{c}`' for c in columns])
    placeholders = ', '.join([f':{c}' for c in columns])
    sql = f"INSERT INTO `{table}` ({cols_comma}) VALUES ({placeholders})"

    async with _db_manager.engine.connect() as conn:
        total = 0
        for i in range(0, len(rows), batch_size):
            batch = rows[i:i + batch_size]
            for row in batch:
                clean = prepare_row(table, row)
                await conn.execute(text(sql), clean)
            total += len(batch)
            print(f"    → {total}/{len(rows)} 行...", end='\r')
        await conn.commit()

    print(f"    ✅ {total} 行已导入")
    return total


async def main():
    print("📦 导入 Mock 数据到 MySQL\n")

    mappings = [
        ('users',                'users.json'),
        ('items',                'items.json'),
        ('knowledge_documents',  'documents.json'),
        ('cv_tasks',             'cv_tasks.json'),
        ('models',               'models.json'),
        ('training_jobs',        'training_jobs.json'),
        ('user_behaviors',       'behaviors.json'),
        ('inference_logs',       'inference_logs.json'),
    ]

    data_files = set(os.listdir(DATA_DIR))

    for table, filename in mappings:
        if filename in data_files:
            filepath = os.path.join(DATA_DIR, filename)
            print(f"📄 {table} ← {filename}")
            await import_json(table, filepath)
        else:
            print(f"⏭️  {table} — 跳过（{filename} 不存在）")

    print("\n📊 验证:")
    async with _db_manager.engine.connect() as conn:
        result = await conn.execute(text("""
            SELECT TABLE_NAME, TABLE_ROWS
            FROM information_schema.TABLES
            WHERE TABLE_SCHEMA = DATABASE()
              AND TABLE_TYPE = 'BASE TABLE'
            ORDER BY TABLE_NAME
        """))
        for row in result:
            print(f"  {row[0]}: {row[1]}")

    await _db_manager.engine.dispose()
    print("\n🎉 完成!")


if __name__ == '__main__':
    asyncio.run(main())
