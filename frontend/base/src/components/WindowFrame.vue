<template>
  <div
    v-show="!window.minimized"
    class="window-frame"
    :class="{
      maximized: window.maximized,
      focused: isFocused,
      minimizing: isMinimizing
    }"
    :style="windowStyle"
    @mousedown="focus"
  >
    <!-- 标题栏 -->
    <div class="window-titlebar" @mousedown="startDrag" @dblclick="$emit('toggleMaximize')">
      <div class="titlebar-left">
        <span class="titlebar-icon">{{ window.icon }}</span>
        <span class="titlebar-title">{{ window.title }}</span>
      </div>
      <div class="titlebar-controls">
        <button class="control-btn minimize" @click.stop="handleMinimize" title="最小化">
          <svg width="12" height="12" viewBox="0 0 12 12"><rect y="5" width="12" height="1.5" rx="0.75" fill="currentColor"/></svg>
        </button>
        <button class="control-btn maximize" @click.stop="$emit('toggleMaximize')" :title="window.maximized ? '还原' : '最大化'">
          <svg v-if="!window.maximized" width="12" height="12" viewBox="0 0 12 12"><rect x="1" y="1" width="10" height="10" rx="1.5" fill="none" stroke="currentColor" stroke-width="1.2"/></svg>
          <svg v-else width="12" height="12" viewBox="0 0 12 12"><rect x="2.5" y="0.5" width="8" height="8" rx="1.5" fill="none" stroke="currentColor" stroke-width="1.2"/><rect x="0.5" y="2.5" width="8" height="8" rx="1.5" fill="var(--bg-window)" stroke="currentColor" stroke-width="1.2"/></svg>
        </button>
        <button class="control-btn close" @click.stop="$emit('close')" title="关闭">
          <svg width="12" height="12" viewBox="0 0 12 12"><path d="M1 1l10 10M11 1L1 11" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/></svg>
        </button>
      </div>
    </div>

    <!-- 内容区 -->
    <div class="window-content" ref="contentRef">
      <div v-if="!window.mounted" class="window-loading">
        <div class="loading-spinner" />
        <span>加载中...</span>
      </div>
      <div :id="'app-container-' + window.id" class="app-container" :class="{ hidden: !window.mounted }" />
    </div>

    <!-- 拖拽调整大小的手柄 -->
    <template v-if="!window.maximized">
      <div class="resize-handle resize-n" @mousedown.stop="startResize($event, 'n')" />
      <div class="resize-handle resize-s" @mousedown.stop="startResize($event, 's')" />
      <div class="resize-handle resize-e" @mousedown.stop="startResize($event, 'e')" />
      <div class="resize-handle resize-w" @mousedown.stop="startResize($event, 'w')" />
      <div class="resize-handle resize-ne" @mousedown.stop="startResize($event, 'ne')" />
      <div class="resize-handle resize-nw" @mousedown.stop="startResize($event, 'nw')" />
      <div class="resize-handle resize-se" @mousedown.stop="startResize($event, 'se')" />
      <div class="resize-handle resize-sw" @mousedown.stop="startResize($event, 'sw')" />
    </template>
  </div>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'
import type { AppWindow } from '@/stores/windowStore'

const props = defineProps<{
  window: AppWindow
  isFocused: boolean
}>()

const emit = defineEmits<{
  close: []
  minimize: []
  toggleMaximize: []
  focus: []
  move: [x: number, y: number]
  resize: [width: number, height: number, x: number, y: number]
}>()

const isMinimizing = ref(false)

function handleMinimize() {
  if (props.window.maximized) return // 最大化状态不缩小动画
  isMinimizing.value = true
  // 动画结束后通知父组件
  setTimeout(() => {
    isMinimizing.value = false
    emit('minimize')
  }, 350)
}

const windowStyle = computed(() => {
  if (props.window.maximized) {
    return {
      left: '0',
      top: '0',
      right: '0',
      bottom: '0',
      width: 'auto',
      height: 'auto',
      zIndex: props.window.zIndex,
      borderRadius: '0',
      transition: 'none',
    }
  }
  return {
    left: props.window.x + 'px',
    top: props.window.y + 'px',
    width: props.window.width + 'px',
    height: props.window.height + 'px',
    maxHeight: 'calc(100vh - var(--taskbar-height) - 16px)',
    zIndex: props.window.zIndex,
  }
})

function focus() {
  emit('focus')
}

// ── 拖拽移动 ──
function startDrag(e: MouseEvent) {
  if ((e.target as HTMLElement).closest('.control-btn')) return
  if (props.window.maximized) return

  const startX = e.clientX
  const startY = e.clientY
  const origX = props.window.x
  const origY = props.window.y

  function onMove(ev: MouseEvent) {
    emit('move', origX + ev.clientX - startX, origY + ev.clientY - startY)
  }

  function onUp() {
    document.removeEventListener('mousemove', onMove)
    document.removeEventListener('mouseup', onUp)
  }

  document.addEventListener('mousemove', onMove)
  document.addEventListener('mouseup', onUp)
}

// ── 调整大小 ──
function startResize(e: MouseEvent, dir: string) {
  e.preventDefault()
  const startX = e.clientX
  const startY = e.clientY
  const origW = props.window.width
  const origH = props.window.height
  const origLeft = props.window.x
  const origTop = props.window.y

  function onMove(ev: MouseEvent) {
    const dx = ev.clientX - startX
    const dy = ev.clientY - startY
    let newW = origW, newH = origH, newX = origLeft, newY = origTop

    if (dir.includes('e')) newW = origW + dx
    if (dir.includes('s')) newH = origH + dy
    if (dir.includes('w')) { newW = origW - dx; newX = origLeft + dx }
    if (dir.includes('n')) { newH = origH - dy; newY = origTop + dy }

    emit('resize', newW, newH, newX, newY)
  }

  function onUp() {
    document.removeEventListener('mousemove', onMove)
    document.removeEventListener('mouseup', onUp)
  }

  document.addEventListener('mousemove', onMove)
  document.addEventListener('mouseup', onUp)
}
</script>

<style scoped>
.window-frame {
  position: absolute;
  background: var(--bg-window);
  border: 1px solid var(--border-window);
  border-radius: 12px;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  box-shadow:
    0 0 0 1px rgba(0, 0, 0, 0.02),
    0 4px 24px rgba(0, 0, 0, 0.08),
    0 1px 4px rgba(0, 0, 0, 0.04);
  transition: box-shadow 0.2s, border-color 0.2s;
  transform-origin: center bottom;
}

.window-frame.focused {
  border-color: var(--border-window-focused);
  box-shadow:
    0 0 0 1px rgba(59, 130, 246, 0.12),
    0 8px 32px rgba(0, 0, 0, 0.1),
    0 2px 6px rgba(0, 0, 0, 0.05);
}

.window-frame.maximized {
  border-radius: 0;
  border: none;
  box-shadow: none;
}

/* ── 最小化动画 ── */
.window-frame.minimizing {
  animation: minimizeWindow 0.35s cubic-bezier(0.55, 0, 1, 0.45) forwards;
  pointer-events: none;
}

@keyframes minimizeWindow {
  0% {
    opacity: 1;
    transform: scale(1) translateY(0);
  }
  100% {
    opacity: 0;
    transform: scale(0.3) translateY(80px);
  }
}

/* ── Titlebar ── */
.window-titlebar {
  height: 40px;
  background: var(--bg-titlebar);
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 8px 0 14px;
  cursor: grab;
  user-select: none;
  flex-shrink: 0;
  border-bottom: 1px solid rgba(0, 0, 0, 0.06);
}

.window-titlebar:active {
  cursor: grabbing;
}

.titlebar-left {
  display: flex;
  align-items: center;
  gap: 8px;
}

.titlebar-icon {
  font-size: 15px;
  line-height: 1;
}

.titlebar-title {
  font-size: 12.5px;
  font-weight: 500;
  color: var(--text-secondary);
  letter-spacing: -0.1px;
}

.titlebar-controls {
  display: flex;
  align-items: center;
  gap: 6px;
}

.control-btn {
  width: 14px;
  height: 14px;
  border-radius: 50%;
  border: none;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0;
  transition: all 0.15s;
  color: transparent;
  flex-shrink: 0;
}

.control-btn:hover {
  color: rgba(0, 0, 0, 0.6);
}

.control-btn.close {
  background: #ff5f57;
}

.control-btn.minimize {
  background: #febc2e;
}

.control-btn.maximize {
  background: #28c840;
}

.control-btn.close:hover {
  background: #ff3b30;
}

.control-btn.minimize:hover {
  background: #f0a500;
}

.control-btn.maximize:hover {
  background: #1fa835;
}

/* ── Content ── */
.window-content {
  flex: 1;
  position: relative;
  overflow: hidden;
  background: var(--bg-window-content);
}

.app-container {
  width: 100%;
  height: 100%;
}

.app-container.hidden {
  display: none;
}

.window-loading {
  position: absolute;
  inset: 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 12px;
  color: var(--text-muted);
  font-size: 13px;
}

.loading-spinner {
  width: 28px;
  height: 28px;
  border: 2.5px solid rgba(0, 0, 0, 0.08);
  border-top-color: var(--accent-blue);
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

/* ── Resize handles ── */
.resize-handle {
  position: absolute;
  z-index: 20;
}

.resize-n, .resize-s {
  left: 8px;
  right: 8px;
  height: 6px;
}

.resize-e, .resize-w {
  top: 8px;
  bottom: 8px;
  width: 6px;
}

.resize-n { top: -3px; cursor: n-resize; }
.resize-s { bottom: -3px; cursor: s-resize; }
.resize-e { right: -3px; cursor: e-resize; }
.resize-w { left: -3px; cursor: w-resize; }

.resize-ne, .resize-nw, .resize-se, .resize-sw {
  width: 14px;
  height: 14px;
}

.resize-ne { top: -3px; right: -3px; cursor: ne-resize; }
.resize-nw { top: -3px; left: -3px; cursor: nw-resize; }
.resize-se { bottom: -3px; right: -3px; cursor: se-resize; }
.resize-sw { bottom: -3px; left: -3px; cursor: sw-resize; }
.window-frame:not(.focused) .control-btn {
  opacity: 0.7;
}

.window-frame:not(.focused) .control-btn:hover {
  opacity: 1;
}
</style>
