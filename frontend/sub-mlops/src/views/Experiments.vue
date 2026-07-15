<template>
  <div class="experiments-page">
    <div class="toolbar">
      <el-button type="primary"><el-icon><Plus /></el-icon> 创建实验</el-button>
    </div>
    <el-table :data="experiments" style="width:100%;margin-top:16px">
      <el-table-column prop="name" label="实验名称" min-width="200" />
      <el-table-column label="模型对比" width="200">
        <template #default="{ row }">A: {{ row.model_a }} vs B: {{ row.model_b }}</template>
      </el-table-column>
      <el-table-column prop="traffic_split" label="流量分配" width="120" align="center">
        <template #default="{ row }">{{ (row.traffic_split * 100).toFixed(0) }}% / {{ ((1 - row.traffic_split) * 100).toFixed(0) }}%</template>
      </el-table-column>
      <el-table-column prop="status" label="状态" width="100">
        <template #default="{ row }"><el-tag :type="row.status === 'running' ? 'success' : 'info'" size="small">{{ row.status === 'running' ? '运行中' : '已完成' }}</el-tag></template>
      </el-table-column>
      <el-table-column label="结果" min-width="250">
        <template #default="{ row }">
          <span class="result-text">A: {{ (row.metrics.accuracy_a * 100).toFixed(1) }}% | B: {{ (row.metrics.accuracy_b * 100).toFixed(1) }}% | p={{ row.metrics.p_value.toFixed(4) }}</span>
        </template>
      </el-table-column>
      <el-table-column label="操作" width="120">
        <template #default><el-button type="primary" link size="small">详情</el-button></template>
      </el-table-column>
    </el-table>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
const experiments = ref(Array.from({ length: 8 }, (_, i) => ({
  name: `实验-${['推荐算法优化','模型压缩对比','特征工程验证','超参调优','架构对比','数据增强','损失函数','优化器对比'][i]}`,
  model_a: `model_${String(i*2+1).padStart(4,'0')}`, model_b: `model_${String(i*2+2).padStart(4,'0')}`,
  traffic_split: [0.3,0.5,0.5,0.2,0.5,0.5,0.5,0.3][i],
  status: i < 3 ? 'running' : 'completed',
  metrics: { accuracy_a: 0.85 + Math.random() * 0.1, accuracy_b: 0.86 + Math.random() * 0.1, p_value: Math.random() * 0.1 },
})))
</script>

<style scoped>
.toolbar { display: flex; align-items: center; }
.result-text { font-size: 12px; color: #909399; font-family: monospace; }
</style>
