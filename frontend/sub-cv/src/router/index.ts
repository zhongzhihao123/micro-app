import type { RouteRecordRaw } from 'vue-router'

const routes: RouteRecordRaw[] = [
  { path: '/', redirect: '/detect' },
  { path: '/detect', name: 'Detect', component: () => import('@/views/Detect.vue') },
  { path: '/classify', name: 'Classify', component: () => import('@/views/Classify.vue') },
  { path: '/ocr', name: 'OCR', component: () => import('@/views/OCR.vue') },
  { path: '/face', name: 'Face', component: () => import('@/views/FaceAnalysis.vue') },
]

export default routes
