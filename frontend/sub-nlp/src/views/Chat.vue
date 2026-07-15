<template>
  <div class="chat-page">
    <div class="chat-container">
      <!-- 对话区 -->
      <div class="chat-messages" ref="messageContainer">
        <div v-for="(msg, idx) in messages" :key="idx" :class="['message', msg.role]">
          <div class="message-avatar">
            <el-avatar :size="36" :icon="msg.role === 'user' ? 'UserFilled' : 'Cpu'" />
          </div>
          <div class="message-content">
            <div class="message-text">{{ msg.content }}</div>
            <div v-if="msg.sources && msg.sources.length" class="message-sources">
              <div class="sources-title">📚 参考来源:</div>
              <div v-for="(src, i) in msg.sources" :key="i" class="source-item">
                <span class="source-index">[{{ i + 1 }}]</span>
                <span class="source-text">{{ src.content?.substring(0, 100) }}...</span>
                <span class="source-score">相关性: {{ (src.score * 100).toFixed(1) }}%</span>
              </div>
            </div>
          </div>
        </div>

        <div v-if="thinking" class="message assistant">
          <div class="message-avatar">
            <el-avatar :size="36" icon="Cpu" />
          </div>
          <div class="message-content">
            <div class="thinking-dots">
              <span></span><span></span><span></span>
            </div>
          </div>
        </div>
      </div>

      <!-- 输入区 -->
      <div class="chat-input">
        <el-input
          v-model="inputText"
          type="textarea"
          :rows="3"
          placeholder="输入问题，基于知识库进行智能问答..."
          @keydown.enter.exact.prevent="sendMessage"
        />
        <div class="input-actions">
          <div class="input-options">
            <el-select v-model="selectedCollection" size="small" style="width: 180px">
              <el-option label="默认知识库" value="default_kb" />
              <el-option label="技术文档库" value="tech_docs" />
              <el-option label="产品需求库" value="product_docs" />
            </el-select>
            <span class="option-label">Top-K:</span>
            <el-input-number v-model="topK" :min="1" :max="20" size="small" style="width: 100px" />
          </div>
          <el-button type="primary" @click="sendMessage" :loading="thinking">
            <el-icon><Promotion /></el-icon> 发送
          </el-button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, nextTick, onMounted } from 'vue'

const messages = ref<any[]>([])
const inputText = ref('')
const thinking = ref(false)
const selectedCollection = ref('default_kb')
const topK = ref(5)
const messageContainer = ref<HTMLElement>()

function scrollToBottom() {
  nextTick(() => {
    if (messageContainer.value) {
      messageContainer.value.scrollTop = messageContainer.value.scrollHeight
    }
  })
}

async function sendMessage() {
  const query = inputText.value.trim()
  if (!query || thinking.value) return

  messages.value.push({ role: 'user', content: query })
  inputText.value = ''
  thinking.value = true
  scrollToBottom()

  // 模拟 RAG 问答
  await new Promise(r => setTimeout(r, 1500))

  const mockAnswer = generateMockAnswer(query)
  const mockSources = [
    { content: `关于"${query}"的相关文档内容摘要...这是从知识库中检索到的第一条相关记录。`, score: 0.92 },
    { content: `第二条相关文档片段，包含与问题相关的技术细节和实现方案。`, score: 0.87 },
    { content: `第三条参考来源，提供了更多的背景信息和上下文说明。`, score: 0.81 },
  ]

  messages.value.push({
    role: 'assistant',
    content: mockAnswer,
    sources: mockSources,
  })
  thinking.value = false
  scrollToBottom()
}

function generateMockAnswer(query: string): string {
  const answers = [
    `根据知识库中的相关文档，关于"${query}"的问题，我找到了以下信息：\n\n首先，从架构设计文档来看，系统采用了微服务架构，通过 API 网关统一管理请求路由。\n\n其次，在实现层面，建议使用异步消息队列处理耗时任务，确保系统的响应速度。\n\n最后，从运维角度，需要配置完善的监控和告警机制，保障系统稳定性。\n\n如果您需要更详细的信息，可以进一步指定具体方向。`,
    `基于知识库检索结果，针对"${query}"的回答如下：\n\n1. **技术选型**：推荐使用 FastAPI 作为后端框架，配合 PostgreSQL 存储业务数据。\n2. **向量检索**：文档通过 text-embedding-3-small 模型向量化后存入 Milvus，支持高效的语义搜索。\n3. **问答流程**：检索 Top-K 相关文档片段 → 构建 Prompt → LLM 生成回答。\n\n以上信息均来自已上传的技术文档。`,
  ]
  return answers[Math.floor(Math.random() * answers.length)]
}

onMounted(() => {
  messages.value.push({
    role: 'assistant',
    content: '👋 你好！我是 AI 知识库助手。你可以向我提问任何关于已上传文档的问题，我会基于知识库内容为你提供准确的回答。',
  })
})
</script>

<style scoped>
.chat-page {
  height: calc(100vh - 250px);
  min-height: 500px;
}

.chat-container {
  display: flex;
  flex-direction: column;
  height: 100%;
  border: 1px solid #ebeef5;
  border-radius: 8px;
  overflow: hidden;
}

.chat-messages {
  flex: 1;
  overflow-y: auto;
  padding: 20px;
  background: #fafafa;
}

.message {
  display: flex;
  gap: 12px;
  margin-bottom: 20px;
}

.message.user {
  flex-direction: row-reverse;
}

.message.user .message-content {
  background: #409EFF;
  color: #fff;
  border-radius: 12px 4px 12px 12px;
}

.message.assistant .message-content {
  background: #fff;
  border: 1px solid #ebeef5;
  border-radius: 4px 12px 12px 12px;
}

.message-content {
  padding: 12px 16px;
  max-width: 75%;
  line-height: 1.6;
}

.message-text {
  white-space: pre-wrap;
}

.message-sources {
  margin-top: 12px;
  padding-top: 12px;
  border-top: 1px solid #ebeef5;
  font-size: 12px;
}

.sources-title {
  color: #909399;
  margin-bottom: 6px;
}

.source-item {
  display: flex;
  gap: 8px;
  margin-bottom: 4px;
  color: #606266;
}

.source-index {
  color: #409EFF;
  font-weight: 600;
}

.source-score {
  color: #67C23A;
  white-space: nowrap;
}

.thinking-dots {
  display: flex;
  gap: 6px;
  padding: 4px 0;
}

.thinking-dots span {
  width: 8px;
  height: 8px;
  background: #909399;
  border-radius: 50%;
  animation: bounce 1.4s infinite ease-in-out both;
}

.thinking-dots span:nth-child(1) { animation-delay: -0.32s; }
.thinking-dots span:nth-child(2) { animation-delay: -0.16s; }

@keyframes bounce {
  0%, 80%, 100% { transform: scale(0); }
  40% { transform: scale(1); }
}

.chat-input {
  border-top: 1px solid #ebeef5;
  padding: 16px;
  background: #fff;
}

.input-actions {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 10px;
}

.input-options {
  display: flex;
  align-items: center;
  gap: 8px;
}

.option-label {
  font-size: 13px;
  color: #909399;
}
</style>
