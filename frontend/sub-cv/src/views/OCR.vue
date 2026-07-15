<template>
  <div class="ocr-page">
    <el-row :gutter="20">
      <el-col :span="10">
        <el-card shadow="hover">
          <template #header><span class="card-title">📤 上传图片</span></template>
          <el-upload class="upload-area" drag :auto-upload="false" :on-change="handleImage" accept="image/*">
            <el-icon :size="48"><UploadFilled /></el-icon>
            <div class="upload-text">上传含文字的图片</div>
          </el-upload>
          <div v-if="imageUrl" class="image-preview"><img :src="imageUrl" alt="Preview" /></div>
          <el-button type="primary" style="width:100%;margin-top:12px" @click="doOCR" :loading="loading">开始识别</el-button>
        </el-card>
      </el-col>
      <el-col :span="14">
        <el-card shadow="hover">
          <template #header><span class="card-title">📝 识别结果</span></template>
          <div v-if="!fullText" class="empty-state"><el-icon :size="64" color="#C0C4CC"><Document /></el-icon><p>上传图片开始 OCR 识别</p></div>
          <div v-else>
            <div class="ocr-text">{{ fullText }}</div>
            <el-divider />
            <div class="ocr-blocks">
              <div v-for="(block, i) in blocks" :key="i" class="ocr-block">
                <span class="block-index">{{ i + 1 }}</span>
                <span class="block-text">{{ block.text }}</span>
                <el-tag size="small">{{ (block.confidence * 100).toFixed(0) }}%</el-tag>
              </div>
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
const fullText = ref('')
const blocks = ref<any[]>([])
const MOCK_TEXTS = [
  '项目验收报告\n编号: PRJ-2024-001\n状态: 已完成\n验收日期: 2024年7月14日',
  '发票\n号码: INV-20240714\n金额: ¥12,800.00\n开票日期: 2024-07-14',
  '会议纪要\n时间: 2024年7月14日 14:00\n主题: AI平台架构评审\n参会人员: 技术部全员',
]
function handleImage(file: any) {
  const reader = new FileReader()
  reader.onload = (e) => { imageUrl.value = e.target?.result as string }
  reader.readAsDataURL(file.raw)
}
async function doOCR() {
  if (!imageUrl.value) { ElMessage.warning('请先上传图片'); return }
  loading.value = true
  await new Promise(r => setTimeout(r, 1200))
  const text = MOCK_TEXTS[Math.floor(Math.random() * MOCK_TEXTS.length)]
  fullText.value = text
  blocks.value = text.split('\n').map(line => ({ text: line, confidence: Math.round((Math.random() * 0.2 + 0.8) * 100) / 100 }))
  loading.value = false
  ElMessage.success('OCR 识别完成')
}
</script>

<style scoped>
.card-title { font-size: 15px; font-weight: 600; }
.upload-text { font-size: 14px; color: #606266; margin-top: 8px; }
.image-preview { margin-top: 12px; }
.image-preview img { width: 100%; border-radius: 8px; max-height: 250px; object-fit: contain; background: #f5f5f5; }
.empty-state { text-align: center; padding: 60px; color: #C0C4CC; }
.ocr-text { white-space: pre-wrap; font-size: 15px; line-height: 1.8; padding: 16px; background: #f5f7fa; border-radius: 8px; font-family: 'PingFang SC', sans-serif; }
.ocr-blocks { display: flex; flex-direction: column; gap: 8px; }
.ocr-block { display: flex; align-items: center; gap: 12px; }
.block-index { width: 24px; height: 24px; background: #409EFF; color: #fff; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 12px; font-weight: 600; }
.block-text { flex: 1; font-size: 14px; }
</style>
