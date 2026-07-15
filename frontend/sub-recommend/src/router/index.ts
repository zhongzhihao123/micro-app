import type { RouteRecordRaw } from 'vue-router'

const routes: RouteRecordRaw[] = [
  { path: '/', redirect: '/dashboard' },
  { path: '/dashboard', name: 'Dashboard', component: () => import('@/views/Dashboard.vue') },
  { path: '/items', name: 'Items', component: () => import('@/views/Items.vue') },
  { path: '/behavior', name: 'Behavior', component: () => import('@/views/Behavior.vue') },
  { path: '/ab-test', name: 'ABTest', component: () => import('@/views/ABTest.vue') },
]

export default routes
