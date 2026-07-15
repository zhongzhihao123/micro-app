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
                <el-tag size="small" :type="userInfo.role === 'admin' ? 'danger' : 'info'" style="margin-top:4px">{{ userInfo.role }}</el-tag>
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
            <el-button type="danger" plain size="small" style="width:100%" @click="handleLogout">🚪 退出登录</el-button>
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
  }
})

// ── App permission filtering ──
const appPermKeyMap: Record<string, string> = {
  'sub-nlp': 'nlp', 'sub-recommend': 'recommend', 'sub-cv': 'cv',
  'sub-mlops': 'mlops', 'sub-sql': 'dbadmin', 'system-manager': 'system-manager',
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
onUnmounted(() => { clearInterval(clockTimer); for (const [, app] of microApps) app.unmount() })
</script>

<style>
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

* { margin:0; padding:0; box-sizing:border-box; }

:root {
  --taskbar-height: 48px;
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
  display:flex; flex-direction:column; gap:10px; z-index:2;
  padding-bottom:calc(var(--taskbar-height)+16px);
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
  position:absolute; inset:0; bottom:calc(var(--taskbar-height)+8px); z-index:3; pointer-events:none;
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

/* User avatar */
.user-avatar-btn { width:30px; height:30px; border-radius:50%; cursor:pointer; transition:all 0.2s; }
.user-avatar-btn:hover { transform:scale(1.08); box-shadow:0 0 0 2px rgba(255,255,255,0.15); }
.user-avatar-circle {
  width:30px; height:30px; border-radius:50%;
  background:linear-gradient(135deg,#3b82f6,#8b5cf6);
  color:#fff; font-size:13px; font-weight:700;
  display:flex; align-items:center; justify-content:center;
}

/* User menu */
.user-menu-header { display:flex; align-items:center; gap:12px; }
.um-avatar {
  width:44px; height:44px; border-radius:50%;
  background:linear-gradient(135deg,#3b82f6,#8b5cf6);
  color:#fff; font-size:20px; font-weight:700;
  display:flex; align-items:center; justify-content:center; flex-shrink:0;
}
.um-info { display:flex; flex-direction:column; }
.um-name { font-size:15px; font-weight:600; color:#1a1d28; }
.um-email { font-size:12px; color:#9ca3af; }
.um-perms-label { font-size:12px; color:#9ca3af; }

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
</style>
