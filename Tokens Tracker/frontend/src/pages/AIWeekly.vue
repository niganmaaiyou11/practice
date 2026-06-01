<template>
  <div class="weekly-shell">
    <aside class="weekly-index anim-fade-up">
      <p class="index-label">{{ loc.t.weekly?.navLabel || 'AI Weekly' }}</p>
      <a
        v-for="category in categories"
        :key="category.key"
        :href="`#${category.key}`"
        class="index-link"
      >
        {{ category.title }}
      </a>
      <div class="index-divider"></div>
      <button class="index-link index-action" @click="onRefresh" :disabled="refreshing">
        {{ refreshing ? (loc.t.weekly?.refreshing || '刷新中...') : (loc.t.weekly?.refresh || '手动刷新') }}
      </button>
    </aside>

    <main class="weekly-page">
      <section class="weekly-hero anim-fade-up">
        <div class="hero-top-row">
          <div>
            <p class="eyebrow">{{ loc.t.weekly?.navLabel || 'AI Weekly' }} · {{ issueLabel }}</p>
            <h1>{{ loc.t.weekly?.pageTitle || 'AI 周报' }}</h1>
            <p class="hero-subtitle">{{ loc.t.weekly?.heroSubtitle || '精选每周 AI 模型、工具、开源与国内动态，帮助你更快判断哪些变化值得关注。' }}</p>
          </div>
          <NotificationBell />
        </div>
      </section>

      <!-- Feed Status Card -->
      <section v-if="feedStatus" class="status-card anim-fade-up" style="animation-delay: 40ms">
        <div class="section-head">
          <span>{{ loc.t.weekly?.feedStatus || '数据源状态' }}</span>
          <span class="status-time">{{ loc.t.weekly?.lastRefresh || '最后刷新：' }}{{ formatRefreshTime(feedStatus.last_refresh_at) }}</span>
        </div>
        <div class="source-grid">
          <div
            v-for="src in feedStatus.sources"
            :key="src.name"
            class="source-chip"
            :class="{ ok: src.ok, fail: !src.ok }"
          >
            <span class="source-dot"></span>
            <span class="source-name">{{ src.name }}</span>
            <span v-if="src.ok" class="source-count">{{ src.items_count }}{{ loc.t.weekly?.items || ' 条' }}</span>
            <span v-else class="source-error" :title="src.error">{{ loc.t.weekly?.failed || '失败' }}</span>
          </div>
        </div>
        <p v-if="refreshResult" class="refresh-result">
          {{ loc.t.weekly?.refreshDone || '刷新完成：新增 ' }}{{ refreshResult.new_items }}{{ loc.t.weekly?.refreshItems || ' 条，' }}
          {{ refreshResult.sources_ok }}/{{ refreshResult.sources_ok + refreshResult.sources_failed }}{{ loc.t.weekly?.refreshSourcesOk || ' 个源成功' }}
        </p>
      </section>

      <section class="summary-card anim-fade-up" style="animation-delay: 80ms">
        <div class="section-head">
          <span>{{ loc.t.weekly?.weeklySummary || '本周摘要' }}</span>
          <router-link to="/leaderboard">{{ loc.t.weekly?.viewLeaderboard || '查看模型榜单' }}</router-link>
        </div>
        <ol class="highlight-list">
          <li v-for="item in weeklyHighlights" :key="item">{{ item }}</li>
        </ol>
      </section>

      <section class="category-list">
        <article
          v-for="category in categories"
          :id="category.key"
          :key="category.key"
          class="category-section anim-fade-up"
        >
          <div class="category-head">
            <p>{{ category.kicker }}</p>
            <h2>{{ category.title }}</h2>
            <span>{{ category.description }}</span>
          </div>

          <div class="news-list">
            <router-link
              v-for="item in itemsByCategory(category.key)"
              :key="item.slug"
              :to="`/weekly/${item.slug}`"
              class="news-card"
            >
              <div class="news-meta">
                <span>{{ category.title }}</span>
                <span>{{ item.reading_time }}</span>
                <span class="impact-pill" :class="`impact-${item.impact.toLowerCase()}`">{{ item.impact }}</span>
              </div>
              <h3>{{ item.title }}</h3>
              <p>{{ item.summary }}</p>
              <span class="read-link">{{ loc.t.weekly?.readMore || '阅读全文' }}</span>
            </router-link>
          </div>
        </article>
      </section>
    </main>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { fetchWeekly, triggerWeeklyRefresh, fetchWeeklyStatus } from '../api/weekly'
import type { WeeklyStatusResponse } from '../api/weekly'
import { weeklyHighlights as fallbackHighlights, weeklyItems as fallbackItems } from '../data/weekly'
import type { WeeklyItem } from '../types'
import NotificationBell from '../components/NotificationBell.vue'
import { useLocaleStore } from '../stores/locale'

const loc = useLocaleStore()

const weeklyHighlights = ref<string[]>(fallbackHighlights)
const weeklyItems = ref<WeeklyItem[]>(fallbackItems.map((item) => ({
  slug: item.slug,
  title: item.title,
  summary: item.summary,
  category: item.category,
  impact: item.impact,
  reading_time: item.readingTime,
  published_at: item.publishedAt,
  source_name: 'AI Weekly',
  source_url: '#',
  body: item.body,
  takeaways: item.takeaways,
})))
const issueDate = ref('')
const feedStatus = ref<WeeklyStatusResponse | null>(null)
const refreshing = ref(false)
const refreshResult = ref<{ new_items: number; sources_ok: number; sources_failed: number } | null>(null)

const issueLabel = computed(() => issueDate.value || new Date().toISOString().slice(0, 10))

onMounted(async () => {
  try {
    const data = await fetchWeekly()
    weeklyHighlights.value = data.highlights
    weeklyItems.value = data.items
    issueDate.value = data.issue_date
  } catch {
    issueDate.value = new Date().toISOString().slice(0, 10)
  }

  try {
    feedStatus.value = await fetchWeeklyStatus()
  } catch {
    // silent
  }
})

async function onRefresh() {
  refreshing.value = true
  refreshResult.value = null
  try {
    const result = await triggerWeeklyRefresh()
    refreshResult.value = result
    // Reload data
    const data = await fetchWeekly()
    weeklyHighlights.value = data.highlights
    weeklyItems.value = data.items
    issueDate.value = data.issue_date
    feedStatus.value = await fetchWeeklyStatus()
  } catch {
    // error handled by interceptor
  } finally {
    refreshing.value = false
  }
}

function formatRefreshTime(value: string | null): string {
  const w = loc.t.weekly
  if (!value) return w?.neverRefreshed || '未刷新'
  const date = new Date(value)
  const now = new Date()
  const diffMs = now.getTime() - date.getTime()
  const diffMin = Math.floor(diffMs / 60000)
  if (diffMin < 1) return w?.justNow || '刚刚'
  if (diffMin < 60) return `${diffMin}${w?.minutesAgo || ' 分钟前'}`
  const diffHour = Math.floor(diffMin / 60)
  if (diffHour < 24) return `${diffHour}${w?.hoursAgo || ' 小时前'}`
  return value.slice(0, 16).replace('T', ' ')
}

const categories = computed<Array<{
  key: 'model' | 'industry' | 'openSource' | 'tool' | 'china'
  title: string
  kicker: string
  description: string
}>>(() => {
  const w = loc.t.weekly
  return [
    { key: 'model', title: w?.catModel || '模型动态', kicker: 'Models', description: w?.catModelDesc || '新模型、榜单、价格和上下文窗口变化。' },
    { key: 'industry', title: w?.catIndustry || '行业新闻', kicker: 'Industry', description: w?.catIndustryDesc || '大厂产品、平台能力和商业化趋势。' },
    { key: 'openSource', title: w?.catOpenSource || '开源项目', kicker: 'Open Source', description: w?.catOpenSourceDesc || '值得关注的开源模型、框架和本地部署方向。' },
    { key: 'tool', title: w?.catTool || 'AI 工具', kicker: 'Tools', description: w?.catToolDesc || '开发者工具、评测、可观测性和效率产品。' },
    { key: 'china', title: w?.catChina || '国内 AI', kicker: 'China AI', description: w?.catChinaDesc || '中国模型、产品和价格性能动态。' },
  ]
})

function itemsByCategory(category: string) {
  return weeklyItems.value.filter((item) => item.category === category)
}
</script>

<style scoped>
.weekly-shell {
  display: grid;
  grid-template-columns: 220px minmax(0, 1fr);
  gap: 56px;
  align-items: start;
  background: #f5f4ed;
  color: #141413;
  border-radius: 28px;
  padding: 40px;
}

/* ── Sidebar Index ── */
.weekly-index {
  position: sticky;
  top: calc(var(--header-height) + 32px);
  display: grid;
  gap: 4px;
  padding: 18px;
  border: 1px solid #f0eee6;
  border-radius: 18px;
  background: #faf9f5;
}

.index-label,
.eyebrow,
.category-head p,
.news-meta {
  font-size: 10px;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}

.index-label {
  color: #c96442;
  margin-bottom: 8px;
}

.index-link {
  color: #5e5d59;
  text-decoration: none;
  padding: 9px 8px;
  border-radius: 10px;
  font-size: 15px;
  transition: background 160ms ease, color 160ms ease;
}

.index-link:hover {
  color: #141413;
  background: #f0eee6;
}

.index-divider {
  height: 1px;
  background: #f0eee6;
  margin: 8px 0;
}

.index-action {
  border: none;
  background: transparent;
  cursor: pointer;
  font-family: inherit;
  text-align: left;
  color: #c96442;
  font-size: 14px;
  font-weight: 500;
}

.index-action:hover {
  background: #f0eee6;
  color: #c96442;
}

.index-action:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* ── Main Content ── */
.weekly-page {
  display: flex;
  flex-direction: column;
  gap: 80px;
}

.weekly-hero,
.summary-card,
.category-section,
.status-card {
  background: #faf9f5;
  border: 1px solid #f0eee6;
  border-radius: 24px;
}

.weekly-hero {
  padding: 56px;
}

.hero-top-row {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 24px;
}

.eyebrow {
  color: #c96442;
  margin-bottom: 18px;
}

.weekly-hero h1,
.category-head h2,
.news-card h3 {
  font-family: Georgia, 'Times New Roman', serif;
  font-weight: 500;
  color: #141413;
}

.weekly-hero h1 {
  font-size: clamp(44px, 7vw, 64px);
  line-height: 1.1;
  margin-bottom: 20px;
}

.hero-subtitle {
  max-width: 720px;
  color: #5e5d59;
  font-size: 17px;
  line-height: 1.6;
}

/* ── Status Card ── */
.status-card {
  padding: 28px 32px;
}

.section-head {
  display: flex;
  justify-content: space-between;
  gap: 24px;
  margin-bottom: 18px;
  color: #141413;
  font-weight: 500;
}

.section-head a {
  color: #c96442;
  text-decoration: none;
}

.status-time {
  color: #5e5d59;
  font-size: 13px;
  font-weight: 400;
}

.source-grid {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-bottom: 12px;
}

.source-chip {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 6px 12px;
  border-radius: 999px;
  background: #f0eee6;
  font-size: 12px;
  color: #5e5d59;
}

.source-chip.ok .source-dot {
  background: #4f7653;
}

.source-chip.fail .source-dot {
  background: #9f3f26;
}

.source-dot {
  width: 6px;
  height: 6px;
  border-radius: 999px;
}

.source-name {
  font-weight: 500;
  color: #141413;
}

.source-count {
  color: #5e5d59;
}

.source-error {
  color: #9f3f26;
  cursor: help;
}

.refresh-result {
  margin-top: 8px;
  font-size: 13px;
  color: #4f7653;
}

/* ── Summary Card ── */
.summary-card {
  padding: 28px 32px;
}

.highlight-list {
  display: grid;
  gap: 14px;
  margin: 0;
  padding-left: 22px;
  color: #5e5d59;
  line-height: 1.6;
}

/* ── Category Sections ── */
.category-list {
  display: grid;
  gap: 96px;
}

.category-section {
  padding: 40px;
  scroll-margin-top: calc(var(--header-height) + 32px);
}

.category-head {
  max-width: 720px;
  margin-bottom: 28px;
}

.category-head p {
  color: #c96442;
  margin-bottom: 10px;
}

.category-head h2 {
  font-size: 36px;
  line-height: 1.3;
  margin-bottom: 10px;
}

.category-head span {
  color: #5e5d59;
  line-height: 1.6;
}

.news-list {
  display: grid;
  border-top: 1px solid #f0eee6;
}

.news-card {
  display: block;
  padding: 28px 0;
  color: inherit;
  text-decoration: none;
  border-bottom: 1px solid #f0eee6;
  transition: background 160ms ease;
}

.news-card:hover {
  background: rgba(201, 100, 66, 0.035);
}

.news-meta {
  display: flex;
  align-items: center;
  gap: 12px;
  flex-wrap: wrap;
  color: #5e5d59;
  margin-bottom: 12px;
}

.news-card h3 {
  max-width: 820px;
  font-size: 30px;
  line-height: 1.18;
  margin-bottom: 12px;
}

.news-card p {
  max-width: 780px;
  color: #5e5d59;
  line-height: 1.6;
  margin-bottom: 16px;
}

.read-link {
  color: #c96442;
  font-size: 14px;
  font-weight: 500;
}

.impact-pill {
  display: inline-flex;
  padding: 3px 8px;
  border-radius: 999px;
  background: #f0eee6;
  color: #5e5d59;
}

.impact-high {
  color: #9f3f26;
}

.impact-medium {
  color: #9b6a1b;
}

.impact-watch {
  color: #4f7653;
}

@media (max-width: 980px) {
  .weekly-shell {
    grid-template-columns: 1fr;
    padding: 24px;
  }

  .weekly-index {
    position: static;
  }

  .hero-top-row {
    flex-direction: column;
  }
}

@media (max-width: 640px) {
  .weekly-hero,
  .summary-card,
  .category-section,
  .status-card {
    padding: 24px;
  }

  .news-card h3 {
    font-size: 25px;
  }
}
</style>
