<template>
  <div class="nlp-app">
    <div class="sub-app-header">
      <h2>🧠 NLP 知识库问答系统</h2>
      <el-tabs v-model="activeTab" @tab-click="handleTabClick">
        <el-tab-pane label="知识库管理" name="knowledge" />
        <el-tab-pane label="智能问答" name="chat" />
        <el-tab-pane label="集合管理" name="collections" />
      </el-tabs>
    </div>
    <div class="sub-app-content">
      <router-view />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'

const router = useRouter()
const route = useRoute()

const activeTab = ref('knowledge')

watch(() => route.path, (path) => {
  if (path.includes('chat')) activeTab.value = 'chat'
  else if (path.includes('collections')) activeTab.value = 'collections'
  else activeTab.value = 'knowledge'
}, { immediate: true })

function handleTabClick(tab: any) {
  router.push(`/${tab.props.name}`)
}
</script>

<style scoped>
.nlp-app {
  height: 100%;
  background: #f5f7fa;
  padding: 16px;
  box-sizing: border-box;
  overflow: auto;
}

.sub-app-header {
  background: #fff;
  padding: 20px 24px;
  border-radius: 8px;
  margin-bottom: 16px;
  box-shadow: 0 1px 4px rgba(0,0,0,0.06);
}

.sub-app-header h2 {
  margin: 0 0 16px 0;
  font-size: 20px;
  color: #303133;
}

.sub-app-content {
  background: #fff;
  padding: 24px;
  border-radius: 8px;
  min-height: 500px;
  box-shadow: 0 1px 4px rgba(0,0,0,0.06);
}
</style>
