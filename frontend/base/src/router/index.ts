import { createRouter, createWebHistory } from 'vue-router'
import type { RouteRecordRaw } from 'vue-router'

const routes: RouteRecordRaw[] = [
  {
    path: '/',
    redirect: '/desktop',
  },
  {
    path: '/desktop',
    name: 'Desktop',
    component: () => import('@/App.vue'),
    meta: { title: 'AI 桌面' },
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

export default router
