<template>
  <div class="knowledge-page">
    <!-- 操作栏 -->
    <div class="toolbar">
      <el-upload
        :auto-upload="false"
        :show-file-list="false"
        :on-change="handleFileSelect"
        accept=".pdf,.docx,.txt,.md,.html"
      >
        <el-button type="primary">
          <el-icon><Upload /></el-icon> 上传文档
        </el-button>
      </el-upload>

      <el-input
        v-model="searchQuery"
        placeholder="搜索文档..."
        :prefix-icon="Search"
        style="width: 300px; margin-left: 12px"
        clearable
      />

      <el-select v-model="statusFilter" placeholder="状态筛选" style="width: 140px; margin-left: 12px" clearable>
        <el-option label="全部" value="" />
        <el-option label="处理中" value="processing" />
        <el-option label="已完成" value="completed" />
        <el-option label="失败" value="failed" />
      </el-select>
    </div>

    <!-- 文档列表 -->
    <el-table :data="documents" style="width: 100%; margin-top: 16px" v-loading="loading">
      <el-table-column prop="title" label="文档名称" min-width="250">
        <template #default="{ row }">
          <el-icon style="margin-right: 6px"><Document /></el-icon>
          {{ row.title }}
        </template>
      </el-table-column>
      <el-table-column prop="file_type" label="类型" width="100" />
      <el-table-column prop="file_size" label="大小" width="100">
        <template #default="{ row }">
          {{ formatSize(row.file_size) }}
        </template>
      </el-table-column>
      <el-table-column prop="chunk_count" label="分块数" width="100" />
      <el-table-column prop="status" label="状态" width="120">
        <template #default="{ row }">
          <el-tag :type="statusType(row.status)" size="small">
            {{ statusText(row.status) }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="created_at" label="上传时间" width="180" />
      <el-table-column label="操作" width="180" fixed="right">
        <template #default="{ row }">
          <el-button type="primary" link size="small" @click="viewDocument(row)">查看</el-button>
          <el-button type="danger" link size="small" @click="deleteDocument(row)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>

    <!-- 分页 -->
    <div class="pagination">
      <el-pagination
        v-model:current-page="page"
        :page-size="pageSize"
        :total="total"
        layout="total, prev, pager, next"
      />
    </div>

    <!-- 上传对话框 -->
    <el-dialog v-model="uploadDialogVisible" title="上传文档" width="500px" :teleported="false">
      <div class="upload-area">
        <el-icon :size="64" color="#C0C4CC"><UploadFilled /></el-icon>
        <p>将文件拖拽到此处，或点击选择文件</p>
        <p class="upload-hint">支持 PDF、DOCX、TXT、MD、HTML 格式</p>
      </div>
      <el-progress v-if="uploading" :percentage="uploadProgress" :status="uploadProgress === 100 ? 'success' : undefined" />
      <template #footer>
        <el-button @click="uploadDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="startUpload" :loading="uploading">开始上传</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { Search } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'

const loading = ref(false)
const searchQuery = ref('')
const statusFilter = ref('')
const page = ref(1)
const pageSize = ref(20)
const total = ref(0)
const uploadDialogVisible = ref(false)
const uploading = ref(false)
const uploadProgress = ref(0)
const selectedFile = ref<any>(null)

const documents = ref([
  { id: '1', title: 'AI平台架构设计文档.pdf', file_type: 'PDF', file_size: 2450000, chunk_count: 156, status: 'completed', created_at: '2024-07-14 10:30' },
  { id: '2', title: '产品需求说明书_v2.1.docx', file_type: 'DOCX', file_size: 1800000, chunk_count: 89, status: 'completed', created_at: '2024-07-13 15:20' },
  { id: '3', title: '系统运维手册.md', file_type: 'MD', file_size: 560000, chunk_count: 34, status: 'processing', created_at: '2024-07-14 09:15' },
  { id: '4', title: 'API接口文档.html', file_type: 'HTML', file_size: 3200000, chunk_count: 210, status: 'completed', created_at: '2024-07-12 08:00' },
  { id: '5', title: '会议纪要_20240710.txt', file_type: 'TXT', file_size: 120000, chunk_count: 8, status: 'failed', created_at: '2024-07-10 14:00' },
])

function formatSize(bytes: number): string {
  if (bytes < 1024) return bytes + ' B'
  if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB'
  return (bytes / (1024 * 1024)).toFixed(1) + ' MB'
}

function statusType(status: string): string {
  const map: Record<string, string> = { completed: 'success', processing: 'warning', failed: 'danger', pending: 'info' }
  return map[status] || 'info'
}

function statusText(status: string): string {
  const map: Record<string, string> = { completed: '已完成', processing: '处理中', failed: '失败', pending: '待处理' }
  return map[status] || status
}

function handleFileSelect(file: any) {
  selectedFile.value = file
  uploadDialogVisible.value = true
}

function startUpload() {
  uploading.value = true
  uploadProgress.value = 0
  const timer = setInterval(() => {
    uploadProgress.value += 10
    if (uploadProgress.value >= 100) {
      clearInterval(timer)
      uploading.value = false
      uploadDialogVisible.value = false
      ElMessage.success('文档上传成功，正在处理中...')
    }
  }, 300)
}

function viewDocument(row: any) {
  ElMessage.info(`查看文档: ${row.title}`)
}

async function deleteDocument(row: any) {
  await ElMessageBox.confirm(`确定要删除 "${row.title}" 吗？`, '确认删除', { type: 'warning' })
  ElMessage.success('文档已删除')
}
</script>

<style scoped>
.knowledge-page {
  padding: 0;
}

.toolbar {
  display: flex;
  align-items: center;
}

.upload-area {
  text-align: center;
  padding: 40px;
  border: 2px dashed #dcdfe6;
  border-radius: 8px;
  color: #909399;
}

.upload-hint {
  font-size: 12px;
  color: #C0C4CC;
  margin-top: 8px;
}

.pagination {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}
</style>
