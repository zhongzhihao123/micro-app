<template>
  <div class="behavior-page">
    <div class="toolbar">
      <el-date-picker
        v-model="dateRange"
        type="daterange"
        range-separator="至"
        start-placeholder="开始日期"
        end-placeholder="结束日期"
        style="width: 280px"
      />
      <el-select v-model="behaviorType" placeholder="行为类型" style="width: 150px; margin-left: 12px" clearable>
        <el-option label="全部" value="" />
        <el-option label="浏览" value="view" />
        <el-option label="点击" value="click" />
        <el-option label="收藏" value="like" />
        <el-option label="购买" value="purchase" />
        <el-option label="分享" value="share" />
      </el-select>
    </div>

    <el-table :data="behaviors" style="width: 100%; margin-top: 16px">
      <el-table-column prop="user_id" label="用户ID" width="150" />
      <el-table-column prop="item_id" label="商品ID" width="150" />
      <el-table-column prop="behavior_type" label="行为类型" width="100">
        <template #default="{ row }">
          <el-tag :type="behaviorColor(row.behavior_type)" size="small">
            {{ behaviorLabel(row.behavior_type) }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="weight" label="权重" width="80" align="center" />
      <el-table-column prop="session_id" label="会话ID" width="150" />
      <el-table-column prop="created_at" label="时间" width="180" />
    </el-table>

    <div class="pagination">
      <el-pagination v-model:current-page="page" :page-size="pageSize" :total="5000" layout="total, prev, pager, next" />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'

const dateRange = ref<[Date, Date]>()
const behaviorType = ref('')
const page = ref(1)
const pageSize = ref(20)

const behaviorLabel = (type: string) => ({ view: '浏览', click: '点击', like: '收藏', purchase: '购买', share: '分享', comment: '评论' } as any)[type] || type
const behaviorColor = (type: string) => ({ view: 'info', click: '', like: 'warning', purchase: 'success', share: 'primary', comment: 'danger' } as any)[type] || ''

const behaviors = ref(
  Array.from({ length: 20 }, (_, i) => ({
    user_id: `user_${String(Math.floor(Math.random() * 1000) + 1).padStart(4, '0')}`,
    item_id: `item_${String(Math.floor(Math.random() * 500) + 1).padStart(4, '0')}`,
    behavior_type: ['view', 'click', 'like', 'purchase', 'share'][Math.floor(Math.random() * 5)],
    weight: (Math.random() * 5).toFixed(1),
    session_id: `sess_${Math.random().toString(36).substring(2, 10)}`,
    created_at: new Date(Date.now() - Math.random() * 86400000 * 7).toISOString().replace('T', ' ').substring(0, 19),
  }))
)
</script>

<style scoped>
.toolbar { display: flex; align-items: center; }
.pagination { margin-top: 20px; display: flex; justify-content: flex-end; }
</style>
