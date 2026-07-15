<template>
  <div class="models-page">
    <div class="toolbar">
      <el-button type="primary" @click="registerDialog = true"><el-icon><Plus /></el-icon> 注册模型</el-button>
      <el-select v-model="statusFilter" placeholder="状态" style="width:140px;margin-left:12px" clearable>
        <el-option label="全部" value="" />
        <el-option label="开发中" value="development" />
        <el-option label="预发布" value="staging" />
        <el-option label="生产中" value="production" />
        <el-option label="已归档" value="archived" />
      </el-select>
    </div>

    <el-table :data="models" style="width:100%;margin-top:16px">
      <el-table-column prop="name" label="模型名称" min-width="180" />
      <el-table-column prop="version" label="版本" width="100" />
      <el-table-column prop="model_type" label="类型" width="120">
        <template #default="{ row }"><el-tag size="small">{{ row.model_type }}</el-tag></template>
      </el-table-column>
      <el-table-column prop="framework" label="框架" width="100" />
      <el-table-column prop="status" label="状态" width="100">
        <template #default="{ row }">
          <el-tag :type="statusColor(row.status)" size="small">{{ statusLabel(row.status) }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column label="指标" min-width="200">
        <template #default="{ row }">
          <span class="metrics-text">
            准确率 {{ (row.metrics.accuracy * 100).toFixed(1) }}% | F1 {{ (row.metrics.f1_score * 100).toFixed(1) }}% | P50 {{ row.metrics.latency_p50_ms }}ms
          </span>
        </template>
      </el-table-column>
      <el-table-column label="操作" width="220" fixed="right">
        <template #default="{ row }">
          <el-button type="primary" link size="small">详情</el-button>
          <el-button v-if="row.status === 'development'" type="success" link size="small">发布预发</el-button>
          <el-button v-if="row.status === 'staging'" type="warning" link size="small">推全</el-button>
          <el-button type="danger" link size="small">归档</el-button>
        </template>
      </el-table-column>
    </el-table>

    <el-dialog v-model="registerDialog" title="注册新模型" width="500px" :teleported="false">
      <el-form :model="form" label-width="100px">
        <el-form-item label="模型名称" required><el-input v-model="form.name" /></el-form-item>
        <el-form-item label="版本" required><el-input v-model="form.version" placeholder="如 1.0.0" /></el-form-item>
        <el-form-item label="模型类型"><el-select v-model="form.type" style="width:100%"><el-option v-for="t in ['classification','detection','nlp','recommendation','custom']" :key="t" :label="t" :value="t" /></el-select></el-form-item>
        <el-form-item label="框架"><el-select v-model="form.framework" style="width:100%"><el-option v-for="f in ['pytorch','tensorflow','onnx','sklearn']" :key="f" :label="f" :value="f" /></el-select></el-form-item>
        <el-form-item label="描述"><el-input v-model="form.desc" type="textarea" :rows="2" /></el-form-item>
      </el-form>
      <template #footer><el-button @click="registerDialog = false">取消</el-button><el-button type="primary" @click="registerDialog = false">注册</el-button></template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
const registerDialog = ref(false)
const statusFilter = ref('')
const form = ref({ name: '', version: '1.0.0', type: 'classification', framework: 'pytorch', desc: '' })
const statusColor = (s: string) => ({ development: 'info', staging: 'warning', production: 'success', archived: '' } as any)[s] || 'info'
const statusLabel = (s: string) => ({ development: '开发中', staging: '预发布', production: '生产中', archived: '已归档' } as any)[s] || s
const models = ref(Array.from({ length: 15 }, (_, i) => ({
  name: ['bert-classifier','resnet-detector','xgboost-ranker','gpt-rag','lstm-forecaster'][i % 5],
  version: `v${Math.floor(i/3)+1}.${i%3}.0`,
  model_type: ['classification','detection','nlp','recommendation'][i % 4],
  framework: ['pytorch','tensorflow','onnx','sklearn'][i % 4],
  status: ['development','staging','production','archived'][i % 4],
  metrics: { accuracy: 0.8 + Math.random() * 0.18, f1_score: 0.78 + Math.random() * 0.2, latency_p50_ms: Math.round(Math.random() * 50 + 5), latency_p99_ms: Math.round(Math.random() * 200 + 50) },
})))
</script>

<style scoped>
.toolbar { display: flex; align-items: center; }
.metrics-text { font-size: 12px; color: #909399; font-family: monospace; }
</style>
