<template>
  <div class="mlops-app">
    <div class="sub-app-header">
      <h2>⚙️ MLOps 平台</h2>
      <el-tabs v-model="activeTab" @tab-click="handleTabClick">
        <el-tab-pane label="模型管理" name="models" />
        <el-tab-pane label="训练任务" name="training" />
        <el-tab-pane label="实验管理" name="experiments" />
        <el-tab-pane label="监控中心" name="monitor" />
      </el-tabs>
    </div>
    <div class="sub-app-content">
      <router-view />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
const route = useRoute()
const router = useRouter()
const activeTab = ref('models')
watch(() => route.path, (path) => {
  if (path.includes('training')) activeTab.value = 'training'
  else if (path.includes('experiments')) activeTab.value = 'experiments'
  else if (path.includes('monitor')) activeTab.value = 'monitor'
  else activeTab.value = 'models'
}, { immediate: true })
function handleTabClick(tab: any) { router.push(`/${tab.props.name}`) }
</script>

<style scoped>
.mlops-app { height: 100%; background: #f5f7fa; padding: 16px; box-sizing: border-box; overflow: auto; }
.sub-app-header { background: #fff; padding: 20px 24px; border-radius: 8px; margin-bottom: 16px; box-shadow: 0 1px 4px rgba(0,0,0,0.06); }
.sub-app-header h2 { margin: 0 0 16px 0; font-size: 20px; color: #303133; }
.sub-app-content { background: #fff; padding: 24px; border-radius: 8px; min-height: 500px; box-shadow: 0 1px 4px rgba(0,0,0,0.06); }
</style>
