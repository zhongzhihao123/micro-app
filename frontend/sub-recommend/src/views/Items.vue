<template>
  <div class="items-page">
    <div class="toolbar">
      <el-input v-model="searchQuery" placeholder="搜索商品..." :prefix-icon="Search" style="width: 300px" clearable />
      <el-select v-model="categoryFilter" placeholder="分类筛选" style="width: 150px; margin-left: 12px" clearable>
        <el-option label="全部" value="" />
        <el-option label="电子产品" value="电子产品" />
        <el-option label="图书" value="图书" />
        <el-option label="服装" value="服装" />
        <el-option label="食品" value="食品" />
        <el-option label="家居" value="家居" />
      </el-select>
      <el-button type="primary" style="margin-left: 12px">
        <el-icon><Plus /></el-icon> 添加商品
      </el-button>
    </div>

    <el-table :data="items" style="width: 100%; margin-top: 16px" v-loading="loading">
      <el-table-column prop="title" label="商品名称" min-width="200" />
      <el-table-column prop="category" label="分类" width="120">
        <template #default="{ row }">
          <el-tag size="small">{{ row.category }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="price" label="价格" width="100" align="right">
        <template #default="{ row }">¥{{ row.price?.toFixed(2) }}</template>
      </el-table-column>
      <el-table-column prop="score" label="推荐分" width="100" align="center">
        <template #default="{ row }">
          <el-tag :type="row.score > 0.8 ? 'success' : row.score > 0.5 ? 'warning' : 'info'" size="small">
            {{ (row.score * 100).toFixed(0) }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="views" label="浏览量" width="100" align="right" />
      <el-table-column prop="clicks" label="点击量" width="100" align="right" />
      <el-table-column prop="ctr" label="点击率" width="100" align="center">
        <template #default="{ row }">{{ (row.ctr * 100).toFixed(1) }}%</template>
      </el-table-column>
      <el-table-column label="操作" width="150" fixed="right">
        <template #default>
          <el-button type="primary" link size="small">编辑</el-button>
          <el-button type="primary" link size="small">推荐</el-button>
          <el-button type="danger" link size="small">下架</el-button>
        </template>
      </el-table-column>
    </el-table>

    <div class="pagination">
      <el-pagination v-model:current-page="page" :page-size="pageSize" :total="100" layout="total, prev, pager, next" />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { Search } from '@element-plus/icons-vue'

const loading = ref(false)
const searchQuery = ref('')
const categoryFilter = ref('')
const page = ref(1)
const pageSize = ref(20)

const items = ref(
  Array.from({ length: 20 }, (_, i) => ({
    id: `item_${String(i + 1).padStart(4, '0')}`,
    title: `产品-${String(i + 1).padStart(4, '0')}`,
    category: ['电子产品', '图书', '服装', '食品', '家居'][i % 5],
    price: Math.round(Math.random() * 5000 + 50) / 100,
    score: Math.round(Math.random() * 40 + 60) / 100,
    views: Math.floor(Math.random() * 50000 + 1000),
    clicks: Math.floor(Math.random() * 5000 + 100),
    ctr: Math.round(Math.random() * 15 + 3) / 100,
  }))
)
</script>

<style scoped>
.toolbar { display: flex; align-items: center; }
.pagination { margin-top: 20px; display: flex; justify-content: flex-end; }
</style>
