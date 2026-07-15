<template>
  <div class="detect-page">
    <el-row :gutter="20">
      <el-col :span="10">
        <el-card shadow="hover">
          <template #header><span class="card-title">📤 上传图片</span></template>
          <el-upload
            class="upload-area"
            drag
            :auto-upload="false"
            :on-change="handleImageChange"
            accept="image/*"
          >
            <el-icon :size="48"><UploadFilled /></el-icon>
            <div class="upload-text">将图片拖到此处，或点击上传</div>
            <div class="upload-hint">支持 JPG/PNG/WebP 格式</div>
          </el-upload>

          <div v-if="imageUrl" class="image-preview">
            <img :src="imageUrl" alt="Preview" />
          </div>

          <el-button type="primary" style="width: 100%; margin-top: 12px" @click="startDetection" :loading="detecting">
            <el-icon><Search /></el-icon> 开始检测
          </el-button>
        </el-card>
      </el-col>

      <el-col :span="14">
        <el-card shadow="hover">
          <template #header>
            <div class="result-header">
              <span class="card-title">📊 检测结果</span>
              <span v-if="detectTime" class="detect-time">耗时: {{ detectTime }}ms</span>
            </div>
          </template>

          <div v-if="!results.length && !detecting" class="empty-state">
            <el-icon :size="64" color="#C0C4CC"><PictureFilled /></el-icon>
            <p>上传图片开始目标检测</p>
          </div>

          <el-table v-if="results.length" :data="results" style="width: 100%">
            <el-table-column prop="label" label="检测目标" min-width="150">
              <template #default="{ row }">
                <el-tag :type="row.confidence > 0.8 ? 'success' : 'warning'">{{ row.label }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="confidence" label="置信度" width="120" align="center">
              <template #default="{ row }">
                <el-progress :percentage="Math.round(row.confidence * 100)" :stroke-width="8" :color="row.confidence > 0.8 ? '#67C23A' : '#E6A23C'" />
              </template>
            </el-table-column>
            <el-table-column label="位置 (x, y, w, h)" min-width="200">
              <template #default="{ row }">
                <span class="bbox-text">
                  ({{ row.bbox.x.toFixed(2) }}, {{ row.bbox.y.toFixed(2) }}, {{ row.bbox.width.toFixed(2) }}, {{ row.bbox.height.toFixed(2) }})
                </span>
              </template>
            </el-table-column>
          </el-table>

          <div v-if="results.length" class="detect-summary">
            <el-tag type="info">共检测到 {{ results.length }} 个目标</el-tag>
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
const detecting = ref(false)
const detectTime = ref<number | null>(null)
const results = ref<any[]>([])

const MOCK_OBJECTS = ['person', 'car', 'bicycle', 'motorcycle', 'bus', 'truck', 'traffic light', 'bench', 'bird', 'cat', 'dog', 'laptop', 'cell phone', 'book', 'bottle', 'cup', 'chair', 'table', 'keyboard']

function handleImageChange(file: any) {
  const reader = new FileReader()
  reader.onload = (e) => { imageUrl.value = e.target?.result as string }
  reader.readAsDataURL(file.raw)
}

async function startDetection() {
  if (!imageUrl.value) { ElMessage.warning('请先上传图片'); return }
  detecting.value = true
  results.value = []
  await new Promise(r => setTimeout(r, 1500))
  const count = Math.floor(Math.random() * 6) + 1
  results.value = Array.from({ length: count }, () => ({
    label: MOCK_OBJECTS[Math.floor(Math.random() * MOCK_OBJECTS.length)],
    confidence: Math.round((Math.random() * 0.35 + 0.65) * 10000) / 10000,
    bbox: { x: Math.random() * 0.7, y: Math.random() * 0.7, width: Math.random() * 0.3 + 0.05, height: Math.random() * 0.3 + 0.05 },
  }))
  detectTime.value = Math.round(Math.random() * 250 + 50)
  detecting.value = false
  ElMessage.success(`检测完成，发现 ${count} 个目标`)
}
</script>

<style scoped>
.card-title { font-size: 15px; font-weight: 600; }
.upload-area { width: 100%; }
.upload-text { font-size: 14px; color: #606266; margin-top: 8px; }
.upload-hint { font-size: 12px; color: #C0C4CC; margin-top: 4px; }
.image-preview { margin-top: 12px; }
.image-preview img { width: 100%; border-radius: 8px; max-height: 250px; object-fit: contain; background: #f5f5f5; }
.result-header { display: flex; justify-content: space-between; align-items: center; }
.detect-time { font-size: 13px; color: #909399; }
.empty-state { text-align: center; padding: 60px; color: #C0C4CC; }
.bbox-text { font-family: monospace; font-size: 12px; color: #606266; }
.detect-summary { margin-top: 16px; }
</style>
