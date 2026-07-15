<template>
  <div class="ab-page">
    <div class="toolbar">
      <el-button type="primary" @click="createDialogVisible = true">
        <el-icon><Plus /></el-icon> 创建实验
      </el-button>
    </div>

    <el-table :data="experiments" style="width: 100%; margin-top: 16px">
      <el-table-column prop="name" label="实验名称" min-width="200" />
      <el-table-column prop="model_a" label="模型 A" width="150" />
      <el-table-column prop="model_b" label="模型 B" width="150" />
      <el-table-column prop="traffic_split" label="流量分配" width="120" align="center">
        <template #default="{ row }">
          {{ (row.traffic_split * 100).toFixed(0) }}% / {{ ((1 - row.traffic_split) * 100).toFixed(0) }}%
        </template>
      </el-table-column>
      <el-table-column prop="status" label="状态" width="100">
        <template #default="{ row }">
          <el-tag :type="row.status === 'running' ? 'success' : row.status === 'completed' ? 'info' : 'warning'" size="small">
            {{ { running: '运行中', completed: '已完成', draft: '草稿' }[row.status] }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column label="结果对比" min-width="250">
        <template #default="{ row }">
          <div class="result-compare">
            <span>A: {{ (row.metrics.accuracy_a * 100).toFixed(1) }}%</span>
            <span>B: {{ (row.metrics.accuracy_b * 100).toFixed(1) }}%</span>
            <el-tag :type="row.metrics.p_value < 0.05 ? 'success' : 'warning'" size="small">
              p={{ row.metrics.p_value.toFixed(4) }}
            </el-tag>
          </div>
        </template>
      </el-table-column>
      <el-table-column label="操作" width="150" fixed="right">
        <template #default="{ row }">
          <el-button v-if="row.status === 'draft'" type="success" link size="small">启动</el-button>
          <el-button v-if="row.status === 'running'" type="warning" link size="small">停止</el-button>
          <el-button type="primary" link size="small">详情</el-button>
        </template>
      </el-table-column>
    </el-table>

    <!-- 创建实验对话框 -->
    <el-dialog v-model="createDialogVisible" title="创建 A/B 实验" width="550px">
      <el-form :model="createForm" label-width="100px">
        <el-form-item label="实验名称" required>
          <el-input v-model="createForm.name" placeholder="如: 推荐算法v2 vs v3" />
        </el-form-item>
        <el-form-item label="模型 A" required>
          <el-select v-model="createForm.modelA" style="width: 100%">
            <el-option label="协同过滤 v2.1" value="model_0001" />
            <el-option label="混合推荐 v1.5" value="model_0002" />
            <el-option label="深度学习 v3.0" value="model_0003" />
          </el-select>
        </el-form-item>
        <el-form-item label="模型 B" required>
          <el-select v-model="createForm.modelB" style="width: 100%">
            <el-option label="协同过滤 v2.2" value="model_0004" />
            <el-option label="混合推荐 v2.0" value="model_0005" />
            <el-option label="深度学习 v3.1" value="model_0006" />
          </el-select>
        </el-form-item>
        <el-form-item label="流量分配">
          <el-slider v-model="createForm.trafficSplit" :min="0.1" :max="0.9" :step="0.1" show-input />
        </el-form-item>
        <el-form-item label="评估指标">
          <el-checkbox-group v-model="createForm.metrics">
            <el-checkbox label="accuracy">准确率</el-checkbox>
            <el-checkbox label="latency">延迟</el-checkbox>
            <el-checkbox label="throughput">吞吐量</el-checkbox>
            <el-checkbox label="ctr">点击率</el-checkbox>
          </el-checkbox-group>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="createDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="createExperiment">创建实验</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { ElMessage } from 'element-plus'

const createDialogVisible = ref(false)
const createForm = ref({
  name: '',
  modelA: '',
  modelB: '',
  trafficSplit: 0.5,
  metrics: ['accuracy', 'latency'],
})

const experiments = ref([
  { name: '推荐算法 v2.1 vs v2.2', model_a: '协同过滤 v2.1', model_b: '协同过滤 v2.2', traffic_split: 0.5, status: 'running', metrics: { accuracy_a: 0.875, accuracy_b: 0.892, latency_a_ms: 8.2, latency_b_ms: 7.8, p_value: 0.023 } },
  { name: '混合推荐 vs 深度学习', model_a: '混合推荐 v1.5', model_b: '深度学习 v3.0', traffic_split: 0.3, status: 'running', metrics: { accuracy_a: 0.918, accuracy_b: 0.932, latency_a_ms: 15.0, latency_b_ms: 45.0, p_value: 0.041 } },
  { name: '特征工程优化实验', model_a: '协同过滤 v2.0', model_b: '协同过滤 v2.1', traffic_split: 0.5, status: 'completed', metrics: { accuracy_a: 0.861, accuracy_b: 0.875, latency_a_ms: 9.1, latency_b_ms: 8.2, p_value: 0.008 } },
])

function createExperiment() {
  ElMessage.success('实验创建成功')
  createDialogVisible.value = false
}
</script>

<style scoped>
.toolbar { display: flex; align-items: center; }
.result-compare { display: flex; gap: 12px; align-items: center; font-size: 13px; }
</style>
