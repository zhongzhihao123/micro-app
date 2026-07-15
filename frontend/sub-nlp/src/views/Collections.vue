<template>
  <div class="collections-page">
    <div class="toolbar">
      <el-button type="primary" @click="createDialogVisible = true">
        <el-icon><Plus /></el-icon> 创建集合
      </el-button>
    </div>

    <el-table :data="collections" style="width: 100%; margin-top: 16px" v-loading="loading">
      <el-table-column prop="name" label="集合名称" min-width="200" />
      <el-table-column prop="description" label="描述" min-width="250" />
      <el-table-column prop="entity_count" label="向量数量" width="120" align="right" />
      <el-table-column prop="dimension" label="维度" width="100" align="center" />
      <el-table-column prop="index_type" label="索引类型" width="120" />
      <el-table-column prop="metric" label="度量方式" width="100" />
      <el-table-column prop="created_at" label="创建时间" width="180" />
      <el-table-column label="操作" width="180" fixed="right">
        <template #default="{ row }">
          <el-button type="primary" link size="small">详情</el-button>
          <el-button type="danger" link size="small" @click="deleteCollection(row)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>

    <!-- 创建对话框 -->
    <el-dialog v-model="createDialogVisible" title="创建知识库集合" width="500px" :teleported="false">
      <el-form :model="createForm" label-width="100px">
        <el-form-item label="集合名称" required>
          <el-input v-model="createForm.name" placeholder="英文名称，如 tech_docs" />
        </el-form-item>
        <el-form-item label="描述">
          <el-input v-model="createForm.description" type="textarea" :rows="2" />
        </el-form-item>
        <el-form-item label="向量维度">
          <el-input-number v-model="createForm.dimension" :min="128" :max="4096" :step="128" />
        </el-form-item>
        <el-form-item label="索引类型">
          <el-select v-model="createForm.indexType">
            <el-option label="IVF_FLAT" value="IVF_FLAT" />
            <el-option label="IVF_SQ8" value="IVF_SQ8" />
            <el-option label="HNSW" value="HNSW" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="createDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="createCollection">创建</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'

const loading = ref(false)
const createDialogVisible = ref(false)
const createForm = ref({
  name: '',
  description: '',
  dimension: 1536,
  indexType: 'IVF_FLAT',
})

const collections = ref([
  { name: 'aisys_default_kb', description: '默认知识库', entity_count: 485000, dimension: 1536, index_type: 'IVF_FLAT', metric: 'COSINE', created_at: '2024-07-01 10:00' },
  { name: 'aisys_tech_docs', description: '技术文档库', entity_count: 120000, dimension: 1536, index_type: 'HNSW', metric: 'COSINE', created_at: '2024-07-05 14:30' },
  { name: 'aisys_product_docs', description: '产品需求文档库', entity_count: 85000, dimension: 1536, index_type: 'IVF_FLAT', metric: 'IP', created_at: '2024-07-08 09:15' },
])

function createCollection() {
  if (!createForm.value.name) {
    ElMessage.warning('请输入集合名称')
    return
  }
  ElMessage.success(`集合 ${createForm.value.name} 创建成功`)
  createDialogVisible.value = false
}

async function deleteCollection(row: any) {
  await ElMessageBox.confirm(`确定要删除集合 "${row.name}" 吗？所有向量数据将丢失！`, '危险操作', { type: 'error' })
  ElMessage.success('集合已删除')
}
</script>

<style scoped>
.collections-page {
  padding: 0;
}

.toolbar {
  display: flex;
  align-items: center;
}
</style>
