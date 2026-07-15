<template>
  <div class="dashboard-page">
    <!-- KPI 卡片 -->
    <el-row :gutter="16" class="kpi-row">
      <el-col :span="6" v-for="kpi in kpis" :key="kpi.label">
        <el-card shadow="hover" class="kpi-card">
          <div class="kpi-content">
            <div class="kpi-label">{{ kpi.label }}</div>
            <div class="kpi-value" :style="{ color: kpi.color }">{{ kpi.value }}</div>
            <div class="kpi-trend">
              <el-icon :color="kpi.trend > 0 ? '#67C23A' : '#F56C6C'">
                <component :is="kpi.trend > 0 ? 'CaretTop' : 'CaretBottom'" />
              </el-icon>
              {{ Math.abs(kpi.trend) }}% vs 上周
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 推荐效果 & 算法对比 -->
    <el-row :gutter="16" class="chart-row">
      <el-col :span="16">
        <el-card shadow="hover">
          <template #header><span class="card-title">📈 推荐效果趋势</span></template>
          <div class="chart-placeholder">
            <div class="mock-chart">
              <div v-for="(bar, i) in mockBars" :key="i" class="chart-bar-group">
                <div class="bar" :style="{ height: bar.clickRate * 200 + 'px', background: '#409EFF' }" />
                <div class="bar-label">{{ bar.date }}</div>
              </div>
            </div>
            <div class="chart-legend">
              <span class="legend-item"><span class="dot" style="background:#409EFF" /> 点击率</span>
              <span class="legend-item"><span class="dot" style="background:#67C23A" /> 转化率</span>
              <span class="legend-item"><span class="dot" style="background:#E6A23C" /> 覆盖率</span>
            </div>
          </div>
        </el-card>
      </el-col>

      <el-col :span="8">
        <el-card shadow="hover">
          <template #header><span class="card-title">⚡ 算法性能对比</span></template>
          <div class="algo-list">
            <div v-for="algo in algorithms" :key="algo.name" class="algo-item">
              <div class="algo-header">
                <span class="algo-name">{{ algo.name }}</span>
                <el-tag :type="algo.status === 'online' ? 'success' : 'info'" size="small">{{ algo.status === 'online' ? '在线' : '离线' }}</el-tag>
              </div>
              <div class="algo-metrics">
                <span>准确率 {{ algo.accuracy }}%</span>
                <span>召回率 {{ algo.recall }}%</span>
                <span>延迟 {{ algo.latency }}ms</span>
              </div>
              <el-progress :percentage="algo.accuracy" :stroke-width="6" :color="algo.color" />
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'

const kpis = ref([
  { label: '日均推荐请求', value: '85.2万', trend: 12.5, color: '#409EFF' },
  { label: '平均点击率', value: '12.4%', trend: 3.2, color: '#67C23A' },
  { label: '转化率', value: '5.8%', trend: -1.5, color: '#E6A23C' },
  { label: '推荐覆盖率', value: '78.3%', trend: 5.8, color: '#F56C6C' },
])

const algorithms = ref([
  { name: '协同过滤', status: 'online', accuracy: 87.5, recall: 82.3, latency: 8, color: '#409EFF' },
  { name: '内容推荐', status: 'online', accuracy: 85.2, recall: 79.8, latency: 12, color: '#67C23A' },
  { name: '混合推荐', status: 'online', accuracy: 91.8, recall: 88.5, latency: 15, color: '#E6A23C' },
  { name: '深度学习', status: 'offline', accuracy: 93.2, recall: 90.1, latency: 45, color: '#F56C6C' },
])

const mockBars = Array.from({ length: 14 }, (_, i) => ({
  date: `${i + 1}日`,
  clickRate: 0.08 + Math.random() * 0.08,
}))
</script>

<style scoped>
.kpi-row { margin-bottom: 16px; }
.kpi-card { cursor: pointer; transition: transform 0.2s; }
.kpi-card:hover { transform: translateY(-2px); }
.kpi-label { font-size: 13px; color: #909399; margin-bottom: 8px; }
.kpi-value { font-size: 28px; font-weight: 700; margin-bottom: 4px; }
.kpi-trend { font-size: 12px; color: #C0C4CC; display: flex; align-items: center; gap: 4px; }
.chart-row { margin-bottom: 16px; }
.card-title { font-size: 15px; font-weight: 600; }
.chart-placeholder { padding: 20px 0; }
.mock-chart { display: flex; align-items: flex-end; gap: 8px; height: 220px; padding: 0 20px; }
.chart-bar-group { flex: 1; display: flex; flex-direction: column; align-items: center; }
.bar { width: 100%; border-radius: 4px 4px 0 0; min-height: 4px; transition: height 0.3s; }
.bar-label { font-size: 11px; color: #909399; margin-top: 6px; }
.chart-legend { display: flex; gap: 20px; justify-content: center; margin-top: 16px; }
.legend-item { display: flex; align-items: center; gap: 6px; font-size: 12px; color: #606266; }
.dot { width: 10px; height: 10px; border-radius: 50%; }
.algo-list { display: flex; flex-direction: column; gap: 16px; }
.algo-item { padding: 12px; border: 1px solid #ebeef5; border-radius: 8px; }
.algo-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px; }
.algo-name { font-weight: 600; font-size: 14px; }
.algo-metrics { display: flex; gap: 12px; font-size: 12px; color: #909399; margin-bottom: 8px; }
</style>
