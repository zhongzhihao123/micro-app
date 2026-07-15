-- ============================================================
-- AI System Platform - MySQL Database Initialization
-- ============================================================

-- 用户表
CREATE TABLE IF NOT EXISTS users (
    id CHAR(36) PRIMARY KEY DEFAULT (UUID()),
    username VARCHAR(100) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    role VARCHAR(20) DEFAULT 'user',
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- API Key 表
CREATE TABLE IF NOT EXISTS api_keys (
    id CHAR(36) PRIMARY KEY DEFAULT (UUID()),
    user_id CHAR(36) NOT NULL,
    key_hash VARCHAR(255) UNIQUE NOT NULL,
    name VARCHAR(100) NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    last_used_at TIMESTAMP NULL,
    expires_at TIMESTAMP NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- ==================== NLP 知识库 ====================

-- 知识库文档
CREATE TABLE IF NOT EXISTS knowledge_documents (
    id CHAR(36) PRIMARY KEY DEFAULT (UUID()),
    user_id CHAR(36),
    title VARCHAR(500) NOT NULL,
    content LONGTEXT,
    file_type VARCHAR(50),
    file_size BIGINT,
    chunk_count INT DEFAULT 0,
    status VARCHAR(20) DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL
);

-- 文档分块
CREATE TABLE IF NOT EXISTS document_chunks (
    id CHAR(36) PRIMARY KEY DEFAULT (UUID()),
    document_id CHAR(36) NOT NULL,
    chunk_index INT NOT NULL,
    content LONGTEXT NOT NULL,
    token_count INT DEFAULT 0,
    milvus_id BIGINT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (document_id) REFERENCES knowledge_documents(id) ON DELETE CASCADE
);

-- 对话历史
CREATE TABLE IF NOT EXISTS conversations (
    id CHAR(36) PRIMARY KEY DEFAULT (UUID()),
    user_id CHAR(36),
    title VARCHAR(500),
    model VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL
);

CREATE TABLE IF NOT EXISTS messages (
    id CHAR(36) PRIMARY KEY DEFAULT (UUID()),
    conversation_id CHAR(36) NOT NULL,
    role VARCHAR(20) NOT NULL,
    content LONGTEXT NOT NULL,
    token_count INT DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (conversation_id) REFERENCES conversations(id) ON DELETE CASCADE
);

-- ==================== 推荐系统 ====================

-- 商品/内容
CREATE TABLE IF NOT EXISTS items (
    id CHAR(36) PRIMARY KEY DEFAULT (UUID()),
    title VARCHAR(500) NOT NULL,
    description TEXT,
    category VARCHAR(100),
    tags JSON,
    price DECIMAL(10,2),
    metadata JSON,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 用户行为
CREATE TABLE IF NOT EXISTS user_behaviors (
    id CHAR(36) PRIMARY KEY DEFAULT (UUID()),
    user_id CHAR(36) NOT NULL,
    item_id CHAR(36) NOT NULL,
    behavior_type VARCHAR(20) NOT NULL,
    weight DECIMAL(5,2) DEFAULT 1.0,
    session_id VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (item_id) REFERENCES items(id) ON DELETE CASCADE
);

-- 推荐结果缓存
CREATE TABLE IF NOT EXISTS recommendations (
    id CHAR(36) PRIMARY KEY DEFAULT (UUID()),
    user_id CHAR(36) NOT NULL,
    item_ids JSON NOT NULL,
    scores JSON,
    algorithm VARCHAR(50),
    expires_at TIMESTAMP NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- ==================== 计算机视觉 ====================

-- 图像任务
CREATE TABLE IF NOT EXISTS cv_tasks (
    id CHAR(36) PRIMARY KEY DEFAULT (UUID()),
    user_id CHAR(36),
    task_type VARCHAR(50) NOT NULL,
    image_url TEXT,
    status VARCHAR(20) DEFAULT 'pending',
    result JSON,
    processing_time_ms INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP NULL,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL
);

-- 检测结果
CREATE TABLE IF NOT EXISTS detection_results (
    id CHAR(36) PRIMARY KEY DEFAULT (UUID()),
    task_id CHAR(36) NOT NULL,
    label VARCHAR(200) NOT NULL,
    confidence DECIMAL(5,4),
    bbox JSON,
    metadata JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (task_id) REFERENCES cv_tasks(id) ON DELETE CASCADE
);

-- ==================== MLOps 平台 ====================

-- 模型注册
CREATE TABLE IF NOT EXISTS models (
    id CHAR(36) PRIMARY KEY DEFAULT (UUID()),
    name VARCHAR(200) NOT NULL,
    version VARCHAR(50) NOT NULL,
    model_type VARCHAR(50) NOT NULL,
    framework VARCHAR(50),
    description TEXT,
    parameters JSON,
    metrics JSON,
    artifact_path TEXT,
    status VARCHAR(20) DEFAULT 'development',
    created_by CHAR(36),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY uk_name_version (name, version),
    FOREIGN KEY (created_by) REFERENCES users(id)
);

-- 训练任务
CREATE TABLE IF NOT EXISTS training_jobs (
    id CHAR(36) PRIMARY KEY DEFAULT (UUID()),
    model_id CHAR(36),
    job_name VARCHAR(200) NOT NULL,
    status VARCHAR(20) DEFAULT 'queued',
    config JSON,
    metrics JSON,
    started_at TIMESTAMP NULL,
    completed_at TIMESTAMP NULL,
    error_message TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (model_id) REFERENCES models(id) ON DELETE SET NULL
);

-- A/B 实验
CREATE TABLE IF NOT EXISTS ab_experiments (
    id CHAR(36) PRIMARY KEY DEFAULT (UUID()),
    name VARCHAR(200) NOT NULL,
    model_a_id CHAR(36),
    model_b_id CHAR(36),
    traffic_split DECIMAL(3,2) DEFAULT 0.50,
    status VARCHAR(20) DEFAULT 'draft',
    metrics JSON,
    started_at TIMESTAMP NULL,
    ended_at TIMESTAMP NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (model_a_id) REFERENCES models(id),
    FOREIGN KEY (model_b_id) REFERENCES models(id)
);

-- 推理日志
CREATE TABLE IF NOT EXISTS inference_logs (
    id CHAR(36) PRIMARY KEY DEFAULT (UUID()),
    model_id CHAR(36),
    request_id VARCHAR(100) UNIQUE,
    input_preview TEXT,
    output_preview TEXT,
    latency_ms INT,
    token_count INT,
    cost DECIMAL(10,6),
    is_error BOOLEAN DEFAULT FALSE,
    error_message TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (model_id) REFERENCES models(id) ON DELETE SET NULL
);

-- ==================== 索引 ====================
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_api_keys_user ON api_keys(user_id);
CREATE INDEX idx_documents_user ON knowledge_documents(user_id);
CREATE INDEX idx_documents_status ON knowledge_documents(status);
CREATE INDEX idx_chunks_document ON document_chunks(document_id);
CREATE INDEX idx_conversations_user ON conversations(user_id);
CREATE INDEX idx_messages_conversation ON messages(conversation_id);
CREATE INDEX idx_behaviors_user ON user_behaviors(user_id);
CREATE INDEX idx_behaviors_item ON user_behaviors(item_id);
CREATE INDEX idx_behaviors_type ON user_behaviors(behavior_type);
CREATE INDEX idx_behaviors_time ON user_behaviors(created_at);
CREATE INDEX idx_items_category ON items(category);
CREATE INDEX idx_cv_tasks_user ON cv_tasks(user_id);
CREATE INDEX idx_cv_tasks_type ON cv_tasks(task_type);
CREATE INDEX idx_models_name ON models(name);
CREATE INDEX idx_training_jobs_status ON training_jobs(status);
CREATE INDEX idx_inference_logs_model ON inference_logs(model_id);
CREATE INDEX idx_inference_logs_time ON inference_logs(created_at);

-- 插入默认管理员 (密码: admin123)
INSERT INTO users (id, username, email, hashed_password, role) 
VALUES (UUID(), 'admin', 'admin@ai-platform.local', '$2b$12$LJ3m4ys3Lk0TSwHCpNqrquV0YpZx4UqBw0GjRqJxpR3xV3vJ0z2Xe', 'admin')
ON DUPLICATE KEY UPDATE username = username;
