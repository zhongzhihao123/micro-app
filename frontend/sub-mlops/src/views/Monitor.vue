<template>
  <div class="monitor-page">
    <!-- 概览卡片 -->
    <el-row :gutter="16" class="overview-row">
      <el-col :span="6" v-for="m in overview" :key="m.label">
        <el-card shadow="hover" class="overview-card">
          <div class="overview-label">{{ m.label }}</div>
          <div class="overview-value" :style="{color:m.color}">{{ m.value }}</div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 资源 & 推理统计 -->
    <el-row :gutter="16">
      <el-col :span="12">
        <el-card shadow="hover">
          <template #header><span class="card-title">💻 资源使用</span></template>
          <div class="resource-list">
            <div v-for="r in resources" :key="r.name" class="resource-item">
              <div class="resource-header"><span>{{ r.name }}</span><span>{{ r.percent }}%</span></div>
              <el-progress :percentage="r.percent" :color="r.color" :stroke-width="12" />
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="12">
        <el-card shadow="hover">
          <template #header><span class="card-title">📊 推理统计 (24h)</span></template>
          <div class="inference-stats">
            <div class="stat-row"><span>总请求数</span><strong>{{ formatNum(inference.total_requests) }}</strong></div>
            <div class="stat-row"><span>平均延迟</span><strong>{{ inference.avg_latency }}ms</strong></div>
            <div class="stat-row"><span>P99 延迟</span><strong>{{ inference.p99_latency }}ms</strong></div>
            <div class="stat-row"><span>错误率</span><strong :style="{color:inference.error_rate > 0.01 ? '#F56C6C' : '#67C23A'}">{{ (inference.error_rate * 100).toFixed(2) }}%</strong></div>
            <div class="stat-row"><span>今日费用</span><strong>${{ inference.cost.toFixed(2) }}</strong></div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 漂移告警 -->
    <el-card shadow="hover" style="margin-top:16px">
      <template #header><span class="card-title">⚠️ 模型漂移检测</span></template>
      <el-table :data="driftAlerts" style="width:100%">
        <el-table-column prop="model_name" label="模型" min-width="180" />
        <el-table-column prop="drift_score" label="漂移分数" width="120" align="center">
          <template #default="{ row }">
            <el-progress :percentage="Math.round(row.drift_score * 100)" :stroke-width="8" :color="row.drift_score > 0.15 ? '#F56C6C' : '#67C23A'" />
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="row.status === 'warning' ? 'danger' : 'success'" size="small">{{ row.status === 'warning' ? '⚠ 告警' : '✓ 正常' }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="建议" min-width="250">
          <template #default="{ row }">{{ row.drift_score > 0.15 ? '建议触发模型重训练，当前性能已出现明显下降' : '模型表现稳定，无需操作' }}</template>
        </el-table-column>
        <el-table-column label="操作" width="120">
          <template #default><el-button type="primary" link size="small">查看详情</el-button></template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 推理日志 -->
    <el-card shadow="hover" style="margin-top:16px">
      <template #header><span class="card-title">📋 最近推理日志</span></template>
      <el-table :data="logs" style="width:100%" max-height="350">
        <el-table-column prop="model_id" label="模型ID" width="150" />
        <el-table-column prop="latency_ms" label="延迟" width="100" align="right">
          <template #default="{ row }">{{ row.latency_ms }}ms</template>
        </el-table-column>
        <el-table-column prop="token_count" label="Token数" width="100" align="right" />
        <el-table-column prop="cost" label="费用" width="100" align="right">
          <template #default="{ row }">${{ row.cost.toFixed(6) }}</template>
        </el-table-column>
        <el-table-column prop="is_error" label="状态" width="80">
          <template #default="{ row }"><el-tag :type="row.is_error ? 'danger' : 'success'" size="small">{{ row.is_error ? '失败' : '成功' }}</el-tag></template>
        </el-table-column>
        <el-table-column prop="created_at" label="时间" width="180" />
      </el-table>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
const formatNum = (n: number) => n >= 10000 ? (n/10000).toFixed(1) + '万' : String(n)
const overview = ref([
  { label: '生产模型数', value: '8', color: '#409EFF' },
  { label: '活跃实验', value: '3', color: '#67C23A' },
  { label: '24h 推理量', value: '32.5万', color: '#E6A23C' },
  { label: '系统可用率', value: '99.97%', color: '#F56C6C' },
])
const resources = ref([
  { name: 'CPU', percent: 42, color: '#409EFF' },
  { name: '内存', percent: 67, color: '#67C23A' },
  { name: 'GPU #1', percent: 35, color: '#E6A23C' },
  { name: 'GPU #2', percent: 78, color: '#F56C6C' },
])
const inference = ref({ total_requests: 325000, avg_latency: 23.5, p99_latency: 187.2, error_rate: 0.003, cost: 45.82 })
const driftAlerts = ref(Array.from({ length: 5 }, (_, i) => ({
  model_name: ['bert-classifier','resnet-detector','xgboost-ranker','gpt-rag','lstm-forecaster'][i],
  drift_score: Math.round(Math.random() * 3000) / 10000,
  status: Math.random() > 0.7 ? 'warning' : 'ok',
})))
const logs = ref(Array.from({ length: 20 }, () => ({
  model_id: `model_${String(Math.floor(Math.random()*20)+1).padStart(4,'0')}`,
  latency_ms: Math.round(Math.random() * 300 + 5),
  token_count: Math.floor(Math.random() * 3000 + 50),
  cost: Math.round(Math.random() * 500) / 10000,
  is_error: Math.random() < 0.03,
  created_at: new Date(Date.now() - Math.random() * 86400000).toISOString().replace('T',' ').substring(0,19),
})))
</script>

<style scoped>
.overview-row { margin-bottom: 16px; }
.overview-card { text-align: center; cursor: pointer; transition: transform 0.2s; }
.overview-card:hover { transform: translateY(-2px); }
.overview-label { font-size: 13px; color: #909399; margin-bottom: 8px; }
.overview-value { font-size: 28px; font-weight: 700; }
.card-title { font-size: 15px; font-weight: 600; }
.resource-list { display: flex; flex-direction: column; gap: 16px; }
.resource-header { display: flex; justify-content: space-between; margin-bottom: 6px; font-size: 13px; color: #606266; }
.inference-stats { display: flex; flex-direction: column; gap: 12px; }
.stat-row { display: flex; justify-content: space-between; font-size: 14px; }
.stat-row strong { font-family: monospace; }
</style>
