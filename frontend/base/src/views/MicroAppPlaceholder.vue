<template>
  <div class="micro-placeholder">
    <el-skeleton :loading="true" animated>
      <template #template>
        <el-skeleton-item variant="text" style="width: 30%" />
        <el-skeleton-item variant="text" />
        <el-skeleton-item variant="text" />
        <el-skeleton-item variant="rect" style="height: 200px; margin-top: 16px" />
      </template>
    </el-skeleton>
    <div class="loading-text">正在加载子应用...</div>
  </div>
</template>

<script setup lang="ts">
// 微前端占位组件 - qiankun 会自动替换内容
</script>

<style scoped>
.micro-placeholder {
  padding: 40px;
  text-align: center;
}

.loading-text {
  margin-top: 20px;
  color: #909399;
  font-size: 14px;
}
</style>
