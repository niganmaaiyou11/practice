<template>
  <div class="detail-shell">
    <router-link to="/weekly" class="back-link">{{ loc.t.weekly?.backToWeekly || '← 返回 AI 周报' }}</router-link>

    <article v-if="item" class="article-card anim-fade-up">
      <header class="article-header">
        <p class="eyebrow">{{ categoryLabel(item.category) }} · {{ formatDate(item.published_at) }} · {{ item.reading_time }}</p>
        <h1>{{ item.title }}</h1>
        <p class="dek">{{ item.summary }}</p>
        <a v-if="item.source_url !== '#'" :href="item.source_url" target="_blank" rel="noopener noreferrer" class="source-link">
          {{ loc.t.weekly?.source || '来源：' }}{{ item.source_name }}
        </a>
      </header>

      <section class="takeaway-box">
        <p>{{ loc.t.weekly?.takeaways || '要点' }}</p>
        <ul>
          <li v-for="takeaway in item.takeaways" :key="takeaway">{{ takeaway }}</li>
        </ul>
      </section>

      <section class="article-body">
        <p v-for="paragraph in item.body" :key="paragraph">{{ paragraph }}</p>
      </section>
    </article>

    <section v-else class="article-card empty-state">
      <h1>{{ loc.t.weekly?.notFound || '未找到这条周报' }}</h1>
      <p>{{ loc.t.weekly?.notFoundDesc || '这条内容可能已移动或被移除。' }}</p>
      <router-link to="/weekly">{{ loc.t.weekly?.backLink || '回到 AI 周报' }}</router-link>
    </section>
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { useRoute } from 'vue-router'
import { fetchWeeklyItem } from '../api/weekly'
import { findWeeklyItem } from '../data/weekly'
import type { WeeklyItem } from '../types'
import { useLocaleStore } from '../stores/locale'

const loc = useLocaleStore()

const route = useRoute()
const item = ref<WeeklyItem | null>(null)

onMounted(async () => {
  const slug = String(route.params.slug || '')
  try {
    item.value = await fetchWeeklyItem(slug)
  } catch {
    const fallback = findWeeklyItem(slug)
    if (fallback) {
      item.value = {
        ...fallback,
        reading_time: fallback.readingTime,
        published_at: fallback.publishedAt,
        source_name: 'AI Weekly',
        source_url: '#',
      }
    }
  }
})

function categoryLabel(category: string) {
  const w = loc.t.weekly
  const labels: Record<string, string> = {
    model: w?.catModel || '模型动态',
    industry: w?.catIndustry || '行业新闻',
    openSource: w?.catOpenSource || '开源项目',
    tool: w?.catTool || 'AI 工具',
    china: w?.catChina || '国内 AI',
  }
  return labels[category] || category
}

function formatDate(value: string) {
  return value.slice(0, 10)
}
</script>

<style scoped>
.detail-shell {
  max-width: 960px;
  margin: 0 auto;
  background: #f5f4ed;
  color: #141413;
  border-radius: 28px;
  padding: 40px;
}

.back-link {
  display: inline-flex;
  margin-bottom: 24px;
  color: #c96442;
  text-decoration: none;
  font-size: 15px;
}

.article-card {
  background: #faf9f5;
  border: 1px solid #f0eee6;
  border-radius: 24px;
  padding: clamp(28px, 6vw, 64px);
}

.article-header {
  border-bottom: 1px solid #f0eee6;
  padding-bottom: 32px;
  margin-bottom: 32px;
}

.eyebrow {
  color: #c96442;
  font-size: 10px;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  margin-bottom: 18px;
}

.article-header h1,
.empty-state h1 {
  font-family: Georgia, 'Times New Roman', serif;
  font-size: clamp(38px, 7vw, 56px);
  font-weight: 500;
  line-height: 1.16;
  color: #141413;
  margin-bottom: 22px;
}

.dek {
  max-width: 760px;
  color: #5e5d59;
  font-family: Georgia, 'Times New Roman', serif;
  font-size: 18px;
  line-height: 1.6;
}

.source-link {
  display: inline-flex;
  margin-top: 18px;
  color: #c96442;
  text-decoration: none;
  font-size: 14px;
}

.takeaway-box {
  border-top: 3px solid #c96442;
  background: #f5f4ed;
  border-radius: 0 0 18px 18px;
  padding: 22px 24px;
  margin-bottom: 40px;
}

.takeaway-box p {
  color: #141413;
  font-weight: 500;
  margin-bottom: 12px;
}

.takeaway-box ul {
  display: grid;
  gap: 10px;
  margin: 0;
  padding-left: 20px;
  color: #5e5d59;
  line-height: 1.6;
}

.article-body {
  display: grid;
  gap: 24px;
}

.article-body p,
.empty-state p {
  color: #141413;
  font-size: 16px;
  line-height: 1.72;
}

.empty-state a {
  display: inline-flex;
  margin-top: 20px;
  color: #c96442;
  text-decoration: none;
}

@media (max-width: 640px) {
  .detail-shell {
    padding: 24px;
  }
}
</style>
