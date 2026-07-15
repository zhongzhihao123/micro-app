<template>
  <div class="training-page">
    <div class="toolbar">
      <el-button type="primary" @click="submitDialog = true"><el-icon><Plus /></el-icon> 提交训练任务</el-button>
    </div>

    <el-table :data="jobs" style="width:100%;margin-top:16px">
      <el-table-column prop="job_name" label="任务名称" min-width="200" />
      <el-table-column prop="status" label="状态" width="100">
        <template #default="{ row }">
          <el-tag :type="jobStatusColor(row.status)" size="small">{{ jobStatusLabel(row.status) }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column label="配置" min-width="200">
        <template #default="{ row }">
          <span class="config-text">epochs: {{ row.config.epochs }}, batch: {{ row.config.batch_size }}, lr: {{ row.config.learning_rate }}</span>
        </template>
      </el-table-column>
      <el-table-column label="指标" min-width="200">
        <template #default="{ row }">
          <span v-if="Object.keys(row.metrics).length" class="metrics-text">
            loss: {{ row.metrics.train_loss?.toFixed(4) }} | val_acc: {{ ((row.metrics.val_accuracy || 0) * 100).toFixed(1) }}%
          </span>
          <span v-else class="no-metrics">-</span>
        </template>
      </el-table-column>
      <el-table-column prop="started_at" label="开始时间" width="180" />
      <el-table-column label="操作" width="120">
        <template #default="{ row }">
          <el-button type="primary" link size="small">详情</el-button>
          <el-button v-if="row.status === 'running'" type="danger" link size="small">停止</el-button>
        </template>
      </el-table-column>
    </el-table>

    <el-dialog v-model="submitDialog" title="提交训练任务" width="500px" :teleported="false">
      <el-form :model="trainForm" label-width="120px">
        <el-form-item label="模型名称" required><el-input v-model="trainForm.modelName" /></el-form-item>
        <el-form-item label="版本"><el-input v-model="trainForm.version" /></el-form-item>
        <el-form-item label="训练轮数"><el-input-number v-model="trainForm.epochs" :min="1" :max="1000" /></el-form-item>
        <el-form-item label="批次大小"><el-select v-model="trainForm.batchSize"><el-option v-for="b in [16,32,64,128,256]" :key="b" :label="b" :value="b" /></el-select></el-form-item>
        <el-form-item label="学习率"><el-input v-model="trainForm.lr" placeholder="1e-4" /></el-form-item>
        <el-form-item label="优先级"><el-slider v-model="trainForm.priority" :min="0" :max="10" show-input /></el-form-item>
      </el-form>
      <template #footer><el-button @click="submitDialog = false">取消</el-button><el-button type="primary" @click="submitDialog = false">提交</el-button></template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
const submitDialog = ref(false)
const trainForm = ref({ modelName: '', version: 'v1.0', epochs: 50, batchSize: 32, lr: '1e-4', priority: 5 })
const jobStatusColor = (s: string) => ({ queued: 'info', running: 'warning', completed: 'success', failed: 'danger', cancelled: '' } as any)[s] || 'info'
const jobStatusLabel = (s: string) => ({ queued: '排队中', running: '运行中', completed: '已完成', failed: '失败', cancelled: '已取消' } as any)[s] || s
const jobs = ref(Array.from({ length: 12 }, (_, i) => ({
  job_name: `training-run-${String(i+1).padStart(3,'0')}`,
  status: ['completed','running','failed','queued'][i % 4],
  config: { epochs: [30,50,100][i%3], batch_size: [16,32,64][i%3], learning_rate: [1e-4,1e-5,3e-4][i%3] },
  metrics: i % 4 !== 2 ? { train_loss: Math.round((Math.random() * 1.5 + 0.1) * 10000) / 10000, val_loss: Math.round((Math.random() * 2 + 0.2) * 10000) / 10000, val_accuracy: Math.round((Math.random() * 0.2 + 0.75) * 10000) / 10000 } : {},
  started_at: new Date(Date.now() - (i+1)*3600000).toISOString().replace('T',' ').substring(0,19),
})))
</script>

<style scoped>
.toolbar { display: flex; align-items: center; }
.config-text, .metrics-text { font-size: 12px; color: #909399; font-family: monospace; }
.no-metrics { color: #C0C4CC; }
</style>
