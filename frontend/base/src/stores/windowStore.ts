import { defineStore } from 'pinia'
import { ref, reactive } from 'vue'

export interface AppWindow {
  id: string
  name: string
  title: string
  icon: string
  entry: string
  color: string
  x: number
  y: number
  width: number
  height: number
  zIndex: number
  minimized: boolean
  maximized: boolean
  mounted: boolean
}

// 子应用定义
export const APP_DEFS = [
  {
    id: 'sub-nlp',
    name: 'NLP 知识库',
    title: 'NLP 知识库问答',
    icon: '🧠',
    entry: '//localhost:3001',
    color: '#22d3ee',
    defaultWidth: 1100,
    defaultHeight: 720,
  },
  {
    id: 'sub-recommend',
    name: '推荐系统',
    title: '智能推荐系统',
    icon: '🎯',
    entry: '//localhost:3002',
    color: '#f59e0b',
    defaultWidth: 1050,
    defaultHeight: 700,
  },
  {
    id: 'sub-cv',
    name: '计算机视觉',
    title: '计算机视觉平台',
    icon: '👁️',
    entry: '//localhost:3003',
    color: '#34d399',
    defaultWidth: 1100,
    defaultHeight: 720,
  },
  {
    id: 'sub-mlops',
    name: 'MLOps 平台',
    title: 'MLOps 平台',
    icon: '⚙️',
    entry: '//localhost:3004',
    color: '#a78bfa',
    defaultWidth: 1150,
    defaultHeight: 740,
  },
  {
    id: 'sub-sql',
    name: 'SQL 数据',
    title: 'SQL 数据管理',
    icon: '🗄️',
    entry: '//localhost:3005',
    color: '#3b82f6',
    defaultWidth: 1200,
    defaultHeight: 760,
  },
  {
    id: 'system-manager',
    name: '系统管理',
    title: '系统管理 - 用户权限',
    icon: '🔐',
    entry: '//localhost:3006',
    color: '#ef4444',
    defaultWidth: 1200,
    defaultHeight: 780,
  },
  {
    id: 'sub-cicd',
    name: 'CI/CD 流水线',
    title: 'CI/CD 流水线 - 自动化构建部署',
    icon: '🚀',
    entry: '//localhost:3007',
    color: '#10b981',
    defaultWidth: 1200,
    defaultHeight: 780,
  },
  {
    id: 'sub-oa',
    name: 'OA 审批',
    title: 'OA 审批系统 - 企业请假审批',
    icon: '📋',
    entry: '//localhost:3008',
    color: '#1890ff',
    defaultWidth: 1100,
    defaultHeight: 720,
  },
]

export const useWindowStore = defineStore('windows', () => {
  const windows = ref<AppWindow[]>([])
  const nextZIndex = ref(100)
  const activeWindowId = ref<string | null>(null)

  function getWindow(id: string) {
    return windows.value.find(w => w.id === id)
  }

  function openApp(appId: string) {
    // 如果已打开且最小化 → 恢复
    const existing = windows.value.find(w => w.id === appId)
    if (existing) {
      if (existing.minimized) {
        existing.minimized = false
      }
      focusWindow(appId)
      return
    }

    // 创建新窗口
    const def = APP_DEFS.find(a => a.id === appId)
    if (!def) return

    const offset = windows.value.length * 30
    const win: AppWindow = {
      id: def.id,
      name: def.name,
      title: def.title,
      icon: def.icon,
      entry: def.entry,
      color: def.color,
      x: 80 + offset,
      y: 50 + offset,
      width: Math.min(def.defaultWidth, window.innerWidth - 120),
      height: Math.min(def.defaultHeight, window.innerHeight - 140),
      zIndex: ++nextZIndex.value,
      minimized: false,
      maximized: false,
      mounted: false,
    }

    windows.value.push(win)
    focusWindow(appId)
  }

  function closeWindow(appId: string) {
    const idx = windows.value.findIndex(w => w.id === appId)
    if (idx !== -1) {
      windows.value.splice(idx, 1)
      if (activeWindowId.value === appId) {
        activeWindowId.value = windows.value.length > 0
          ? windows.value[windows.value.length - 1].id
          : null
      }
    }
  }

  function minimizeWindow(appId: string) {
    const win = windows.value.find(w => w.id === appId)
    if (win) {
      win.minimized = true
      if (activeWindowId.value === appId) {
        // 激活下一个未最小化的窗口
        const next = [...windows.value].reverse().find(w => w.id !== appId && !w.minimized)
        activeWindowId.value = next?.id ?? null
      }
    }
  }

  function toggleMaximize(appId: string) {
    const win = windows.value.find(w => w.id === appId)
    if (win) {
      win.maximized = !win.maximized
    }
  }

  function focusWindow(appId: string) {
    const win = windows.value.find(w => w.id === appId)
    if (win) {
      win.zIndex = ++nextZIndex.value
      win.minimized = false
      activeWindowId.value = appId
    }
  }

  function updatePosition(appId: string, x: number, y: number) {
    const win = windows.value.find(w => w.id === appId)
    if (win && !win.maximized) {
      win.x = x
      win.y = y
    }
  }

  function updateSize(appId: string, width: number, height: number) {
    const win = windows.value.find(w => w.id === appId)
    if (win && !win.maximized) {
      win.width = Math.max(400, width)
      win.height = Math.max(300, height)
    }
  }

  function setMounted(appId: string) {
    const win = windows.value.find(w => w.id === appId)
    if (win) win.mounted = true
  }

  return {
    windows,
    activeWindowId,
    openApp,
    closeWindow,
    minimizeWindow,
    toggleMaximize,
    focusWindow,
    updatePosition,
    updateSize,
    setMounted,
    getWindow,
  }
})
