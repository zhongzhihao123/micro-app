<template>
  <!-- 登录弹窗 -->
  <LoginDialog :visible="!isLoggedIn" @login="onLogin" />

  <div v-if="isLoggedIn" id="desktop">
    <!-- 桌面壁纸 -->
    <div class="desktop-wallpaper" :style="{ background: currentBg }" />

    <!-- 桌面图标 -->
    <div class="desktop-icons">
      <div v-for="app in visibleApps" :key="app.id" class="desktop-icon" @dblclick="openApp(app.id)">
        <div class="icon-image" :style="{ background: app.color + '18', color: app.color }">
          <span class="icon-emoji">{{ app.icon }}</span>
        </div>
        <span class="icon-label">{{ app.name }}</span>
      </div>
    </div>

    <div class="windows-layer">
      <WindowFrame v-for="win in windows" :key="win.id" :window="win" :isFocused="activeWindowId === win.id"
        @close="closeWindow(win.id)" @minimize="minimizeWindow(win.id)" @toggleMaximize="toggleMaximize(win.id)"
        @focus="focusWindow(win.id)"
        @move="(x, y) => updatePosition(win.id, x, y)"
        @resize="(w, h, x, y) => { updateSize(win.id, w, h); updatePosition(win.id, x, y) }" />
    </div>

    <!-- 底部任务栏 - 毛玻璃效果 -->
    <div class="taskbar">
      <div class="taskbar-left">
        <div class="taskbar-apps">
          <div v-for="win in windows" :key="win.id" class="taskbar-app"
            :class="{ active: activeWindowId === win.id && !win.minimized }" @click="handleTaskbarClick(win.id)">
            <div class="taskbar-app-icon" :style="{ color: win.color }"><span>{{ win.icon }}</span></div>
            <span class="taskbar-app-name">{{ win.name }}</span>
            <div class="taskbar-app-indicator" :class="{ visible: true, glowing: activeWindowId === win.id && !win.minimized, dimmed: win.minimized }" />
          </div>
        </div>
      </div>
      <div class="taskbar-right">
        <!-- OA 审批快捷按钮 -->
        <el-popover placement="top-end" :width="350" trigger="click" popper-class="oa-popover">
          <template #reference>
            <div class="taskbar-icon-btn oa-btn" title="OA 审批">
              <span style="font-size:16px">📋</span>
              <span v-if="oaPendingCount > 0" class="oa-badge">{{ oaPendingCount }}</span>
            </div>
          </template>
          <div class="oa-popover-content">
            <div class="oa-popover-header">
              <span>📋 OA 审批待办</span>
              <span v-if="oaPendingCount > 0" class="oa-popover-badge">{{ oaPendingCount }} 条</span>
            </div>
            <div class="oa-popover-actions">
              <el-button size="small" type="primary" @click="openOA('pending')">待我审批</el-button>
              <el-button size="small" @click="openOA('create')">发起审批</el-button>
              <el-button size="small" @click="openOA('dashboard')">工作台</el-button>
            </div>
          </div>
        </el-popover>

        <div class="taskbar-time">
          <span class="time-text">{{ currentTime }}</span>
          <span class="date-text">{{ currentDate }}</span>
        </div>

        <!-- 换肤按钮 -->
        <el-popover placement="top-end" :width="340" trigger="click" popper-class="skin-popover">
          <template #reference>
            <div class="taskbar-icon-btn" title="更换壁纸">
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><circle cx="12" cy="12" r="10"/><path d="M12 2a14.5 14.5 0 0 0 0 20 14.5 14.5 0 0 0 0-20"/><path d="M2 12h20"/></svg>
            </div>
          </template>
          <div class="skin-picker">
            <div class="skin-section-title">🎨 纯色背景</div>
            <div class="skin-grid">
              <div v-for="c in solidColors" :key="c.key" class="skin-item" :class="{ active: wallpaper === c.key }"
                @click="setWallpaper(c.key)">
                <div class="skin-preview" :style="{ background: c.color }" />
                <span class="skin-label">{{ c.name }}</span>
              </div>
            </div>

            <div class="skin-section-title">🌈 渐变风格</div>
            <div class="skin-grid">
              <div v-for="c in gradientColors" :key="c.key" class="skin-item" :class="{ active: wallpaper === c.key }"
                @click="setWallpaper(c.key)">
                <div class="skin-preview" :style="{ background: `linear-gradient(135deg, ${c.c1}, ${c.c2})` }" />
                <span class="skin-label">{{ c.name }}</span>
              </div>
            </div>

            <div class="skin-section-title">🖼️ 精美壁纸</div>
            <div class="skin-grid">
              <div v-for="c in scenicWallpapers" :key="c.key" class="skin-item" :class="{ active: wallpaper === c.key }"
                @click="setWallpaper(c.key)" style="width:96px">
                <div class="skin-preview-lg" :style="c.style" />
                <span class="skin-label">{{ c.name }}</span>
              </div>
            </div>
          </div>
        </el-popover>

        <!-- 用户头像 -->
        <el-popover placement="top-end" :width="300" trigger="click" :show-after="0" :hide-after="100" popper-class="user-popover" @show="loadUserInfo">
          <template #reference>
            <div class="user-avatar-btn">
              <div class="user-avatar-circle">{{ userInitial }}</div>
            </div>
          </template>
          <div class="user-panel">
            <!-- 顶部身份区 -->
            <div class="up-banner">
              <div class="up-banner-bg" />
              <div class="up-avatar">
                <div class="up-avatar-ring">
                  <div class="up-avatar-inner">{{ userInitial }}</div>
                </div>
                <div class="up-status-dot" />
              </div>
              <div class="up-identity">
                <div class="up-name">{{ userInfo.displayName || userInfo.username }}</div>
                <div class="up-email">{{ userInfo.email || '未设置邮箱' }}</div>
              </div>
              <div class="up-role-badge" :class="userInfo.role === 'admin' ? 'role-admin' : 'role-user'">
                {{ userInfo.role === 'admin' ? '管理员' : '普通用户' }}
              </div>
            </div>

            <!-- 信息区 -->
            <div class="up-section">
              <div class="up-info-row">
                <span class="up-info-label">用户名</span>
                <span class="up-info-value">{{ userInfo.username }}</span>
              </div>
              <div class="up-info-row">
                <span class="up-info-label">角色</span>
                <span class="up-info-value">{{ userInfo.role }}</span>
              </div>
              <div class="up-info-row">
                <span class="up-info-label">状态</span>
                <span class="up-info-value up-status-active">● 在线</span>
              </div>
            </div>

            <!-- 权限区 -->
            <div class="up-section" v-if="userInfo.permissions?.length">
              <div class="up-section-title">
                <span>应用权限</span>
                <span class="up-perm-count">{{ userInfo.permissions.length }}</span>
              </div>
              <div class="up-perm-grid">
                <div v-for="p in userInfo.permissions" :key="p" class="up-perm-chip">
                  <span class="up-perm-icon">{{ permIcon(p) }}</span>
                  <span>{{ permLabel(p) }}</span>
                </div>
              </div>
            </div>

            <!-- 操作区 -->
            <div class="up-actions">
              <button class="up-btn up-btn-logout" @click="handleLogout">
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"/><polyline points="16 17 21 12 16 7"/><line x1="21" y1="12" x2="9" y2="12"/></svg>
                退出登录
              </button>
            </div>
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

// OA 审批待办数
const oaPendingCount = ref(0)
let oaPollTimer: number | null = null
async function pollOAStatus() {
  try {
    const token = localStorage.getItem('token')
    if (!token) return
    const res = await axios.get('/api/oa/notifications/unread-count', {
      headers: { Authorization: `Bearer ${token}` }
    })
    oaPendingCount.value = res.data?.data || 0
  } catch {}
}
function openOA(page: string) {
  const pathMap: Record<string, string> = { dashboard: '/oa/dashboard', pending: '/oa/pending', create: '/oa/create' }
  const path = pathMap[page] || '/oa/dashboard'
  // Use store.openApp to open/create the window
  store.openApp('sub-oa')
  // Navigate to the correct page once the app is loaded
  setTimeout(() => {
    const container = document.querySelector('[data-qiankun="sub-oa"]')
    if (container) {
      const appEl = container.querySelector('#app')
      const vueApp = (appEl as any)?.__vue_app__
      if (vueApp?.config?.globalProperties?.$router) {
        vueApp.config.globalProperties.$router.push(path)
      }
    }
  }, 500)
}
const { windows, activeWindowId, openApp, closeWindow, minimizeWindow, toggleMaximize, focusWindow, updatePosition, updateSize } = store

const token = ref(localStorage.getItem('jwt_token') || '')
const isLoggedIn = ref(!!token.value)
const userInfo = ref<any>({})
const userInitial = computed(() => (userInfo.value.displayName || userInfo.value.username || 'U').charAt(0).toUpperCase())
const userPerms = ref<string[]>([])

function onLogin(data: any) {
  token.value = data.token
  isLoggedIn.value = true
  localStorage.setItem('jwt_token', data.token)
  userInfo.value = data.user || {}
  userPerms.value = data.user?.permissions || []
  localStorage.setItem('user_info', JSON.stringify(data.user || {}))
  loadUserSettings()
}

async function loadUserInfo() {
  try {
    const res = await axios.get('/api/settings', { headers: { Authorization: `Bearer ${token.value}`, 'X-User-Id': String(userInfo.value.id) } })
    if (res.data.code === 200) userInfo.value = { ...userInfo.value, ...res.data.data }
  } catch {}
}

function handleLogout() {
  localStorage.removeItem('jwt_token'); localStorage.removeItem('user_info')
  token.value = ''; isLoggedIn.value = false; userInfo.value = {}
  for (const w of [...windows]) closeWindow(w.id)
}

// ── 权限图标/标签映射 ──
const permMap: Record<string, { icon: string; label: string }> = {
  'nlp': { icon: '🧠', label: 'NLP 知识库' },
  'recommend': { icon: '🎯', label: '推荐系统' },
  'cv': { icon: '👁️', label: '计算机视觉' },
  'mlops': { icon: '⚙️', label: 'MLOps 平台' },
  'dbadmin': { icon: '🗄️', label: '数据管理' },
  'system-manager': { icon: '👥', label: '系统管理' },
}
function permIcon(p: string) { return permMap[p]?.icon || '📦' }
function permLabel(p: string) { return permMap[p]?.label || p }

// ── 壁纸系统 ──
const wallpaper = ref('midnight')

const solidColors = [
  { key: 'midnight', name: '午夜蓝', color: '#0f172a' },
  { key: 'slate', name: '石板灰', color: '#1e293b' },
  { key: 'charcoal', name: '炭灰', color: '#2d3748' },
  { key: 'navy', name: '海军蓝', color: '#172554' },
]

const gradientColors = [
  { key: 'sunset', name: '日落', c1: '#781440', c2: '#fa783c' },
  { key: 'ocean', name: '海洋', c1: '#0a3264', c2: '#1496b4' },
  { key: 'forest', name: '森林', c1: '#143c28', c2: '#50963c' },
  { key: 'aurora', name: '极光', c1: '#14143c', c2: '#3cc896' },
]

const scenicWallpapers = [
  { key: 'cosmos', name: '星空', style: 'background:radial-gradient(ellipse at 70% 30%,#3b82f6 0%,#1e3a8a 30%,#0f172a 70%,#020617 100%)' },
  { key: 'lavender', name: '薰衣草', style: 'background:radial-gradient(ellipse at 50% 50%,#c084fc 0%,#7c3aed 35%,#281a40 70%,#120826 100%)' },
  { key: 'dusk', name: '黄昏山', style: 'background:linear-gradient(180deg,#1e1e3c 0%,#b45078 45%,#fa963c 75%,#1e293b 100%)' },
  { key: 'dawn', name: '黎明峰', style: 'background:linear-gradient(180deg,#6496c8 0%,#facc96 50%,#3c3228 85%,#1e1e28 100%)' },
]

const currentBg = computed(() => {
  // 纯色
  const solid = solidColors.find(c => c.key === wallpaper.value)
  if (solid) return solid.color
  // 渐变
  const grad = gradientColors.find(c => c.key === wallpaper.value)
  if (grad) return `linear-gradient(135deg, ${grad.c1}, ${grad.c2})`
  // 风景
  const scenic = scenicWallpapers.find(c => c.key === wallpaper.value)
  if (scenic) return scenic.style.split(':')[1]?.trim() || '#0f172a'
  return '#0f172a'
})

async function setWallpaper(key: string) {
  wallpaper.value = key
  try {
    await axios.put('/api/settings', { wallpaper: key },
      { headers: { Authorization: `Bearer ${token.value}`, 'X-User-Id': String(userInfo.value.id) } })
  } catch {}
}

async function loadUserSettings() {
  try {
    const res = await axios.get('/api/settings',
      { headers: { Authorization: `Bearer ${token.value}`, 'X-User-Id': String(userInfo.value.id) } })
    if (res.data.code === 200 && res.data.data?.wallpaper) {
      wallpaper.value = res.data.data.wallpaper
    }
  } catch {}
}

// Init
onMounted(async () => {
  if (isLoggedIn.value) {
    const cached = localStorage.getItem('user_info')
    if (cached) { try { const u = JSON.parse(cached); userInfo.value = u; userPerms.value = u.permissions || [] } catch {} }
    loadUserSettings()
    // Poll OA status
    pollOAStatus()
    oaPollTimer = window.setInterval(pollOAStatus, 30000)
  }
})

// ── App permission filtering ──
const appPermKeyMap: Record<string, string> = {
  'sub-nlp': 'nlp', 'sub-recommend': 'recommend', 'sub-cv': 'cv',
  'sub-mlops': 'mlops', 'sub-sql': 'dbadmin', 'system-manager': 'system-manager',
  'sub-cicd': 'cicd', 'sub-oa': 'oa',
}
const desktopApps = APP_DEFS
const visibleApps = computed(() => {
  if (userPerms.value.length === 0) return desktopApps
  return desktopApps.filter(app => userPerms.value.includes(appPermKeyMap[app.id] || app.id))
})

// ── Micro Apps ──
const microApps = new Map<string, MicroApp>()
const currentTime = ref(''); const currentDate = ref(''); let clockTimer: number

function handleTaskbarClick(appId: string) {
  const win = store.getWindow(appId)
  if (!win) return
  if (win.minimized || activeWindowId !== appId) focusWindow(appId)
  else minimizeWindow(appId)
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
    const container = document.getElementById(`app-container-${win.id}`)
    if (!container) continue
    try {
      const app = loadMicroApp({ name: win.id, entry: win.entry, container: `#app-container-${win.id}` },
        { sandbox: { experimentalStyleIsolation: true } })
      microApps.set(win.id, app); store.setMounted(win.id)
    } catch (e) { console.error(`Failed to load ${win.id}:`, e) }
  }
}, { deep: true })

watch(() => windows.length, (newLen, oldLen) => {
  if (newLen < (oldLen ?? 0)) {
    const currentIds = new Set(windows.map(w => w.id))
    for (const [id, app] of microApps) {
      if (!currentIds.has(id)) {
        app.unmount()
        const c = document.getElementById(`app-container-${id}`)
        if (c) { c.innerHTML = ''; c.removeAttribute('data-qiankun') }
        document.querySelectorAll(`style[data-qiankun="${id}"]`).forEach(el => el.remove())
        microApps.delete(id)
      }
    }
  }
})

onMounted(() => { updateClock(); clockTimer = window.setInterval(updateClock, 10000) })
onUnmounted(() => { clearInterval(clockTimer); if (oaPollTimer) clearInterval(oaPollTimer); for (const [, app] of microApps) app.unmount() })
</script>

<style>
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

* { margin:0; padding:0; box-sizing:border-box; }

:root {
  --taskbar-height: 48px;

  /* 窗口主题变量 */
  --bg-window: #ffffff;
  --bg-window-content: #ffffff;
  --bg-titlebar: #f8f9fb;
  --border-window: rgba(0, 0, 0, 0.08);
  --border-window-focused: rgba(59, 130, 246, 0.3);
  --text-primary: #1a1d28;
  --text-secondary: #475569;
  --text-muted: #94a3b8;
  --accent-blue: #3b82f6;
}

html, body, #app {
  height:100%; font-family:'Outfit',-apple-system,BlinkMacSystemFont,sans-serif;
  overflow:hidden; background:#0f172a; color:#e2e8f0; user-select:none;
}

#desktop { height:100vh; position:relative; overflow:hidden; }

.desktop-wallpaper {
  position:absolute; inset:0; z-index:0;
  transition: background 0.6s ease;
}

/* ── Desktop Icons ── */
.desktop-icons {
  position:absolute; top:32px; left:32px;
  display:flex; flex-direction:column; flex-wrap:wrap; gap:10px; z-index:2;
  padding-bottom:calc(var(--taskbar-height)+16px);
  max-height:calc(100vh - var(--taskbar-height) - 48px);
  align-content:flex-start;
}
.desktop-icon {
  display:flex; flex-direction:column; align-items:center; gap:5px;
  padding:10px 14px; border-radius:14px; cursor:pointer; transition:all 0.2s; width:88px;
}
.desktop-icon:hover { background:rgba(255,255,255,0.06); backdrop-filter:blur(12px); }
.icon-image {
  width:52px; height:52px; border-radius:16px;
  display:flex; align-items:center; justify-content:center;
  transition:transform 0.2s; box-shadow:0 4px 16px rgba(0,0,0,0.3);
}
.desktop-icon:hover .icon-image { transform:scale(1.06); }
.icon-emoji { font-size:26px; line-height:1; }
.icon-label {
  font-size:11px; color:rgba(255,255,255,0.7); text-align:center;
  line-height:1.3; font-weight:500; text-shadow:0 1px 4px rgba(0,0,0,0.5);
}

.windows-layer {
  position:absolute; top:0; left:0; right:0; bottom:calc(var(--taskbar-height) + 8px);
  z-index:3; pointer-events:none;
}
.windows-layer > * { pointer-events:auto; }

/* ── Taskbar (高级毛玻璃) ── */
.taskbar {
  position:absolute; bottom:0; left:0; right:0; height:var(--taskbar-height);
  -webkit-backdrop-filter:blur(40px) saturate(2) brightness(0.9);
  /* border-top:1px solid rgba(255,255,255,0.06); */
  display:flex; align-items:center; justify-content:space-between;
  padding:0 10px; z-index:100;
  background: hsla(0,0%,40%,.5);
  box-shadow: 0 0 5px #ccc;
}
/* 顶部高光边线 */
.taskbar::before {
  content:''; position:absolute; top:0; left:0; right:0; height:1px;
  background:linear-gradient(90deg,transparent 5%,rgba(255,255,255,0.12) 30%,rgba(255,255,255,0.18) 50%,rgba(255,255,255,0.12) 70%,transparent 95%);
}
/* 底部微弱内阴影 */
.taskbar::after {
  content:''; position:absolute; bottom:0; left:0; right:0; height:1px;
  background:rgba(0,0,0,0.2);
}

.taskbar-left { display:flex; align-items:center; flex:1; }
.taskbar-apps { display:flex; align-items:center; gap:1px; }

.taskbar-app {
  display:flex; align-items:center; gap:7px; padding:5px 12px; border-radius:8px;
  cursor:pointer; transition:all 0.2s cubic-bezier(0.4,0,0.2,1); position:relative;
}
.taskbar-app:hover { background:rgba(255,255,255,0.08); }
.taskbar-app.active { background:rgba(255,255,255,0.12); }
.taskbar-app:active { transform:scale(0.97); }
.taskbar-app-icon {
  font-size:16px; line-height:1; display:flex; align-items:center;
  filter:drop-shadow(0 1px 2px rgba(0,0,0,0.3));
}
.taskbar-app-name {
  font-size:11.5px; color:rgba(255,255,255,0.55); font-weight:500;
  transition:color 0.2s; letter-spacing:-0.2px;
}
.taskbar-app.active .taskbar-app-name { color:rgba(255,255,255,0.9); }
.taskbar-app:hover .taskbar-app-name { color:rgba(255,255,255,0.75); }

.taskbar-app-indicator {
  position:absolute; bottom:2px; left:50%; transform:translateX(-50%);
  height:2px; border-radius:2px; transition:all 0.35s cubic-bezier(0.4,0,0.2,1);
  opacity:0.9;
}
.taskbar-app-indicator.visible { width:16px; background:rgba(255,255,255,0.25); }
.taskbar-app-indicator.glowing { width:24px; background:#60a5fa; box-shadow:0 0 8px rgba(96,165,250,0.5); opacity:1; }
.taskbar-app-indicator.dimmed { width:8px; background:rgba(255,255,255,0.15); }

.taskbar-right { display:flex; align-items:center; gap:8px; }
.taskbar-time { display:flex; flex-direction:column; align-items:flex-end; padding:2px 8px; }
.time-text {
  font-size:13px; font-weight:600; color:rgba(255,255,255,0.8);
  font-family:'JetBrains Mono',monospace; letter-spacing:-0.3px;
}
.date-text {
  font-size:10.5px; color:rgba(255,255,255,0.35); letter-spacing:-0.2px;
}

/* Taskbar icon buttons */
.taskbar-icon-btn {
  width:30px; height:30px; border-radius:7px;
  display:flex; align-items:center; justify-content:center;
  cursor:pointer; transition:all 0.2s cubic-bezier(0.4,0,0.2,1);
  color:rgba(255,255,255,0.4);
}
.taskbar-icon-btn:hover { background:rgba(255,255,255,0.1); color:rgba(255,255,255,0.8); }
.taskbar-icon-btn:active { transform:scale(0.92); }
.taskbar-icon-btn.oa-btn { position: relative; }
.oa-badge {
  position: absolute; top: -2px; right: -2px;
  background: #ff4d4f; color: #fff;
  font-size: 10px; min-width: 16px; height: 16px; line-height: 16px;
  border-radius: 8px; text-align: center; padding: 0 4px; font-weight: 600;
}

/* User avatar */
.user-avatar-btn { width:30px; height:30px; border-radius:50%; cursor:pointer; transition:all 0.2s; }
.user-avatar-btn:hover { transform:scale(1.08); box-shadow:0 0 0 2px rgba(255,255,255,0.15); }
.user-avatar-circle {
  width:30px; height:30px; border-radius:50%;
  background:linear-gradient(135deg,#3b82f6,#8b5cf6);
  color:#fff; font-size:13px; font-weight:700;
  display:flex; align-items:center; justify-content:center;
}

/* ── User Panel (企业级) ── */
.user-panel {
  font-family:'Outfit',-apple-system,BlinkMacSystemFont,sans-serif;
  margin:-12px; padding:0;
  overflow:hidden;
}

/* 顶部身份区 */
.up-banner {
  position:relative; padding:24px 20px 16px;
  background:linear-gradient(135deg,#1e293b 0%,#0f172a 100%);
  overflow:hidden;
}
.up-banner-bg {
  position:absolute; inset:0;
  background:
    radial-gradient(circle at 80% 20%,rgba(59,130,246,0.15) 0%,transparent 50%),
    radial-gradient(circle at 20% 80%,rgba(139,92,246,0.1) 0%,transparent 50%);
}
.up-avatar {
  position:relative; display:inline-block; margin-bottom:12px;
}
.up-avatar-ring {
  width:56px; height:56px; border-radius:50%; padding:2px;
  background:linear-gradient(135deg,#3b82f6,#8b5cf6,#ec4899);
  box-shadow:0 4px 20px rgba(59,130,246,0.3);
}
.up-avatar-inner {
  width:100%; height:100%; border-radius:50%;
  background:linear-gradient(135deg,#3b82f6,#8b5cf6);
  color:#fff; font-size:22px; font-weight:700;
  display:flex; align-items:center; justify-content:center;
  border:2px solid #1e293b;
}
.up-status-dot {
  position:absolute; bottom:2px; right:2px;
  width:12px; height:12px; border-radius:50%;
  background:#22c55e; border:2px solid #1e293b;
  box-shadow:0 0 8px rgba(34,197,94,0.5);
}
.up-identity { position:relative; }
.up-name {
  font-size:17px; font-weight:700; color:#f1f5f9;
  letter-spacing:-0.3px; line-height:1.2;
}
.up-email {
  font-size:12px; color:#94a3b8; margin-top:2px;
  font-family:'JetBrains Mono',monospace;
}
.up-role-badge {
  position:absolute; top:20px; right:16px;
  padding:3px 10px; border-radius:20px;
  font-size:11px; font-weight:600; letter-spacing:0.3px;
}
.role-admin {
  background:rgba(239,68,68,0.15); color:#fca5a5;
  border:1px solid rgba(239,68,68,0.2);
}
.role-user {
  background:rgba(59,130,246,0.15); color:#93c5fd;
  border:1px solid rgba(59,130,246,0.2);
}

/* 信息区 */
.up-section {
  padding:14px 20px;
  border-bottom:1px solid #f1f5f9;
}
.up-section:last-of-type { border-bottom:none; }
.up-section-title {
  display:flex; align-items:center; justify-content:space-between;
  font-size:11px; font-weight:600; color:#94a3b8;
  text-transform:uppercase; letter-spacing:0.8px;
  margin-bottom:10px;
}
.up-perm-count {
  background:#f1f5f9; color:#64748b;
  padding:1px 7px; border-radius:10px;
  font-size:10px; font-weight:700;
}
.up-info-row {
  display:flex; align-items:center; justify-content:space-between;
  padding:6px 0;
}
.up-info-row + .up-info-row { border-top:1px solid #f8fafc; }
.up-info-label {
  font-size:12px; color:#94a3b8; font-weight:500;
}
.up-info-value {
  font-size:13px; color:#1e293b; font-weight:600;
  font-family:'JetBrains Mono',monospace;
}
.up-status-active {
  color:#22c55e; font-family:'Outfit',sans-serif;
  font-size:12px;
}

/* 权限网格 */
.up-perm-grid {
  display:flex; flex-wrap:wrap; gap:6px;
}
.up-perm-chip {
  display:inline-flex; align-items:center; gap:4px;
  padding:4px 10px; border-radius:6px;
  background:#f8fafc; border:1px solid #e2e8f0;
  font-size:12px; color:#475569; font-weight:500;
  transition:all 0.15s;
}
.up-perm-chip:hover {
  background:#eff6ff; border-color:#bfdbfe; color:#2563eb;
}
.up-perm-icon { font-size:13px; }

/* 操作区 */
.up-actions {
  padding:12px 20px 16px;
}
.up-btn {
  width:100%; padding:9px 0; border:none; border-radius:8px;
  font-size:13px; font-weight:600; cursor:pointer;
  display:flex; align-items:center; justify-content:center; gap:6px;
  transition:all 0.2s; font-family:'Outfit',sans-serif;
}
.up-btn-logout {
  background:#fef2f2; color:#dc2626; border:1px solid #fecaca;
}
.up-btn-logout:hover {
  background:#fee2e2; border-color:#fca5a5;
  box-shadow:0 2px 8px rgba(220,38,38,0.1);
}
.up-btn-logout:active {
  transform:scale(0.98);
}

/* ── Skin Picker ── */
.skin-picker { max-height:420px; overflow-y:auto; }
.skin-section-title { font-size:12px; font-weight:600; color:#6b7280; margin:10px 0 6px; }
.skin-section-title:first-child { margin-top:0; }
.skin-grid { display:flex; flex-wrap:wrap; gap:8px; }
.skin-item { display:flex; flex-direction:column; align-items:center; gap:3px; cursor:pointer; width:72px; }
.skin-item.active .skin-label { color:#3b82f6; font-weight:600; }
.skin-item.active .skin-preview { box-shadow:0 0 0 2px #3b82f6,0 0 0 3px rgba(59,130,246,0.3); }
.skin-item.active .skin-preview-lg { box-shadow:0 0 0 2px #3b82f6,0 0 0 3px rgba(59,130,246,0.3); }
.skin-preview { width:68px; height:44px; border-radius:6px; transition:all 0.15s; }
.skin-preview-lg { width:92px; height:56px; border-radius:6px; transition:all 0.15s; }
.skin-preview:hover, .skin-preview-lg:hover { transform:scale(1.05); }
.skin-label { font-size:10px; color:#9ca3af; text-align:center; }

::-webkit-scrollbar { width:5px; }
::-webkit-scrollbar-track { background:transparent; }
::-webkit-scrollbar-thumb { background:rgba(255,255,255,0.1); border-radius:3px; }
</style>

<!-- 全局修复 popover 在 Shadow DOM 下的样式 -->
<style>
.skin-popover { z-index: 10000 !important; }
.user-popover {
  z-index: 10000 !important;
  padding: 0 !important;
  border-radius: 14px !important;
  box-shadow: 0 12px 40px rgba(0,0,0,0.15), 0 4px 12px rgba(0,0,0,0.08) !important;
  border: 1px solid #e2e8f0 !important;
  overflow: hidden !important;
}
.user-popover .el-popover-arrow { display: none !important; }
</style>
