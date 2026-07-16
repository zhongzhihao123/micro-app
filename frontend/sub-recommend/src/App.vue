<template>
  <div class="recommend-app">
    <div class="sub-app-header">
      <h2>🎯 智能推荐系统</h2>
      <el-tabs v-model="activeTab" @tab-click="handleTabClick">
        <el-tab-pane label="数据看板" name="dashboard" />
        <el-tab-pane label="商品管理" name="items" />
        <el-tab-pane label="用户行为" name="behavior" />
        <el-tab-pane label="A/B 实验" name="ab-test" />
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
const activeTab = ref('dashboard')

watch(() => route.path, (path) => {
  if (path.includes('items')) activeTab.value = 'items'
  else if (path.includes('behavior')) activeTab.value = 'behavior'
  else if (path.includes('ab-test')) activeTab.value = 'ab-test'
  else activeTab.value = 'dashboard'
}, { immediate: true })

function handleTabClick(tab: any) { router.push(`/${tab.props.name}`) }
</script>

<style scoped>
.recommend-app { height: 100%; background: #f5f7fa; padding: 16px; box-sizing: border-box; overflow: auto; }
.sub-app-header { background: #fff; padding: 20px 24px; border-radius: 8px; margin-bottom: 16px; box-shadow: 0 1px 4px rgba(0,0,0,0.06); }
.sub-app-header h2 { margin: 0 0 16px 0; font-size: 20px; color: #303133; }
.sub-app-content { background: #fff; padding: 24px; border-radius: 8px; min-height: 500px; box-shadow: 0 1px 4px rgba(0,0,0,0.06); }
</style>
