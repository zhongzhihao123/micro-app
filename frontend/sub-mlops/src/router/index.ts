import type { RouteRecordRaw } from 'vue-router'

const routes: RouteRecordRaw[] = [
  { path: '/', redirect: '/models' },
  { path: '/models', name: 'Models', component: () => import('@/views/Models.vue') },
  { path: '/training', name: 'Training', component: () => import('@/views/Training.vue') },
  { path: '/experiments', name: 'Experiments', component: () => import('@/views/Experiments.vue') },
  { path: '/monitor', name: 'Monitor', component: () => import('@/views/Monitor.vue') },
]

export default routes
