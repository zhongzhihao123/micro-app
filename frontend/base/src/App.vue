<template>
  <!-- 登录弹窗 -->
  <LoginDialog :visible="!isLoggedIn" @login="onLogin" />

  <!-- 桌面 -->
  <div v-if="isLoggedIn" id="desktop">
    <!-- 桌面壁纸 -->
    <div class="desktop-wallpaper" :style="{ backgroundImage: `url(${bgImage})` }" />

    <!-- 桌面图标 - 按权限过滤 -->
    <div class="desktop-icons">
      <div
        v-for="app in visibleApps"
        :key="app.id"
        class="desktop-icon"
        @dblclick="openApp(app.id)"
      >
        <div class="icon-image" :style="{ background: app.color + '18', color: app.color }">
          <span class="icon-emoji">{{ app.icon }}</span>
        </div>
        <span class="icon-label">{{ app.name }}</span>
      </div>
    </div>

    <!-- 窗口层 -->
    <div class="windows-layer">
      <WindowFrame
        v-for="win in windows"
        :key="win.id"
        :window="win"
        :isFocused="activeWindowId === win.id"
        @close="closeWindow(win.id)"
        @minimize="minimizeWindow(win.id)"
        @toggleMaximize="toggleMaximize(win.id)"
        @focus="focusWindow(win.id)"
        @move="(x, y) => updatePosition(win.id, x, y)"
        @resize="(w, h, x, y) => { updateSize(win.id, w, h); updatePosition(win.id, x, y) }"
      />
    </div>

    <!-- 底部任务栏 -->
    <div class="taskbar">
      <div class="taskbar-left">
        <div class="taskbar-apps">
          <div
            v-for="win in windows"
            :key="win.id"
            class="taskbar-app"
            :class="{ active: activeWindowId === win.id && !win.minimized }"
            @click="handleTaskbarClick(win.id)"
          >
            <div class="taskbar-app-icon" :style="{ color: win.color }">
              <span>{{ win.icon }}</span>
            </div>
            <span class="taskbar-app-name">{{ win.name }}</span>
            <div
              class="taskbar-app-indicator"
              :class="{
                visible: true,
                glowing: activeWindowId === win.id && !win.minimized,
                dimmed: win.minimized
              }"
            />
          </div>
        </div>
      </div>
      <div class="taskbar-right">
        <div class="taskbar-time">
          <span class="time-text">{{ currentTime }}</span>
          <span class="date-text">{{ currentDate }}</span>
        </div>

        <!-- 用户头像 + 下拉菜单 -->
        <el-popover placement="top-end" :width="260" trigger="click" @show="loadUserInfo">
          <template #reference>
            <div class="user-avatar-btn">
              <div class="user-avatar-circle">{{ userInitial }}</div>
            </div>
          </template>
          <div class="user-menu">
            <div class="user-menu-header">
              <div class="um-avatar">{{ userInitial }}</div>
              <div class="um-info">
                <div class="um-name">{{ userInfo.displayName || userInfo.username }}</div>
                <div class="um-email">{{ userInfo.email }}</div>
                <el-tag size="small" :type="userInfo.role === 'admin' ? 'danger' : 'info'" style="margin-top:4px">
                  {{ userInfo.role }}
                </el-tag>
              </div>
            </div>
            <el-divider style="margin:10px 0" />
            <div class="um-perms" v-if="userInfo.permissions?.length">
              <span class="um-perms-label">应用权限 ({{ userInfo.permissions.length }})：</span>
              <div style="margin-top:6px">
                <el-tag v-for="p in userInfo.permissions" :key="p" size="small" style="margin:2px">{{ p }}</el-tag>
              </div>
            </div>
            <el-divider style="margin:10px 0" />
            <el-button type="danger" plain size="small" style="width:100%" @click="handleLogout">
              🚪 退出登录
            </el-button>
          </div>
        </el-popover>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, watch, nextTick } from 'vue'
import { useWindowStore, APP_DEFS } from '@/stores/windowStore'
import { loadMicroApp } from 'qiankun'
import type { MicroApp } from 'qiankun'
import WindowFrame from '@/components/WindowFrame.vue'
import LoginDialog from '@/components/LoginDialog.vue'
import axios from 'axios'

const store = useWindowStore()
const { windows, activeWindowId, openApp, closeWindow, minimizeWindow, toggleMaximize, focusWindow, updatePosition, updateSize } = store

// ── 登录状态 ──
const token = ref(localStorage.getItem('jwt_token') || '')
const isLoggedIn = ref(!!token.value)

// ── 用户信息 ──
const userInfo = ref<any>({})
const userInitial = computed(() => (userInfo.value.displayName || userInfo.value.username || 'U').charAt(0).toUpperCase())

function onLogin(data: any) {
  token.value = data.token
  isLoggedIn.value = true
  localStorage.setItem('jwt_token', data.token)
  userInfo.value = data.user || {}
  localStorage.setItem('user_info', JSON.stringify(data.user || {}))
  window.dispatchEvent(new Event('storage'))
}

function handleLogout() {
  localStorage.removeItem('jwt_token')
  localStorage.removeItem('user_info')
  token.value = ''
  isLoggedIn.value = false
  userInfo.value = {}
  // 关闭所有窗口
  for (const w of [...windows]) closeWindow(w.id)
}

// ── 权限过滤后的桌面图标 ──
const desktopApps = APP_DEFS
const userPerms = ref<string[]>([])

// app id → 权限 key 映射
const appPermKeyMap: Record<string, string> = {
  'sub-nlp': 'nlp',
  'sub-recommend': 'recommend',
  'sub-cv': 'cv',
  'sub-mlops': 'mlops',
  'sub-sql': 'dbadmin',
  'system-manager': 'system-manager',
}

const visibleApps = computed(() => {
  if (userPerms.value.length === 0) {
    // 还没加载权限时展示全部
    return desktopApps
  }
  return desktopApps.filter(app => {
    const permKey = appPermKeyMap[app.id] || app.id
    return userPerms.value.includes(permKey)
  })
})

async function loadUserInfo() {
  try {
    const res = await axios.get('/api/users/me', {
      headers: { Authorization: `Bearer ${token.value}` }
    })
    if (res.data.code === 200) {
      userInfo.value = res.data.data
      userPerms.value = res.data.data.permissions || []
      localStorage.setItem('user_info', JSON.stringify(res.data.data))
    }
  } catch {
    // 用本地缓存
    const cached = localStorage.getItem('user_info')
    if (cached) {
      try {
        const u = JSON.parse(cached)
        userInfo.value = u
        userPerms.value = u.permissions || []
      } catch {}
    }
  }
}

// 初始加载用户信息
onMounted(async () => {
  if (isLoggedIn.value) {
    const cached = localStorage.getItem('user_info')
    if (cached) {
      try {
        const u = JSON.parse(cached)
        userInfo.value = u
        userPerms.value = u.permissions || []
      } catch {}
    }
    loadUserInfo()
  }
})

// ── 桌面背景图片 ──
const bgImage = ref('')
// 生成现代几何风格桌面背景
function generateBgImage() {
  const c = document.createElement('canvas')
  c.width = 1920; c.height = 1080
  const ctx = c.getContext('2d')!
  // 渐变背景
  const g = ctx.createLinearGradient(0, 0, 1920, 1080)
  g.addColorStop(0, '#0f172a')
  g.addColorStop(0.3, '#1e293b')
  g.addColorStop(0.6, '#0f172a')
  g.addColorStop(1, '#020617')
  ctx.fillStyle = g; ctx.fillRect(0, 0, 1920, 1080)

  // 网格线
  ctx.strokeStyle = 'rgba(59,130,246,0.06)'; ctx.lineWidth = 1
  for (let x = 0; x < 1920; x += 80) { ctx.beginPath(); ctx.moveTo(x, 0); ctx.lineTo(x, 1080); ctx.stroke() }
  for (let y = 0; y < 1080; y += 80) { ctx.beginPath(); ctx.moveTo(0, y); ctx.lineTo(1920, y); ctx.stroke() }

  // 大圆光晕
  const drawGlow = (cx: number, cy: number, r: number, color: string, alpha: number) => {
    const grad = ctx.createRadialGradient(cx, cy, 0, cx, cy, r)
    grad.addColorStop(0, color)
    grad.addColorStop(1, 'transparent')
    ctx.fillStyle = grad
    ctx.globalAlpha = alpha
    ctx.fillRect(cx - r, cy - r, r * 2, r * 2)
    ctx.globalAlpha = 1
  }
  drawGlow(400, 300, 500, '#3b82f6', 0.15)
  drawGlow(1500, 700, 450, '#8b5cf6', 0.12)
  drawGlow(960, 540, 600, '#06b6d4', 0.08)

  // 几何线条
  ctx.strokeStyle = 'rgba(59,130,246,0.1)'; ctx.lineWidth = 2
  const drawLine = (x1: number, y1: number, x2: number, y2: number) => {
    ctx.beginPath(); ctx.moveTo(x1, y1); ctx.lineTo(x2, y2); ctx.stroke()
  }
  drawLine(200, 800, 600, 400)
  drawLine(400, 900, 800, 600)
  drawLine(1200, 200, 1600, 600)
  drawLine(1400, 100, 1700, 400)
  ctx.strokeStyle = 'rgba(139,92,246,0.08)'; ctx.lineWidth = 1
  drawLine(100, 600, 400, 200)
  drawLine(1500, 300, 1800, 100)

  // 小点装饰
  for (let i = 0; i < 30; i++) {
    ctx.fillStyle = `rgba(59,130,246,${Math.random() * 0.3})`
    ctx.beginPath()
    ctx.arc(Math.random() * 1920, Math.random() * 1080, Math.random() * 2 + 1, 0, Math.PI * 2)
    ctx.fill()
  }
  bgImage.value = c.toDataURL()
}
onMounted(generateBgImage)

// ── Micro Apps ──
const microApps = new Map<string, MicroApp>()
const currentTime = ref('')
const currentDate = ref('')
let clockTimer: number

function handleTaskbarClick(appId: string) {
  const win = store.getWindow(appId)
  if (!win) return
  if (win.minimized || activeWindowId !== appId) {
    focusWindow(appId)
  } else {
    minimizeWindow(appId)
  }
}

function updateClock() {
  const now = new Date()
  currentTime.value = now.toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' })
  currentDate.value = now.toLocaleDateString('zh-CN', { month: 'long', day: 'numeric', weekday: 'short' })
}

watch(() => windows.map(w => w.id + w.mounted), async () => {
  await nextTick()
  for (const win of windows) {
    if (win.mounted) continue
    const containerId = `app-container-${win.id}`
    const container = document.getElementById(containerId)
    if (!container) continue
    try {
      const app = loadMicroApp(
        { name: win.id, entry: win.entry, container: `#${containerId}`, props: { baseRoute: `/${win.id.replace('sub-', '')}` } },
        { sandbox: { experimentalStyleIsolation: true } },
      )
      microApps.set(win.id, app)
      store.setMounted(win.id)
    } catch (e) { console.error(`Failed to load ${win.id}:`, e) }
  }
}, { deep: true })

watch(() => windows.length, (newLen, oldLen) => {
  if (newLen < (oldLen ?? 0)) {
    const currentIds = new Set(windows.map(w => w.id))
    for (const [id, app] of microApps) {
      if (!currentIds.has(id)) {
        app.unmount()
        // 清理残留的 qiankun 样式标签
        const container = document.getElementById(`app-container-${id}`)
        if (container) {
          container.innerHTML = ''
          container.removeAttribute('data-qiankun')
        }
        document.querySelectorAll(`style[data-qiankun="${id}"]`).forEach(el => el.remove())
        microApps.delete(id)
      }
    }
  }
})

onMounted(() => {
  updateClock()
  clockTimer = window.setInterval(updateClock, 10000)
})

onUnmounted(() => {
  clearInterval(clockTimer)
  for (const [, app] of microApps) app.unmount()
})
</script>

<style>
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

* { margin: 0; padding: 0; box-sizing: border-box; }

:root {
  --bg-deep: #0f172a;
  --bg-window: #ffffff;
  --bg-window-content: #f8f9fb;
  --bg-titlebar: #f0f1f4;
  --bg-taskbar: rgba(15, 23, 42, 0.85);
  --border-subtle: rgba(255, 255, 255, 0.06);
  --border-window: rgba(0, 0, 0, 0.08);
  --border-window-focused: rgba(59, 130, 246, 0.35);
  --text-primary: #e2e8f0;
  --text-secondary: #94a3b8;
  --text-muted: #64748b;
  --accent-blue: #3b82f6;
  --accent-cyan: #06b6d4;
  --accent-purple: #8b5cf6;
  --accent-amber: #f59e0b;
  --accent-emerald: #10b981;
  --taskbar-height: 48px;
}

html, body, #app {
  height: 100%;
  font-family: 'Outfit', -apple-system, BlinkMacSystemFont, sans-serif;
  overflow: hidden;
  background: var(--bg-deep);
  color: var(--text-primary);
  user-select: none;
}

#desktop {
  height: 100vh;
  position: relative;
  overflow: hidden;
}

.desktop-wallpaper {
  position: absolute;
  inset: 0;
  z-index: 0;
  background-size: cover;
  background-position: center;
}

/* ── Desktop Icons ── */
.desktop-icons {
  position: absolute;
  top: 32px;
  left: 32px;
  display: flex;
  flex-direction: column;
  gap: 12px;
  z-index: 2;
  padding-bottom: calc(var(--taskbar-height) + 16px);
}

.desktop-icon {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 6px;
  padding: 10px 14px;
  border-radius: 14px;
  cursor: pointer;
  transition: all 0.2s;
  width: 88px;
}

.desktop-icon:hover {
  background: rgba(255, 255, 255, 0.06);
  backdrop-filter: blur(12px);
}

.icon-image {
  width: 52px; height: 52px;
  border-radius: 16px;
  display: flex; align-items: center; justify-content: center;
  transition: transform 0.2s;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.3);
}

.desktop-icon:hover .icon-image { transform: scale(1.06); }

.icon-emoji { font-size: 26px; line-height: 1; }

.icon-label {
  font-size: 11px; color: rgba(255, 255, 255, 0.7);
  text-align: center; line-height: 1.3; font-weight: 500;
  text-shadow: 0 1px 4px rgba(0, 0, 0, 0.5);
}

.windows-layer {
  position: absolute;
  inset: 0;
  bottom: calc(var(--taskbar-height) + 8px);
  z-index: 3;
  pointer-events: none;
}
.windows-layer > * { pointer-events: auto; }

/* ── Taskbar (深色毛玻璃) ── */
.taskbar {
  position: absolute; bottom: 0; left: 0; right: 0;
  height: var(--taskbar-height);
  background: rgba(15, 23, 42, 0.7);
  backdrop-filter: blur(32px) saturate(1.4);
  -webkit-backdrop-filter: blur(32px) saturate(1.4);
  border-top: 1px solid rgba(255, 255, 255, 0.06);
  display: flex; align-items: center; justify-content: space-between;
  padding: 0 16px;
  z-index: 100;
}

.taskbar::before {
  content: ''; position: absolute; top: 0; left: 50%; transform: translateX(-50%);
  width: 70%; height: 1px;
  background: linear-gradient(90deg, transparent, rgba(255,255,255,0.1), transparent);
}

.taskbar-left { display: flex; align-items: center; flex: 1; }
.taskbar-apps { display: flex; align-items: center; gap: 2px; }

.taskbar-app {
  display: flex; align-items: center; gap: 8px;
  padding: 6px 14px; border-radius: 8px;
  cursor: pointer; transition: all 0.2s; position: relative;
}
.taskbar-app:hover { background: rgba(255, 255, 255, 0.06); }
.taskbar-app.active { background: rgba(59, 130, 246, 0.12); }

.taskbar-app-icon { font-size: 15px; line-height: 1; display: flex; align-items: center; }
.taskbar-app-name { font-size: 11px; color: var(--text-secondary); font-weight: 500; }
.taskbar-app.active .taskbar-app-name { color: var(--text-primary); }

.taskbar-app-indicator {
  position: absolute; bottom: 3px; left: 50%; transform: translateX(-50%);
  height: 2.5px; border-radius: 2px; transition: all 0.35s cubic-bezier(0.4,0,0.2,1);
}
.taskbar-app-indicator.visible { width: 18px; background: var(--accent-blue); }
.taskbar-app-indicator.glowing { width: 26px; background: var(--accent-cyan); box-shadow: 0 0 6px rgba(6,182,212,0.4); }
.taskbar-app-indicator.dimmed { width: 10px; background: var(--text-muted); }

.taskbar-right { display: flex; align-items: center; gap: 12px; }

.taskbar-time { display: flex; flex-direction: column; align-items: flex-end; padding: 2px 6px; }
.time-text { font-size: 13px; font-weight: 600; color: var(--text-primary); font-family: 'JetBrains Mono', monospace; }
.date-text { font-size: 11px; color: var(--text-muted); }

/* ── 用户头像按钮 ── */
.user-avatar-btn {
  width: 34px; height: 34px; border-radius: 50%;
  cursor: pointer; transition: all 0.2s;
}
.user-avatar-btn:hover { transform: scale(1.08); }
.user-avatar-circle {
  width: 34px; height: 34px; border-radius: 50%;
  background: linear-gradient(135deg, #3b82f6, #8b5cf6);
  color: #fff; font-size: 15px; font-weight: 700;
  display: flex; align-items: center; justify-content: center;
}

/* ── 用户菜单 ── */
.user-menu-header { display: flex; align-items: center; gap: 12px; }
.um-avatar {
  width: 44px; height: 44px; border-radius: 50%;
  background: linear-gradient(135deg, #3b82f6, #8b5cf6);
  color: #fff; font-size: 20px; font-weight: 700;
  display: flex; align-items: center; justify-content: center;
  flex-shrink: 0;
}
.um-info { display: flex; flex-direction: column; }
.um-name { font-size: 15px; font-weight: 600; color: #1a1d28; }
.um-email { font-size: 12px; color: #9ca3af; }
.um-perms-label { font-size: 12px; color: #9ca3af; }

::-webkit-scrollbar { width: 5px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: rgba(255, 255, 255, 0.1); border-radius: 3px; }
</style>
