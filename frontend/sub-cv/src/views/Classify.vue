<template>
  <div class="classify-page">
    <el-row :gutter="20">
      <el-col :span="10">
        <el-card shadow="hover">
          <template #header><span class="card-title">📤 上传图片</span></template>
          <el-upload class="upload-area" drag :auto-upload="false" :on-change="handleImage" accept="image/*">
            <el-icon :size="48"><UploadFilled /></el-icon>
            <div class="upload-text">将图片拖到此处，或点击上传</div>
          </el-upload>
          <div v-if="imageUrl" class="image-preview"><img :src="imageUrl" alt="Preview" /></div>
          <el-button type="primary" style="width:100%;margin-top:12px" @click="classify" :loading="loading">开始分类</el-button>
        </el-card>
      </el-col>
      <el-col :span="14">
        <el-card shadow="hover">
          <template #header><span class="card-title">📊 分类结果</span></template>
          <div v-if="!results.length" class="empty-state"><el-icon :size="64" color="#C0C4CC"><PictureFilled /></el-icon><p>上传图片开始分类</p></div>
          <div v-else class="results-list">
            <div v-for="(r, i) in results" :key="i" class="result-item">
              <div class="result-rank">#{{ i + 1 }}</div>
              <div class="result-info">
                <div class="result-label">{{ r.label }}</div>
                <el-progress :percentage="Math.round(r.confidence * 100)" :stroke-width="10" :color="i === 0 ? '#409EFF' : '#C0C4CC'" />
              </div>
              <div class="result-score">{{ (r.confidence * 100).toFixed(1) }}%</div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { ElMessage } from 'element-plus'
const imageUrl = ref('')
const loading = ref(false)
const results = ref<any[]>([])
const CLASSES = ['industrial_product', 'nature_scene', 'document', 'portrait', 'architecture', 'food', 'animal', 'vehicle', 'textile', 'electronic']
function handleImage(file: any) {
  const reader = new FileReader()
  reader.onload = (e) => { imageUrl.value = e.target?.result as string }
  reader.readAsDataURL(file.raw)
}
async function classify() {
  if (!imageUrl.value) { ElMessage.warning('请先上传图片'); return }
  loading.value = true
  await new Promise(r => setTimeout(r, 1000))
  const top5 = CLASSES.sort(() => Math.random() - 0.5).slice(0, 5)
  results.value = top5.map((label, i) => ({
    label,
    confidence: i === 0 ? Math.round((Math.random() * 0.15 + 0.85) * 10000) / 10000 : Math.round(Math.random() * 5000) / 10000,
  })).sort((a, b) => b.confidence - a.confidence)
  loading.value = false
  ElMessage.success('分类完成')
}
</script>

<style scoped>
.card-title { font-size: 15px; font-weight: 600; }
.upload-text { font-size: 14px; color: #606266; margin-top: 8px; }
.image-preview { margin-top: 12px; }
.image-preview img { width: 100%; border-radius: 8px; max-height: 250px; object-fit: contain; background: #f5f5f5; }
.empty-state { text-align: center; padding: 60px; color: #C0C4CC; }
.results-list { display: flex; flex-direction: column; gap: 16px; }
.result-item { display: flex; align-items: center; gap: 16px; }
.result-rank { font-size: 20px; font-weight: 700; color: #409EFF; width: 40px; }
.result-info { flex: 1; }
.result-label { font-size: 14px; font-weight: 600; margin-bottom: 4px; }
.result-score { font-size: 18px; font-weight: 700; color: #67C23A; width: 70px; text-align: right; }
</style>
