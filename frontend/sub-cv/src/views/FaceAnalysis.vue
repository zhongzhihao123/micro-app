<template>
  <div class="face-page">
    <el-row :gutter="20">
      <el-col :span="10">
        <el-card shadow="hover">
          <template #header><span class="card-title">📤 上传人像图片</span></template>
          <el-upload class="upload-area" drag :auto-upload="false" :on-change="handleImage" accept="image/*">
            <el-icon :size="48"><UploadFilled /></el-icon>
            <div class="upload-text">上传含人脸的图片</div>
          </el-upload>
          <div v-if="imageUrl" class="image-preview"><img :src="imageUrl" alt="Preview" /></div>
          <el-button type="primary" style="width:100%;margin-top:12px" @click="detectFaces" :loading="loading">开始分析</el-button>
        </el-card>
      </el-col>
      <el-col :span="14">
        <el-card shadow="hover">
          <template #header>
            <div class="result-header">
              <span class="card-title">👤 人脸分析结果</span>
              <el-tag v-if="faces.length" type="success">检测到 {{ faces.length }} 张人脸</el-tag>
            </div>
          </template>
          <div v-if="!faces.length && !loading" class="empty-state"><el-icon :size="64" color="#C0C4CC"><UserFilled /></el-icon><p>上传人像图片开始分析</p></div>
          <div v-else class="face-list">
            <el-card v-for="face in faces" :key="face.face_id" shadow="never" class="face-card">
              <el-descriptions :column="2" size="small" border>
                <el-descriptions-item label="人脸 ID">{{ face.face_id + 1 }}</el-descriptions-item>
                <el-descriptions-item label="位置">{{ face.bbox.x.toFixed(2) }}, {{ face.bbox.y.toFixed(2) }}</el-descriptions-item>
                <el-descriptions-item label="年龄估计">{{ face.age_estimate }} 岁</el-descriptions-item>
                <el-descriptions-item label="性别">{{ face.gender_estimate === 'male' ? '男' : '女' }}</el-descriptions-item>
                <el-descriptions-item label="情绪">
                  <el-tag :type="emotionType(face.emotion)" size="small">{{ emotionLabel(face.emotion) }}</el-tag>
                </el-descriptions-item>
                <el-descriptions-item label="尺寸">{{ (face.bbox.width * 100).toFixed(0) }}% × {{ (face.bbox.height * 100).toFixed(0) }}%</el-descriptions-item>
              </el-descriptions>
            </el-card>
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
const faces = ref<any[]>([])
const EMOTIONS = ['happy', 'neutral', 'surprised', 'serious', 'smiling']
function emotionLabel(e: string) { return ({ happy: '😊 开心', neutral: '😐 中性', surprised: '😲 惊讶', serious: '🧐 严肃', smiling: '😄 微笑' } as any)[e] || e }
function emotionType(e: string) { return ({ happy: 'success', neutral: 'info', surprised: 'warning', serious: '', smiling: 'success' } as any)[e] || 'info' }
function handleImage(file: any) {
  const reader = new FileReader()
  reader.onload = (e) => { imageUrl.value = e.target?.result as string }
  reader.readAsDataURL(file.raw)
}
async function detectFaces() {
  if (!imageUrl.value) { ElMessage.warning('请先上传图片'); return }
  loading.value = true
  faces.value = []
  await new Promise(r => setTimeout(r, 1500))
  const count = Math.floor(Math.random() * 4) + 1
  faces.value = Array.from({ length: count }, (_, i) => ({
    face_id: i,
    bbox: { x: Math.random() * 0.6, y: Math.random() * 0.5, width: Math.random() * 0.2 + 0.15, height: Math.random() * 0.3 + 0.2 },
    age_estimate: Math.floor(Math.random() * 50) + 18,
    gender_estimate: Math.random() > 0.5 ? 'male' : 'female',
    emotion: EMOTIONS[Math.floor(Math.random() * EMOTIONS.length)],
  }))
  loading.value = false
  ElMessage.success(`检测到 ${count} 张人脸`)
}
</script>

<style scoped>
.card-title { font-size: 15px; font-weight: 600; }
.upload-text { font-size: 14px; color: #606266; margin-top: 8px; }
.image-preview { margin-top: 12px; }
.image-preview img { width: 100%; border-radius: 8px; max-height: 250px; object-fit: contain; background: #f5f5f5; }
.empty-state { text-align: center; padding: 60px; color: #C0C4CC; }
.result-header { display: flex; justify-content: space-between; align-items: center; }
.face-list { display: flex; flex-direction: column; gap: 12px; max-height: 500px; overflow-y: auto; }
.face-card { border: 1px solid #ebeef5; }
</style>
