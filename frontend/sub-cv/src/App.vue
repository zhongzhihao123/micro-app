<template>
  <div class="cv-app">
    <div class="sub-app-header">
      <h2>👁️ 计算机视觉平台</h2>
      <el-tabs v-model="activeTab" @tab-click="handleTabClick">
        <el-tab-pane label="目标检测" name="detect" />
        <el-tab-pane label="图像分类" name="classify" />
        <el-tab-pane label="OCR 识别" name="ocr" />
        <el-tab-pane label="人脸分析" name="face" />
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
const activeTab = ref('detect')
watch(() => route.path, (path) => {
  if (path.includes('classify')) activeTab.value = 'classify'
  else if (path.includes('ocr')) activeTab.value = 'ocr'
  else if (path.includes('face')) activeTab.value = 'face'
  else activeTab.value = 'detect'
}, { immediate: true })
function handleTabClick(tab: any) { router.push(`/${tab.props.name}`) }
</script>

<style scoped>
.cv-app { height: 100%; background: #f5f7fa; padding: 16px; box-sizing: border-box; overflow: auto; }
.sub-app-header { background: #fff; padding: 20px 24px; border-radius: 8px; margin-bottom: 16px; box-shadow: 0 1px 4px rgba(0,0,0,0.06); }
.sub-app-header h2 { margin: 0 0 16px 0; font-size: 20px; color: #303133; }
.sub-app-content { background: #fff; padding: 24px; border-radius: 8px; min-height: 500px; box-shadow: 0 1px 4px rgba(0,0,0,0.06); }
</style>
