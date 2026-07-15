<template>
  <!-- 登录弹窗 -->
  <LoginDialog :visible="!isLoggedIn" @login="onLogin" />

  <!-- 桌面 -->
  <div v-if="isLoggedIn" id="desktop">
    <!-- 桌面壁纸 -->
    <div class="desktop-wallpaper">
      <div class="wallpaper-gradient" />
    </div>

    <!-- 桌面图标 -->
    <div class="desktop-icons">
      <div
        v-for="app in desktopApps"
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
        <!-- 只显示已打开的窗口 -->
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
      </div>
    </div>
  </div>
  <!-- end desktop -->
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, watch, nextTick } from 'vue'
import { useWindowStore, APP_DEFS } from '@/stores/windowStore'
import { loadMicroApp } from 'qiankun'
import type { MicroApp } from 'qiankun'
import WindowFrame from '@/components/WindowFrame.vue'
import LoginDialog from '@/components/LoginDialog.vue'

const store = useWindowStore()
const { windows, activeWindowId, openApp, closeWindow, minimizeWindow, toggleMaximize, focusWindow, updatePosition, updateSize } = store

// ── 登录状态 ──
const token = ref(localStorage.getItem('jwt_token') || '')
const isLoggedIn = ref(!!token.value)

function onLogin(jwt: string) {
  token.value = jwt
  isLoggedIn.value = true
  localStorage.setItem('jwt_token', jwt)
}

const desktopApps = APP_DEFS
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

// ── Clock ──
function updateClock() {
  const now = new Date()
  currentTime.value = now.toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' })
  currentDate.value = now.toLocaleDateString('zh-CN', { month: 'long', day: 'numeric', weekday: 'short' })
}

// ── Mount micro-apps when windows open ──
watch(() => windows.map(w => w.id + w.mounted), async () => {
  await nextTick()
  for (const win of windows) {
    if (win.mounted) continue
    const containerId = `app-container-${win.id}`
    const container = document.getElementById(containerId)
    if (!container) continue

    try {
      const app = loadMicroApp(
        {
          name: win.id,
          entry: win.entry,
          container: `#${containerId}`,
          props: { baseRoute: `/${win.id.replace('sub-', '')}` },
        },
        {
          sandbox: { experimentalStyleIsolation: true },
        },
      )
      microApps.set(win.id, app)
      store.setMounted(win.id)
    } catch (e) {
      console.error(`Failed to load ${win.id}:`, e)
    }
  }
}, { deep: true })

// Cleanup closed windows
watch(() => windows.length, async (newLen, oldLen) => {
  if (newLen < (oldLen ?? 0)) {
    const currentIds = new Set(windows.map(w => w.id))
    for (const [id, app] of microApps) {
      if (!currentIds.has(id)) {
        app.unmount()
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
  for (const [, app] of microApps) {
    app.unmount()
  }
})
</script>

<style>
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

* { margin: 0; padding: 0; box-sizing: border-box; }

:root {
  /* 浅色主题 */
  --bg-deep: #e8ecf1;
  --bg-window: #ffffff;
  --bg-window-content: #f8f9fb;
  --bg-titlebar: #f0f1f4;
  --bg-taskbar: rgba(255, 255, 255, 0.92);
  --border-subtle: rgba(0, 0, 0, 0.06);
  --border-window: rgba(0, 0, 0, 0.08);
  --border-window-focused: rgba(59, 130, 246, 0.35);
  --text-primary: #1a1d28;
  --text-secondary: #6b7280;
  --text-muted: #9ca3af;
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

/* ── Desktop ── */
#desktop {
  height: 100vh;
  position: relative;
  overflow: hidden;
}

.desktop-wallpaper {
  position: absolute;
  inset: 0;
  z-index: 0;
}

.wallpaper-gradient {
  position: absolute;
  inset: 0;
  background:
    linear-gradient(135deg, #e8ecf1 0%, #f0f2f5 30%, #eef1f5 60%, #e4e8ef 100%);
}

/* ── Desktop Icons ── */
.desktop-icons {
  position: absolute;
  top: 32px;
  left: 32px;
  display: flex;
  flex-direction: column;
  gap: 16px;
  z-index: 2;
  /* 留出任务栏的空间 */
  padding-bottom: calc(var(--taskbar-height) + 16px);
}

.desktop-icon {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  padding: 12px 16px;
  border-radius: 14px;
  cursor: pointer;
  transition: all 0.2s;
  width: 88px;
}

.desktop-icon:hover {
  background: rgba(0, 0, 0, 0.04);
}

.icon-image {
  width: 52px;
  height: 52px;
  border-radius: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: transform 0.2s;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
}

.desktop-icon:hover .icon-image {
  transform: scale(1.06);
}

.icon-emoji {
  font-size: 26px;
  line-height: 1;
}

.icon-label {
  font-size: 12px;
  color: var(--text-secondary);
  text-align: center;
  line-height: 1.3;
  font-weight: 500;
}

/* ── Windows Layer ── */
.windows-layer {
  position: absolute;
  inset: 0;
  /* 底部留出 8px 间距，窗口不直接贴任务栏 */
  bottom: calc(var(--taskbar-height) + 8px);
  z-index: 3;
  pointer-events: none;
}

.windows-layer > * {
  pointer-events: auto;
}

/* ── Taskbar (毛玻璃效果) ── */
.taskbar {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  height: var(--taskbar-height);
  background: rgba(255, 255, 255, 0.55);
  backdrop-filter: blur(32px) saturate(1.4);
  -webkit-backdrop-filter: blur(32px) saturate(1.4);
  border-top: 1px solid rgba(255, 255, 255, 0.5);
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 16px;
  z-index: 100;
  box-shadow:
    0 -1px 0 rgba(0, 0, 0, 0.05),
    0 -4px 20px rgba(0, 0, 0, 0.04);
}

/* 任务栏顶部发光边 */
.taskbar::before {
  content: '';
  position: absolute;
  top: 0;
  left: 50%;
  transform: translateX(-50%);
  width: 70%;
  height: 1px;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.8), transparent);
}

.taskbar-left {
  display: flex;
  align-items: center;
  flex: 1;
}

.taskbar-apps {
  display: flex;
  align-items: center;
  gap: 4px;
}

.taskbar-app {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 6px 14px;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s;
  position: relative;
}

.taskbar-app:hover {
  background: rgba(0, 0, 0, 0.04);
}

.taskbar-app.active {
  background: rgba(59, 130, 246, 0.06);
}

.taskbar-app-icon {
  font-size: 16px;
  line-height: 1;
  display: flex;
  align-items: center;
}

.taskbar-app-name {
  font-size: 12px;
  color: var(--text-secondary);
  font-weight: 500;
  transition: color 0.2s;
}

.taskbar-app.active .taskbar-app-name {
  color: var(--text-primary);
}

/* 底部指示条 */
.taskbar-app-indicator {
  position: absolute;
  bottom: 3px;
  left: 50%;
  transform: translateX(-50%);
  height: 2.5px;
  border-radius: 2px;
  transition: all 0.35s cubic-bezier(0.4, 0, 0.2, 1);
}

.taskbar-app-indicator.visible {
  width: 20px;
  background: var(--accent-blue);
}

.taskbar-app-indicator.glowing {
  width: 28px;
  background: var(--accent-cyan);
  box-shadow: 0 0 6px rgba(6, 182, 212, 0.4);
}

.taskbar-app-indicator.dimmed {
  width: 12px;
  background: var(--text-muted);
}

/* Taskbar right */
.taskbar-right {
  display: flex;
  align-items: center;
  gap: 8px;
}

.taskbar-time {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  padding: 2px 8px;
}

.time-text {
  font-size: 13px;
  font-weight: 600;
  color: var(--text-primary);
  font-family: 'JetBrains Mono', monospace;
}

.date-text {
  font-size: 11px;
  color: var(--text-muted);
}

/* ── Scrollbar ── */
::-webkit-scrollbar { width: 5px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: rgba(0, 0, 0, 0.1); border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: rgba(0, 0, 0, 0.2); }
</style>
