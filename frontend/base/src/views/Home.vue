<template>
  <div class="home-page">
    <!-- Headline -->
    <div class="page-headline">
      <div>
        <h1 class="headline-title">AI 平台控制台</h1>
        <p class="headline-desc">{{ currentDate }} · 所有系统运行正常</p>
      </div>
      <div class="headline-badge">
        <span class="badge-dot"></span>
        <span>实时</span>
      </div>
    </div>

    <!-- 统计卡片 -->
    <div class="stats-grid">
      <div v-for="(stat, idx) in stats" :key="stat.title" class="stat-card" :style="{ '--idx': idx }" @click="$router.push(stat.link)">
        <div class="stat-icon" :style="{ background: stat.iconBg, color: stat.iconColor }" v-html="stat.iconSvg"></div>
        <div class="stat-body">
          <div class="stat-label">{{ stat.title }}</div>
          <div class="stat-value">{{ stat.value }}</div>
          <div class="stat-trend" :class="stat.trend > 0 ? 'up' : 'down'">
            <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M18 15l-6-6-6 6"/></svg>
            <span>{{ Math.abs(stat.trend) }}% 较上月</span>
          </div>
        </div>
      </div>
    </div>

    <!-- 主区域 -->
    <div class="home-grid">
      <!-- 服务状态 -->
      <div class="panel panel-services">
        <div class="panel-header">
          <h3 class="panel-title">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><rect x="2" y="2" width="20" height="8" rx="2" ry="2"/><rect x="2" y="14" width="20" height="8" rx="2" ry="2"/><circle cx="6" cy="6" r="1" fill="currentColor"/><circle cx="6" cy="18" r="1" fill="currentColor"/></svg>
            AI 服务状态
          </h3>
          <span class="panel-action">全部在线 →</span>
        </div>
        <div class="service-list">
          <div v-for="svc in services" :key="svc.name" class="service-card" :style="{ '--accent': svc.color }">
            <div class="service-left">
              <div class="service-icon" :style="{ background: svc.color + '18', color: svc.color }">
                <span class="service-emoji">{{ svc.emoji }}</span>
              </div>
              <div class="service-info">
                <div class="service-name">{{ svc.name }}</div>
                <div class="service-desc">{{ svc.desc }}</div>
              </div>
            </div>
            <div class="service-right">
              <div class="service-metrics">
                <div class="metric">
                  <span class="metric-label">延迟</span>
                  <span class="metric-value mono">{{ svc.latency }}ms</span>
                </div>
                <div class="sep" />
                <div class="metric">
                  <span class="metric-label">可用率</span>
                  <span class="metric-value mono">{{ svc.uptime }}%</span>
                </div>
              </div>
              <div class="service-pulse">
                <span class="pulse-ring" />
                <span class="pulse-dot" />
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 系统资源 -->
      <div class="panel panel-resources">
        <div class="panel-header">
          <h3 class="panel-title">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M12 20V10"/><path d="M18 20V4"/><path d="M6 20v-4"/></svg>
            系统资源
          </h3>
          <span class="panel-action">详情 →</span>
        </div>

        <div class="resource-list">
          <div v-for="res in resources" :key="res.name" class="resource-item">
            <div class="resource-head">
              <div class="resource-label">
                <span class="resource-dot" :style="{ background: res.color }"></span>
                <span>{{ res.name }}</span>
              </div>
              <span class="resource-pct mono">{{ res.percent }}%</span>
            </div>
            <div class="resource-bar">
              <div class="resource-bar-fill" :style="{ width: res.percent + '%', background: res.color, boxShadow: `0 0 10px ${res.color}40` }"></div>
            </div>
          </div>
        </div>

        <div class="panel-divider" />

        <div class="quick-entries">
          <div class="quick-label">快速入口</div>
          <div class="quick-grid">
            <button v-for="entry in quickEntries" :key="entry.name" class="quick-btn" :style="{ '--accent': entry.color }" @click="$router.push(entry.link)">
              <span class="quick-btn-icon" v-html="entry.icon"></span>
              <span class="quick-btn-text">{{ entry.name }}</span>
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'

const currentDate = new Date().toLocaleDateString('zh-CN', { year: 'numeric', month: 'long', day: 'numeric', weekday: 'long' })

const stats = ref([
  {
    title: '注册模型', value: '24', trend: 12.5, link: '/mlops',
    iconColor: '#508cff', iconBg: '#508cff12',
    iconSvg: '<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><circle cx="12" cy="12" r="3"/><path d="M19.4 15a1.65 1.65 0 00.33 1.82l.06.06a2 2 0 010 2.83 2 2 0 01-2.83 0l-.06-.06a1.65 1.65 0 00-1.82-.33 1.65 1.65 0 00-1 1.51V21a2 2 0 01-4 0v-.09A1.65 1.65 0 009 19.4a1.65 1.65 0 00-1.82.33l-.06.06a2 2 0 01-2.83-2.83l.06-.06A1.65 1.65 0 004.68 15a1.65 1.65 0 00-1.51-1H3a2 2 0 010-4h.09A1.65 1.65 0 004.6 9a1.65 1.65 0 00-.33-1.82l-.06-.06a2 2 0 012.83-2.83l.06.06A1.65 1.65 0 009 4.68a1.65 1.65 0 001-1.51V3a2 2 0 014 0v.09a1.65 1.65 0 001 1.51 1.65 1.65 0 001.82-.33l.06-.06a2 2 0 012.83 2.83l-.06.06A1.65 1.65 0 0019.4 9a1.65 1.65 0 001.51 1H21a2 2 0 010 4h-.09a1.65 1.65 0 00-1.51 1z"/></svg>',
  },
  {
    title: '知识库文档', value: '1,256', trend: 8.3, link: '/nlp',
    iconColor: '#22d3ee', iconBg: '#22d3ee12',
    iconSvg: '<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M14.5 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V7.5L14.5 2z"/><polyline points="14 2 14 8 20 8"/><line x1="16" y1="13" x2="8" y2="13"/><line x1="16" y1="17" x2="8" y2="17"/></svg>',
  },
  {
    title: '日均推荐', value: '85.2万', trend: 23.1, link: '/recommend',
    iconColor: '#f59e0b', iconBg: '#f59e0b12',
    iconSvg: '<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><polyline points="23 6 13.5 15.5 8.5 10.5 1 18"/><polyline points="17 6 23 6 23 12"/></svg>',
  },
  {
    title: 'API 调用', value: '320万', trend: -2.1, link: '/mlops',
    iconColor: '#34d399', iconBg: '#34d39912',
    iconSvg: '<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><polyline points="22 12 18 12 15 21 9 3 6 12 2 12"/></svg>',
  },
])

const services = ref([
  { name: 'NLP 知识库', emoji: '🧠', desc: 'RAG 问答 · 文档理解', latency: 12, uptime: 99.9, color: '#22d3ee' },
  { name: '推荐系统', emoji: '🎯', desc: '协同过滤 · 内容推荐', latency: 8, uptime: 99.8, color: '#f59e0b' },
  { name: '计算机视觉', emoji: '👁️', desc: '目标检测 · OCR · 人脸', latency: 45, uptime: 99.7, color: '#34d399' },
  { name: 'MLOps 平台', emoji: '⚙️', desc: '模型训练 · 部署 · 监控', latency: 15, uptime: 99.9, color: '#a78bfa' },
])

const resources = ref([
  { name: 'CPU', percent: 42, color: '#508cff' },
  { name: '内存', percent: 67, color: '#22d3ee' },
  { name: 'GPU', percent: 35, color: '#f59e0b' },
  { name: '磁盘', percent: 58, color: '#34d399' },
])

const quickEntries = ref([
  { name: 'NLP 知识库', link: '/nlp', color: '#22d3ee',
    icon: '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M12 2L2 7l10 5 10-5-10-5z"/><path d="M2 17l10 5 10-5"/><path d="M2 12l10 5 10-5"/></svg>' },
  { name: '推荐系统', link: '/recommend', color: '#f59e0b',
    icon: '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M12 20h9"/><path d="M16.5 3.5a2.121 2.121 0 013 3L7 19l-4 1 1-4L16.5 3.5z"/></svg>' },
  { name: '计算机视觉', link: '/cv', color: '#34d399',
    icon: '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><rect x="3" y="3" width="18" height="18" rx="2"/><circle cx="8.5" cy="8.5" r="1.5"/><path d="M21 15l-5-5L5 21"/></svg>' },
  { name: 'MLOps 平台', link: '/mlops', color: '#a78bfa',
    icon: '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><circle cx="12" cy="12" r="3"/><path d="M19.4 15a1.65 1.65 0 00.33 1.82l.06.06a2 2 0 010 2.83 2 2 0 01-2.83 0l-.06-.06a1.65 1.65 0 00-1.82-.33 1.65 1.65 0 00-1 1.51V21a2 2 0 01-4 0v-.09A1.65 1.65 0 009 19.4a1.65 1.65 0 00-1.82.33l-.06.06a2 2 0 01-2.83-2.83l.06-.06A1.65 1.65 0 004.68 15a1.65 1.65 0 00-1.51-1H3a2 2 0 010-4h.09A1.65 1.65 0 004.6 9a1.65 1.65 0 00-.33-1.82l-.06-.06a2 2 0 012.83-2.83l.06.06A1.65 1.65 0 009 4.68a1.65 1.65 0 001-1.51V3a2 2 0 014 0v.09a1.65 1.65 0 001 1.51 1.65 1.65 0 001.82-.33l.06-.06a2 2 0 012.83 2.83l-.06.06A1.65 1.65 0 0019.4 9a1.65 1.65 0 001.51 1H21a2 2 0 010 4h-.09a1.65 1.65 0 00-1.51 1z"/></svg>' },
])
</script>

<style scoped>
.home-page {
  max-width: 1320px;
  margin: 0 auto;
  animation: fadeSlideIn 0.5s ease;
}

@keyframes fadeSlideIn {
  from { opacity: 0; transform: translateY(12px); }
  to { opacity: 1; transform: translateY(0); }
}

/* ── Headline ── */
.page-headline {
  display: flex;
  justify-content: space-between;
  align-items: flex-end;
  margin-bottom: 28px;
}

.headline-title {
  font-size: 24px;
  font-weight: 600;
  color: var(--text-primary);
  letter-spacing: -0.3px;
}

.headline-desc {
  font-size: 13px;
  color: var(--text-muted);
  margin-top: 4px;
}

.headline-badge {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 4px 14px;
  border-radius: 20px;
  background: rgba(52, 211, 153, 0.06);
  border: 1px solid rgba(52, 211, 153, 0.15);
  font-size: 12px;
  color: var(--accent-emerald);
  font-weight: 500;
}

.badge-dot {
  width: 6px; height: 6px;
  border-radius: 50%;
  background: var(--accent-emerald);
  animation: pulse-dot 2s ease-in-out infinite;
}

@keyframes pulse-dot {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.3; }
}

/* ── Stats Grid ── */
.stats-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
  margin-bottom: 24px;
}

.stat-card {
  background: var(--bg-card);
  border: 1px solid var(--border-subtle);
  border-radius: 14px;
  padding: 20px;
  display: flex;
  align-items: flex-start;
  gap: 16px;
  cursor: pointer;
  transition: all 0.3s ease;
  animation: cardIn 0.5s ease backwards;
  animation-delay: calc(var(--idx) * 0.08s);
}

@keyframes cardIn {
  from { opacity: 0; transform: translateY(12px); }
  to { opacity: 1; transform: translateY(0); }
}

.stat-card:hover {
  border-color: var(--border-glow);
  transform: translateY(-2px);
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3), 0 0 0 1px rgba(80, 140, 255, 0.08);
}

.stat-icon {
  width: 44px;
  height: 44px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.stat-icon :deep(svg) {
  width: 22px;
  height: 22px;
}

.stat-body {
  flex: 1;
  min-width: 0;
}

.stat-label {
  font-size: 13px;
  color: var(--text-secondary);
  font-weight: 500;
  margin-bottom: 4px;
}

.stat-value {
  font-size: 26px;
  font-weight: 700;
  color: var(--text-primary);
  letter-spacing: -0.5px;
  font-family: 'JetBrains Mono', monospace;
  line-height: 1.2;
}

.stat-trend {
  display: flex;
  align-items: center;
  gap: 2px;
  font-size: 12px;
  margin-top: 6px;
  font-weight: 500;
}

.stat-trend.up { color: var(--accent-emerald); }
.stat-trend.down { color: var(--accent-rose); }

.stat-trend svg {
  width: 12px;
  height: 12px;
}

.stat-trend.down svg {
  transform: rotate(180deg);
}

/* ── Main Grid ── */
.home-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
}

.panel {
  background: var(--bg-card);
  border: 1px solid var(--border-subtle);
  border-radius: 14px;
  padding: 20px;
}

.panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 18px;
}

.panel-title {
  font-size: 15px;
  font-weight: 600;
  color: var(--text-primary);
  display: flex;
  align-items: center;
  gap: 8px;
}

.panel-title svg {
  color: var(--accent-blue);
  opacity: 0.8;
}

.panel-action {
  font-size: 12px;
  color: var(--text-muted);
  cursor: pointer;
  transition: color 0.2s;
}

.panel-action:hover {
  color: var(--accent-blue);
}

/* ── Service Cards ── */
.service-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.service-card {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 14px 16px;
  border-radius: 10px;
  background: rgba(255, 255, 255, 0.02);
  border: 1px solid transparent;
  transition: all 0.25s ease;
  cursor: pointer;
}

.service-card:hover {
  background: rgba(255, 255, 255, 0.04);
  border-color: var(--border-glow);
}

.service-left {
  display: flex;
  align-items: center;
  gap: 12px;
}

.service-icon {
  width: 38px;
  height: 38px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.service-emoji {
  font-size: 16px;
  line-height: 1;
}

.service-name {
  font-size: 14px;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 2px;
}

.service-desc {
  font-size: 12px;
  color: var(--text-muted);
}

.service-right {
  display: flex;
  align-items: center;
  gap: 16px;
}

.service-metrics {
  display: flex;
  align-items: center;
  gap: 12px;
}

.metric { text-align: right; }

.metric-label {
  display: block;
  font-size: 10px;
  color: var(--text-muted);
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.metric-value {
  font-size: 13px;
  font-weight: 600;
  color: var(--text-secondary);
  font-family: 'JetBrains Mono', monospace;
}

.sep {
  width: 1px;
  height: 24px;
  background: var(--border-subtle);
}

.service-pulse {
  position: relative;
  width: 12px;
  height: 12px;
}

.pulse-ring {
  position: absolute;
  inset: 0;
  border-radius: 50%;
  border: 2px solid var(--accent);
  animation: pulse-ring 2s ease-out infinite;
}

.pulse-dot {
  position: absolute;
  inset: 2px;
  border-radius: 50%;
  background: var(--accent);
}

@keyframes pulse-ring {
  0% { transform: scale(1); opacity: 0.6; }
  100% { transform: scale(2.5); opacity: 0; }
}

/* ── Resource Bars ── */
.resource-list {
  display: flex;
  flex-direction: column;
  gap: 18px;
}

.resource-head {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.resource-label {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 13px;
  color: var(--text-secondary);
  font-weight: 500;
}

.resource-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
}

.resource-pct {
  font-size: 14px;
  font-weight: 600;
  color: var(--text-primary);
  font-family: 'JetBrains Mono', monospace;
}

.resource-bar {
  height: 6px;
  border-radius: 3px;
  background: rgba(255, 255, 255, 0.04);
  overflow: hidden;
}

.resource-bar-fill {
  height: 100%;
  border-radius: 3px;
  transition: width 1s ease;
}

.panel-divider {
  height: 1px;
  background: var(--border-subtle);
  margin: 20px 0;
}

/* ── Quick Entries ── */
.quick-label {
  font-size: 13px;
  color: var(--text-secondary);
  font-weight: 500;
  margin-bottom: 12px;
}

.quick-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 8px;
}

.quick-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 14px;
  border-radius: 10px;
  background: rgba(255, 255, 255, 0.02);
  border: 1px solid var(--border-subtle);
  color: var(--text-secondary);
  font-size: 13px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.25s ease;
  font-family: 'Outfit', sans-serif;
}

.quick-btn:hover {
  background: rgba(255, 255, 255, 0.04);
  border-color: var(--accent);
  color: var(--accent);
  box-shadow: 0 0 20px color-mix(in srgb, var(--accent) 8%, transparent);
}

.quick-btn-icon {
  width: 18px;
  height: 18px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.quick-btn-icon :deep(svg) {
  width: 16px;
  height: 16px;
}

/* ── Responsive ── */
@media (max-width: 1100px) {
  .stats-grid { grid-template-columns: repeat(2, 1fr); }
  .home-grid { grid-template-columns: 1fr; }
}

@media (max-width: 600px) {
  .stats-grid { grid-template-columns: 1fr; }
  .quick-grid { grid-template-columns: 1fr; }
}
</style>
