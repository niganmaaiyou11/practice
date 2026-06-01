<template>
  <div class="leaderboard-page">
    <!-- Page Header -->
    <section class="page-header anim-fade-up">
      <h1 class="page-title">{{ t.leaderboard?.fullTitle || 'AI Model Leaderboard' }}</h1>
      <div class="header-meta">
        <div class="sync-stats">
          <span v-if="store.summary?.last_fetched_at" class="last-updated">
            {{ t.leaderboard?.lastUpdated || 'Last updated' }}:
            {{ formatDate(store.summary.last_fetched_at) }}
          </span>
          <span class="last-updated">
            Registry: {{ modelsStore.providerCount }} providers / {{ modelsStore.modelCount }} models
          </span>
          <span v-if="modelsStore.registry.updated_at" class="last-updated">
            {{ formatDate(modelsStore.registry.updated_at) }}
          </span>
        </div>
        <RouterLink class="header-link" to="/weekly">模型动态</RouterLink>
        <RouterLink class="header-link" to="/leaderboard/compare">模型对比</RouterLink>
        <RouterLink class="header-link" to="/pricing">模型价格</RouterLink>
        <button
          class="sync-btn"
          :disabled="store.syncing"
          @click="onSync"
        >
          {{ store.syncing ? (t.leaderboard?.syncing || 'Syncing...') : (t.leaderboard?.sync || 'Sync Data') }}
        </button>
      </div>
    </section>

    <!-- Category Tabs -->
    <section class="tabs-section">
      <div class="tab-bar">
        <button
          v-for="tab in CATEGORY_TABS"
          :key="tab.key"
          class="tab-btn"
          :class="{ 'is-active': activeTab === tab.key }"
          @click="onTabChange(tab.key)"
        >
          {{ tab.label }}
        </button>
      </div>
    </section>

    <!-- Filter Bar -->
    <section class="filter-section">
      <el-input
        v-model="searchText"
        :placeholder="t.leaderboard?.search || 'Search models...'"
        class="search-input"
        clearable
        @input="onSearchDebounced"
      />
      <el-select
        v-model="store.filters.provider"
        :placeholder="t.filter?.provider || 'Provider'"
        class="provider-select"
        clearable
        @change="onFilterChange"
      >
        <el-option
          v-for="p in store.providers"
          :key="p"
          :label="p"
          :value="p"
        />
      </el-select>
      <div class="china-toggle">
        <el-switch
          v-model="chinaOnly"
          size="small"
          @change="onChinaToggle"
        />
        <span class="china-toggle__label" :class="{ 'is-active': chinaOnly }">
          {{ t.leaderboard?.chinaOnly || 'China AI Only' }}
        </span>
      </div>
      <button
        class="sort-dir-btn"
        @click="toggleSortDir"
        :title="store.filters.sort_dir === 'desc' ? 'Descending' : 'Ascending'"
      >
        {{ store.filters.sort_dir === 'desc' ? '↓' : '↑' }}
      </button>
    </section>

    <!-- Table -->
    <section class="table-section">
      <div v-if="store.entries.length === 0 && !store.loading" class="empty-state">
        <p class="empty-msg">{{ t.leaderboard?.noData || 'No leaderboard data yet' }}</p>
        <p class="empty-hint">{{ t.leaderboard?.noDataHint || '' }}</p>
      </div>
      <el-table
        v-else
        :data="store.entries"
        v-loading="store.loading"
        stripe
        class="lb-table"
        row-key="id"
        @row-click="onRowClick"
      >
        <el-table-column
          :label="t.leaderboard?.rank || 'Rank'"
          width="70"
          align="center"
        >
          <template #default="{ $index }">
            <span class="rank-cell" :class="rankClass($index)">{{ paginatedRank($index) }}</span>
          </template>
        </el-table-column>
        <el-table-column
          :label="t.leaderboard?.model || 'Model'"
          prop="model_name"
          min-width="180"
          sortable
          sort-method="custom"
        >
          <template #default="{ row }">
            <div class="model-cell">
              <ProviderIcon :provider="row.provider" :size="32" />
              <span class="model-name">{{ row.model_name }}</span>
            </div>
          </template>
        </el-table-column>
        <el-table-column
          :label="t.leaderboard?.provider || 'Provider'"
          prop="provider"
          width="130"
        >
          <template #default="{ row }">
            <span class="provider-tag" :style="{ color: providerColor(row.provider) }">
              {{ row.provider }}
            </span>
          </template>
        </el-table-column>
        <el-table-column
          width="130"
        >
          <template #header>
            <el-tooltip v-if="activeTab === 'overall_score'" placement="top" :show-after="100">
              <template #content>
                <div class="score-tip">
                  <div class="score-tip__title">{{ t.leaderboard?.scoreFormulaTitle || 'LLM STATS' }}</div>
                  <div class="score-tip__note">
                    {{ t.leaderboard?.scoreFormulaNote || 'Overall score directly from llm-stats.com — a composite rating that balances coding, reasoning, writing, math, and speed.' }}
                  </div>
                </div>
              </template>
              <span class="th-with-info">
                {{ activeScoreLabel }}
                <span class="info-mark" aria-hidden="true">ⓘ</span>
              </span>
            </el-tooltip>
            <span v-else class="th-with-info">{{ activeScoreLabel }}</span>
          </template>
          <template #default="{ row }">
            <template v-if="isSpeedTab">
              <span v-if="row.tokens_per_second != null" class="metric-cell">
                {{ formatSpeed(row.tokens_per_second) }}
              </span>
              <span v-else class="na-cell">—</span>
            </template>
            <template v-else>
              <div class="score-cell" v-if="getScoreValue(row) != null">
                <span class="score-val">{{ fmtScore(row) }}</span>
                <div class="score-bar"><div class="score-fill" :style="{ width: barWidth(getScoreValue(row)) }" /></div>
              </div>
              <span v-else class="na-cell">—</span>
            </template>
          </template>
        </el-table-column>
        <el-table-column
          v-if="showMetaColumns"
          :label="t.leaderboard?.speed || 'Speed'"
          width="110"
          align="right"
        >
          <template #default="{ row }">
            <span v-if="row.tokens_per_second != null" class="metric-cell">
              {{ formatSpeed(row.tokens_per_second) }}
            </span>
            <span v-else class="na-cell">—</span>
          </template>
        </el-table-column>
        <el-table-column
          v-if="showMetaColumns"
          :label="t.leaderboard?.contextWindow || 'Context'"
          width="100"
          align="right"
        >
          <template #default="{ row }">
            <span v-if="row.context_window != null" class="metric-cell">
              {{ fmtContext(row.context_window) }}
            </span>
            <span v-else class="na-cell">—</span>
          </template>
        </el-table-column>
        <el-table-column type="expand">
          <template #default="{ row }">
            <div class="expand-detail">
              <h4 class="detail-title">{{ t.leaderboard?.scoreBreakdown || 'Score Breakdown' }}</h4>
              <div class="breakdown-grid">
                <div
                  v-for="g in groupBreakdown(row)"
                  :key="g.key"
                  class="breakdown-card"
                  :class="{ 'is-missing': g.value == null }"
                >
                  <div class="breakdown-card__head">
                    <span class="breakdown-card__group">
                      {{ g.label }}
                      <span class="breakdown-card__weight">{{ g.weight }}</span>
                    </span>
                    <span class="breakdown-card__val">
                      {{ g.value != null ? fmtNum(g.value) : '—' }}
                    </span>
                  </div>
                  <div class="breakdown-card__benchmarks">{{ g.benchmarks }}</div>
                  <div class="breakdown-card__inputs" v-if="g.inputs.length">
                    <span
                      v-for="b in g.inputs"
                      :key="b.label"
                      class="breakdown-bench"
                      :class="{ 'is-missing': b.value == null }"
                    >
                      <span class="breakdown-bench__name">{{ b.label }}</span>
                      <span class="breakdown-bench__val">{{ b.value != null ? fmtNum(b.value) : '—' }}</span>
                    </span>
                  </div>
                </div>
              </div>
              <div class="breakdown-formula">
                {{ t.leaderboard?.scoreFormulaNote || 'Overall score from llm-stats.com LLM STATS.' }}
              </div>

              <h4 class="detail-title detail-title--secondary">{{ t.leaderboard?.details || 'Benchmark Details' }}</h4>
              <div class="bench-grid">
                <div class="bench-item" v-if="row.max_output_tokens != null">
                  <span class="bench-label">Max Output</span>
                  <span class="bench-val">{{ fmtContext(row.max_output_tokens) }}</span>
                </div>
                <div class="bench-item" v-if="row.knowledge_cutoff">
                  <span class="bench-label">Knowledge Cutoff</span>
                  <span class="bench-val">{{ row.knowledge_cutoff }}</span>
                </div>
              </div>
            </div>
          </template>
        </el-table-column>
      </el-table>
    </section>

    <!-- Pagination -->
    <section v-if="store.total > 0" class="pagination-section">
      <el-pagination
        v-model:current-page="currentPage"
        v-model:page-size="store.pagination.limit"
        :total="store.total"
        :page-sizes="[20, 50, 100]"
        layout="total, sizes, prev, pager, next"
        @current-change="onPageChange"
        @size-change="onPageChange"
      />
    </section>

    <!-- Scatter Chart (only on Overall tab) -->
    <section v-if="store.entries.length > 0 && activeTab === 'overall_score'" class="chart-section">
      <div class="chart-card liquid-glass-card">
        <div class="liquid-orb liquid-orb--blue"></div>
        <div class="liquid-orb liquid-orb--mint"></div>
        <div class="liquid-orb liquid-orb--gold"></div>
        <div class="chart-card__chrome">
          <div>
            <div class="chart-eyebrow">Overall Arena</div>
            <h3 class="chart-title">Quality vs Speed</h3>
            <p class="chart-subtitle">{{ t.leaderboard?.chartSubtitle || 'Bubble size = context window' }}</p>
          </div>
          <div class="chart-pill">Liquid Glass</div>
        </div>
        <div class="chart-stage">
          <v-chart :option="scatterOption" :autoresize="true" class="chart-instance" />
        </div>
      </div>
    </section>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { useLeaderboardStore } from '../stores/leaderboard'
import { useLocaleStore } from '../stores/locale'
import { useModelsStore } from '../stores/models'

import { ElMessage } from 'element-plus'
import ProviderIcon from '../components/ProviderIcon.vue'

const route = useRoute()
const store = useLeaderboardStore()
const t = useLocaleStore().t
const modelsStore = useModelsStore()

const searchText = ref(typeof route.query.search === 'string' ? route.query.search : '')
let searchTimer: ReturnType<typeof setTimeout> | null = null
const currentPage = ref(1)
const chinaOnly = ref(false)
if (searchText.value) {
  store.filters.search = searchText.value
}

// 6 tabs: 5 categories + Speed
const CATEGORY_TABS = computed(() => [
  { key: 'overall_score', label: t.leaderboard?.tabOverall || 'Overall', scoreField: 'overall_score', showMeta: true },
  { key: 'score_coding', label: t.leaderboard?.tabCoding || 'Coding', scoreField: 'score_coding', showMeta: false },
  { key: 'category_math_score', label: t.leaderboard?.tabMath || 'Math', scoreField: 'category_math_score', fallbackSort: 'score_math', fallbackScore: 'score_math', showMeta: false },
  { key: 'score_reasoning', label: t.leaderboard?.tabReasoning || 'Reasoning', scoreField: 'score_reasoning', showMeta: false },
  { key: 'category_writing_score', label: t.leaderboard?.tabWriting || 'Writing', scoreField: 'category_writing_score', showMeta: false },
  { key: 'tokens_per_second', label: t.leaderboard?.speed || 'Speed', scoreField: 'tokens_per_second', showMeta: false, isSpeed: true },
])
const activeTab = ref('overall_score')

// Active tab metadata
const activeTabDef = computed(() => CATEGORY_TABS.value.find(t => t.key === activeTab.value))
const activeScoreField = computed(() => activeTabDef.value?.scoreField || 'overall_score')
const activeScoreLabel = computed(() => activeTabDef.value?.label || 'Score')
const showMetaColumns = computed(() => activeTabDef.value?.showMeta ?? false)
const isSpeedTab = computed(() => activeTabDef.value?.isSpeed ?? false)

function onTabChange(tabKey: string) {
  activeTab.value = tabKey
  const tab = CATEGORY_TABS.value.find(t => t.key === tabKey)
  store.filters.sort_by = tab?.fallbackSort || tabKey
  onFilterChange()
}

function onChinaToggle(val: boolean) {
  store.filters.china_only = val
  currentPage.value = 1
  store.pagination.skip = 0
  store.fetchEntries()
}

function paginatedRank(index: number): number {
  return store.pagination.skip + index + 1
}

function rankClass(index: number): string {
  const r = paginatedRank(index)
  if (r === 1) return 'rank-gold'
  if (r === 2) return 'rank-silver'
  if (r === 3) return 'rank-bronze'
  return ''
}

function providerColor(provider: string): string {
  return modelsStore.providerColors[provider] || '#999'
}

function getScoreValue(row: any): number | null {
  const field = activeScoreField.value
  // Handle fallback for Math tab: try category_math_score first, then score_math
  const tab = activeTabDef.value
  if (tab?.fallbackScore && row[field] == null) {
    return row[tab.fallbackScore] ?? null
  }
  return row[field] ?? null
}

function fmtScore(row: any): string {
  const val = getScoreValue(row)
  if (val == null) return '—'
  if (isSpeedTab.value) return formatSpeed(val)
  return val.toFixed(1)
}

function barWidth(val: number | null): string {
  if (val == null) return '0%'
  const pctVal = val > 1 ? Math.min(100, val) : Math.min(100, val * 100)
  return pctVal.toFixed(0) + '%'
}

// Used in expandable row breakdown cards
function fmtNum(val: number): string {
  return val > 1 ? val.toFixed(1) : (val * 100).toFixed(1)
}

// LLM STATS overall score — directly from llm-stats.com
const METHODOLOGY_AXES = computed(() => [
  { key: 'coding',         weight: 0.30, benchmarks: 'SWE-Bench Verified, LiveCodeBench, HumanEval, Terminal-Bench 2.0', label: t.leaderboard?.tabCoding || 'Coding' },
  { key: 'reasoning',      weight: 0.35, benchmarks: 'GPQA Diamond, MMLU-Pro, SimpleQA, HLE', label: t.leaderboard?.tabReasoning || 'Reasoning' },
  { key: 'speed',          weight: 0.10, benchmarks: 'Output tokens per second (z-score normalized)', label: t.leaderboard?.speed || 'Speed' },
  { key: 'writing',        weight: 0.15, benchmarks: 'Creative Writing Arena, IFEval, LongWriter, HumanEval-Scribe', label: t.leaderboard?.tabWriting || 'Writing' },
  { key: 'math',           weight: 0.10, benchmarks: 'MATH-500, AIME 2025, FrontierMath, AMC 2025', label: t.leaderboard?.tabMath || 'Math' },
])

function axisLabel(key: string): string {
  const map: Record<string, string> = {
    coding: t.leaderboard?.tabCoding || 'Coding',
    math: t.leaderboard?.tabMath || 'Math',
    reasoning: t.leaderboard?.tabReasoning || 'Reasoning',
    writing: t.leaderboard?.tabWriting || 'Writing',
    speed: t.leaderboard?.speed || 'Speed',
    knowledge: t.leaderboard?.groupKnowledge || 'Knowledge',
    tool_use: t.leaderboard?.groupToolUse || 'Tool Use & Agents',
    long_context: t.leaderboard?.groupLongContext || 'Long Context',
    vision: t.leaderboard?.groupVision || 'Vision',
  }
  return map[key] || key
}

function axisBenchmarks(key: string): string {
  const m = METHODOLOGY_AXES.value.find(a => a.key === key)
  return m?.benchmarks || ''
}

function axisWeight(key: string): string {
  const m = METHODOLOGY_AXES.value.find(a => a.key === key)
  return m ? (m.weight * 100).toFixed(0) + '%' : ''
}

function groupBreakdown(row: any) {
  return [
    {
      key: 'coding',
      label: axisLabel('coding'),
      weight: axisWeight('coding'),
      benchmarks: axisBenchmarks('coding'),
      inputs: [
        { label: t.leaderboard?.scoreSWEBench || 'SWE-Bench', value: row.score_swebench },
        { label: t.leaderboard?.scoreHumanEval || 'HumanEval', value: row.score_humaneval },
        { label: t.leaderboard?.scoreCodingArena || 'Coding Arena', value: row.score_coding_arena },
      ],
      value: row.score_coding,
    },
    {
      key: 'reasoning',
      label: axisLabel('reasoning'),
      weight: axisWeight('reasoning'),
      benchmarks: axisBenchmarks('reasoning'),
      inputs: [
        { label: t.leaderboard?.scoreGPQA || 'GPQA Diamond', value: row.score_gpqa },
        { label: t.leaderboard?.scoreMMLUPro || 'MMLU-Pro', value: row.score_mmlu_pro },
      ],
      value: row.score_reasoning,
    },
    {
      key: 'speed',
      label: axisLabel('speed'),
      weight: axisWeight('speed'),
      benchmarks: axisBenchmarks('speed'),
      inputs: [
        { label: 'tokens/s', value: row.tokens_per_second },
      ],
      value: row.tokens_per_second != null ? row.tokens_per_second : null,
    },
    {
      key: 'writing',
      label: axisLabel('writing'),
      weight: axisWeight('writing'),
      benchmarks: axisBenchmarks('writing'),
      inputs: [],
      value: row.category_writing_score,
    },
    {
      key: 'math',
      label: axisLabel('math'),
      weight: axisWeight('math'),
      benchmarks: axisBenchmarks('math'),
      inputs: [
        { label: t.leaderboard?.scoreMATH || 'MATH', value: row.score_math },
      ],
      value: row.category_math_score ?? row.score_math,
    },
  ]
}

function formatSpeed(tps: number): string {
  if (tps >= 1000) return (tps / 1000).toFixed(1) + 'K'
  return tps.toFixed(0)
}

function fmtContext(n: number): string {
  if (n >= 1_000_000) return (n / 1_000_000).toFixed(1) + 'M'
  if (n >= 1_000) return (n / 1_000).toFixed(0) + 'K'
  return n.toLocaleString()
}

function formatDate(iso: string): string {
  const d = new Date(iso)
  const y = d.getFullYear()
  const m = String(d.getMonth() + 1).padStart(2, '0')
  const day = String(d.getDate()).padStart(2, '0')
  const h = String(d.getHours()).padStart(2, '0')
  const min = String(d.getMinutes()).padStart(2, '0')
  return `${y}-${m}-${day} ${h}:${min}`
}

function onSearchDebounced() {
  if (searchTimer) clearTimeout(searchTimer)
  searchTimer = setTimeout(() => {
    store.setFilter('search', searchText.value || undefined)
    currentPage.value = 1
    store.pagination.skip = 0
    store.fetchEntries()
  }, 300)
}

function onFilterChange() {
  currentPage.value = 1
  store.pagination.skip = 0
  store.fetchEntries()
}

function toggleSortDir() {
  store.filters.sort_dir = store.filters.sort_dir === 'desc' ? 'asc' : 'desc'
  onFilterChange()
}

function onPageChange() {
  store.pagination.skip = (currentPage.value - 1) * store.pagination.limit
  store.fetchEntries()
}

function onRowClick(_row: any) {
  // row click toggles expand
}

async function onSync() {
  const result = await store.triggerSync()
  if (result.ok) {
    await modelsStore.fetchRegistryForce()
    const summary = result.models && result.providers
      ? `Synced ${result.models} models from ${result.providers} providers`
      : result.output || 'Synced'
    ElMessage.success(summary)
  } else {
    ElMessage.error(result.output || 'Sync failed')
  }
}

// Scatter chart — enhanced with quadrant lines, Pareto frontier, & better tooltips
const scatterOption = computed(() => {
  const toPct = (v: number) => v > 1 ? Math.round(v) : Math.round(v * 100)
  const raw = store.entries
    .filter(e => e.overall_score != null && e.tokens_per_second != null)
    .map(e => ({
      score: toPct(e.overall_score!),
      speed: Math.min(e.tokens_per_second!, 500),
      ctx: e.context_window || 128000,
      name: e.model_name,
      provider: e.provider,
    }))

  if (raw.length === 0) return {}

  // Compute medians for quadrant dividing lines
  const scores = raw.map(d => d.score).sort((a, b) => a - b)
  const speeds = raw.map(d => d.speed).sort((a, b) => a - b)
  const medianScore = scores[Math.floor(scores.length / 2)]
  const medianSpeed = speeds[Math.floor(speeds.length / 2)]

  // Pareto frontier: top-right envelope (models not dominated by any other)
  const sorted = [...raw].sort((a, b) => b.score - a.score)
  const frontier: typeof raw = []
  let maxSpeed = -1
  for (const pt of sorted) {
    if (pt.speed > maxSpeed) {
      frontier.push(pt)
      maxSpeed = pt.speed
    }
  }
  // Sort frontier by score ascending for the line
  frontier.sort((a, b) => a.score - b.score)

  const data = raw.map(e => ({
    value: [e.score, e.speed, e.ctx, e.name, e.provider],
    itemStyle: {
      color: hexToRgba(providerColor(e.provider), 0.58),
      shadowBlur: 18,
      shadowColor: hexToRgba(providerColor(e.provider), 0.34),
      borderColor: 'rgba(255,255,255,0.82)',
      borderWidth: 1.6,
      borderType: 'solid' as const,
    },
  }))

  return {
    backgroundColor: 'transparent',
    animationDuration: 900,
    animationEasing: 'cubicOut' as const,
    tooltip: {
      backgroundColor: 'rgba(255,255,255,0.72)',
      borderColor: 'rgba(255,255,255,0.86)',
      borderWidth: 1,
      borderRadius: 20,
      padding: [14, 18],
      extraCssText: 'backdrop-filter: blur(22px) saturate(1.55); -webkit-backdrop-filter: blur(22px) saturate(1.55); box-shadow: 0 22px 60px rgba(31, 41, 55, 0.18), inset 0 1px 0 rgba(255,255,255,0.75);',
      textStyle: { color: '#1d1d1f', fontSize: 13, fontFamily: 'var(--font-family, inherit)' },
      formatter: (params: any) => {
        const d = params.data.value || params.data
        return `<div>
          <strong style="font-size:14px;color:#1d1d1f">${d[3]}</strong>
          <div style="margin-top:6px;color:rgba(60,60,67,0.68);font-size:12px">${d[4]}</div>
          <div style="margin-top:10px;display:flex;flex-direction:column;gap:4px;color:#1d1d1f">
            <span style="color:#0071e3">Score: <b>${d[0]}%</b></span>
            <span>Speed: <b>${d[1].toFixed(0)} t/s</b></span>
            <span>Context: <b>${(d[2] / 1000).toFixed(0)}K</b></span>
          </div>
        </div>`
      },
    },
    grid: { left: 65, right: 42, top: 38, bottom: 55 },
    xAxis: {
      name: t.leaderboard?.overallScore || 'Overall Score',
      nameTextStyle: { fontSize: 12, color: 'rgba(60,60,67,0.72)', fontWeight: 600 },
      axisLine: { lineStyle: { color: 'rgba(255,255,255,0.46)' } },
      axisTick: { show: false },
      axisLabel: { color: 'rgba(60,60,67,0.66)', formatter: '{value}%' },
      splitLine: { lineStyle: { color: 'rgba(255,255,255,0.42)' } },
      ...markLineAt(medianScore, 'xAxis', 'median'),
    },
    yAxis: {
      name: 'Speed (t/s)',
      nameTextStyle: { fontSize: 12, color: 'rgba(60,60,67,0.72)', fontWeight: 600 },
      axisLine: { lineStyle: { color: 'rgba(255,255,255,0.46)' } },
      axisTick: { show: false },
      axisLabel: { color: 'rgba(60,60,67,0.66)' },
      splitLine: { lineStyle: { color: 'rgba(255,255,255,0.42)' } },
      ...markLineAt(medianSpeed, 'yAxis', 'median'),
    },
    series: [
      {
        type: 'scatter',
        name: 'Models',
        data,
        symbolSize: (val: number[]) => {
          const ctx = val[2] || 128000
          return Math.max(8, Math.min(44, Math.log2(ctx / 1000) * 4.2))
        },
        emphasis: {
          scale: 1.55,
          focus: 'self' as const,
          itemStyle: {
            shadowBlur: 28,
            borderColor: 'rgba(255,255,255,0.96)',
            borderWidth: 2.4,
          },
          label: {
            show: true,
            formatter: (p: any) => p.data.value?.[3],
            position: 'top',
            color: '#1d1d1f',
            backgroundColor: 'rgba(255,255,255,0.72)',
            borderColor: 'rgba(255,255,255,0.78)',
            borderWidth: 1,
            borderRadius: 10,
            padding: [5, 8],
            fontSize: 12,
            fontWeight: 600,
          },
        },
      },
      {
        type: 'line',
        name: t.leaderboard?.chartParetoFrontier || 'Pareto Frontier',
        data: frontier.map(f => [f.score, f.speed]),
        lineStyle: {
          color: 'rgba(214, 159, 58, 0.86)',
          type: 'dashed',
          width: 2.5,
          shadowBlur: 10,
          shadowColor: 'rgba(214,159,58,0.40)',
        },
        itemStyle: { color: 'rgba(214,159,58,0.95)', opacity: 0.9 },
        symbol: 'diamond',
        symbolSize: 6,
        silent: true,
        z: 1,
      },
    ],
  }
})

function hexToRgba(color: string, alpha: number): string {
  if (!color.startsWith('#')) return color
  const hex = color.slice(1)
  const full = hex.length === 3 ? hex.split('').map(c => c + c).join('') : hex
  const n = parseInt(full, 16)
  const r = (n >> 16) & 255
  const g = (n >> 8) & 255
  const b = n & 255
  return `rgba(${r}, ${g}, ${b}, ${alpha})`
}

function markLineAt(value: number, axis: string, _label: string) {
  return {
    [axis]: {
      markLine: {
        silent: true,
        symbol: 'none',
        lineStyle: { color: 'rgba(255,255,255,0.58)', type: 'dashed', width: 1, opacity: 0.9 },
        label: { show: false },
        data: [{ [axis]: value }],
      },
    },
  }
}

onMounted(async () => {
  await Promise.all([
    store.fetchEntries(),
    store.fetchSummary(),
    store.fetchProviders(),
  ])
})
</script>

<style scoped>
.leaderboard-page {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-xl);
}

/* Header */
.page-header {
  display: flex;
  align-items: flex-end;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: var(--spacing-md);
}

.page-title {
  font-size: var(--font-size-2xl);
  font-weight: var(--font-weight-semibold);
  color: var(--color-text-primary);
  letter-spacing: var(--letter-spacing-tight);
}

.header-meta {
  display: flex;
  align-items: center;
  gap: var(--spacing-md);
}

.sync-stats {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 2px;
}

.last-updated {
  font-size: var(--font-size-xs);
  color: var(--color-text-tertiary);
}

.header-link,
.sync-btn {
  border: 1px solid var(--color-accent);
  background: transparent;
  color: var(--color-accent);
  font-size: var(--font-size-sm);
  font-weight: var(--font-weight-medium);
  padding: 6px 16px;
  border-radius: var(--radius-md);
  cursor: pointer;
  transition: all var(--transition-fast);
  font-family: inherit;
}

.header-link {
  text-decoration: none;
}

.header-link:hover,
.sync-btn:hover:not(:disabled) {
  background: var(--color-accent);
  color: #fff;
}

.sync-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* Filter Bar */
.filter-section {
  display: flex;
  gap: var(--spacing-sm);
  flex-wrap: wrap;
  align-items: center;
}

.search-input {
  width: 240px;
}

.provider-select {
  width: 160px;
}

.sort-select {
  width: 180px;
}

.sort-dir-btn {
  width: 36px;
  height: 36px;
  border: 1px solid var(--color-border);
  background: var(--color-bg-secondary);
  border-radius: var(--radius-md);
  font-size: 16px;
  cursor: pointer;
  color: var(--color-text-primary);
  display: flex;
  align-items: center;
  justify-content: center;
  transition: background var(--transition-fast);
}

.sort-dir-btn:hover {
  background: var(--color-bg-tertiary);
}

/* Model Category Nav */
.category-section {
  margin-bottom: calc(-1 * var(--spacing-sm));
}

.category-bar {
  display: flex;
  gap: 2px;
  background: var(--color-bg-tertiary);
  border-radius: var(--radius-lg);
  padding: 4px;
  width: fit-content;
  flex-wrap: wrap;
}

.category-btn {
  border: none;
  background: transparent;
  color: var(--color-text-secondary);
  font-size: var(--font-size-sm);
  font-weight: var(--font-weight-medium);
  padding: 8px 20px;
  border-radius: var(--radius-md);
  cursor: pointer;
  transition: all var(--transition-fast);
  font-family: inherit;
  white-space: nowrap;
}

.category-btn:hover {
  color: var(--color-text-primary);
}

.category-btn.is-active {
  background: var(--color-bg-secondary);
  color: var(--color-accent);
  box-shadow: var(--shadow-sm);
  font-weight: var(--font-weight-semibold);
}

/* Category Tabs */
.tabs-section {
  margin-bottom: calc(-1 * var(--spacing-sm));
}

.tab-bar {
  display: flex;
  gap: 2px;
  background: var(--color-bg-tertiary);
  border-radius: var(--radius-lg);
  padding: 4px;
  width: fit-content;
}

.tab-btn {
  border: none;
  background: transparent;
  color: var(--color-text-secondary);
  font-size: var(--font-size-sm);
  font-weight: var(--font-weight-medium);
  padding: 8px 20px;
  border-radius: var(--radius-md);
  cursor: pointer;
  transition: all var(--transition-fast);
  font-family: inherit;
  white-space: nowrap;
}

.tab-btn:hover {
  color: var(--color-text-primary);
}

.tab-btn.is-active {
  background: var(--color-bg-secondary);
  color: var(--color-accent);
  box-shadow: var(--shadow-sm);
  font-weight: var(--font-weight-semibold);
}

/* China AI Toggle */
.china-toggle {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-left: 4px;
  padding: 4px 12px;
  border-radius: var(--radius-md);
  background: var(--color-bg-tertiary);
  transition: background var(--transition-fast);
}

.china-toggle:has(.is-active) {
  background: rgba(220, 38, 38, 0.06);
}

.china-toggle__label {
  font-size: var(--font-size-xs);
  font-weight: var(--font-weight-medium);
  color: var(--color-text-secondary);
  white-space: nowrap;
  transition: color var(--transition-fast);
}

.china-toggle__label.is-active {
  color: #dc2626;
  font-weight: var(--font-weight-semibold);
}

/* Table */
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 200px;
  background: var(--color-bg-tertiary);
  border-radius: var(--radius-xl);
  padding: var(--spacing-2xl);
  text-align: center;
}

.empty-msg {
  font-size: var(--font-size-base);
  color: var(--color-text-secondary);
  margin-bottom: var(--spacing-xs);
}

.empty-hint {
  font-size: var(--font-size-sm);
  color: var(--color-text-tertiary);
  max-width: 420px;
}

.lb-table {
  border-radius: var(--radius-lg);
  overflow: hidden;
}

.lb-table :deep(.el-table__body tr) {
  cursor: pointer;
}

.rank-cell {
  font-weight: var(--font-weight-bold);
  font-size: var(--font-size-sm);
}

.rank-gold { color: #d4a017; }
.rank-silver { color: #888; }
.rank-bronze { color: #b8722e; }

.model-cell {
  display: flex;
  align-items: center;
  gap: 10px;
}

.model-avatar {
  flex-shrink: 0;
  width: 32px;
  height: 32px;
  border-radius: var(--radius-sm);
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 2px 6px rgba(0,0,0,0.10);
}

.model-avatar__text {
  font-size: 12px;
  font-weight: var(--font-weight-bold);
  color: #fff;
  text-shadow: 0 1px 2px rgba(0,0,0,0.12);
}

.model-name {
  font-weight: var(--font-weight-semibold);
  color: var(--color-text-primary);
}

.provider-tag {
  font-size: var(--font-size-xs);
  font-weight: var(--font-weight-semibold);
  text-transform: uppercase;
  letter-spacing: 0.04em;
}

.score-cell {
  display: flex;
  align-items: center;
  gap: 8px;
}

.score-val {
  font-size: var(--font-size-xs);
  font-weight: var(--font-weight-semibold);
  color: var(--color-accent);
  min-width: 42px;
}

.score-bar {
  flex: 1;
  height: 4px;
  background: var(--color-bg-tertiary);
  border-radius: 2px;
  overflow: hidden;
}

.score-fill {
  height: 100%;
  background: var(--color-accent);
  border-radius: 2px;
  transition: width var(--transition-smooth);
}

.metric-cell {
  font-size: var(--font-size-sm);
  font-weight: var(--font-weight-medium);
  font-variant-numeric: tabular-nums;
  color: var(--color-text-primary);
}

.na-cell {
  color: var(--color-text-tertiary);
}

/* Expand details */
.expand-detail {
  padding: var(--spacing-md) var(--spacing-lg);
}

.detail-title {
  font-size: var(--font-size-sm);
  font-weight: var(--font-weight-semibold);
  color: var(--color-text-primary);
  margin-bottom: var(--spacing-md);
}

.bench-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(180px, 1fr));
  gap: var(--spacing-sm);
}

.bench-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: var(--spacing-xs) var(--spacing-sm);
  background: var(--color-bg-tertiary);
  border-radius: var(--radius-sm);
}

.bench-label {
  font-size: var(--font-size-xs);
  color: var(--color-text-secondary);
}

.bench-val {
  font-size: var(--font-size-sm);
  font-weight: var(--font-weight-semibold);
  color: var(--color-text-primary);
}

/* Score column header + tooltip */
.th-with-info {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  cursor: help;
}

.info-mark {
  font-size: 11px;
  color: var(--color-text-tertiary);
  line-height: 1;
}

.score-tip {
  min-width: 420px;
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.score-tip__title {
  font-weight: var(--font-weight-semibold);
  font-size: var(--font-size-sm);
  margin-bottom: 4px;
}

.score-tip__table {
  display: flex;
  flex-direction: column;
  gap: 3px;
}

.score-tip__row {
  display: grid;
  grid-template-columns: 1fr 48px 2fr;
  gap: 8px;
  font-size: 11px;
  align-items: baseline;
}

.score-tip__group {
  font-weight: var(--font-weight-medium);
  white-space: nowrap;
}

.score-tip__weight {
  color: var(--color-accent);
  font-weight: var(--font-weight-semibold);
  font-variant-numeric: tabular-nums;
  text-align: right;
}

.score-tip__bench {
  color: var(--color-text-secondary, #ccc);
  font-variant-numeric: tabular-nums;
  font-size: 10px;
}

.score-tip__note {
  margin-top: 6px;
  padding-top: 6px;
  border-top: 1px solid rgba(255, 255, 255, 0.1);
  font-size: var(--font-size-xs);
  opacity: 0.85;
}

/* Score breakdown cards inside expand row */
.detail-title--secondary {
  margin-top: var(--spacing-lg);
}

.breakdown-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
  gap: var(--spacing-sm);
  margin-bottom: var(--spacing-sm);
}

.breakdown-card {
  background: var(--color-bg-secondary);
  border: 1px solid var(--color-border, rgba(0,0,0,0.06));
  border-radius: var(--radius-md);
  padding: var(--spacing-sm) var(--spacing-md);
  display: flex;
  flex-direction: column;
  gap: 6px;
  transition: opacity var(--transition-fast);
}

.breakdown-card.is-missing {
  opacity: 0.5;
}

.breakdown-card__head {
  display: flex;
  justify-content: space-between;
  align-items: baseline;
}

.breakdown-card__group {
  font-size: var(--font-size-xs);
  font-weight: var(--font-weight-semibold);
  text-transform: uppercase;
  letter-spacing: 0.04em;
  color: var(--color-text-secondary);
  display: flex;
  align-items: center;
  gap: 6px;
}

.breakdown-card__weight {
  display: inline-block;
  font-size: 10px;
  font-weight: var(--font-weight-bold);
  color: var(--color-accent);
  background: color-mix(in srgb, var(--color-accent) 12%, transparent);
  padding: 1px 6px;
  border-radius: 99px;
  letter-spacing: 0;
  text-transform: none;
}

.breakdown-card__benchmarks {
  font-size: 10px;
  color: var(--color-text-tertiary);
  line-height: 1.4;
}

.breakdown-card__val {
  font-size: var(--font-size-base);
  font-weight: var(--font-weight-bold);
  color: var(--color-accent);
  font-variant-numeric: tabular-nums;
}

.breakdown-card__inputs {
  display: flex;
  flex-wrap: wrap;
  gap: 4px 12px;
}

.breakdown-bench {
  display: inline-flex;
  align-items: baseline;
  gap: 4px;
  font-size: 11px;
}

.breakdown-bench__name {
  color: var(--color-text-tertiary);
}

.breakdown-bench__val {
  color: var(--color-text-secondary);
  font-variant-numeric: tabular-nums;
  font-weight: var(--font-weight-medium);
}

.breakdown-bench.is-missing .breakdown-bench__val {
  color: var(--color-text-tertiary);
}

.breakdown-formula {
  font-size: var(--font-size-xs);
  color: var(--color-text-tertiary);
  margin-bottom: var(--spacing-md);
  padding: 6px 10px;
  background: var(--color-bg-tertiary);
  border-radius: var(--radius-sm);
  border-left: 3px solid var(--color-accent);
}

/* Pagination */
.pagination-section {
  display: flex;
  justify-content: center;
}

/* Chart */
.chart-section {
  position: relative;
}

.chart-card {
  position: relative;
  overflow: hidden;
  border-radius: 34px;
  padding: 20px;
  background:
    linear-gradient(135deg, rgba(255,255,255,0.72), rgba(255,255,255,0.28)),
    radial-gradient(circle at 18% 8%, rgba(122, 181, 255, 0.28), transparent 34%),
    radial-gradient(circle at 78% 14%, rgba(154, 236, 209, 0.22), transparent 30%),
    rgba(246, 249, 255, 0.58);
  border: 1px solid rgba(255,255,255,0.68);
  box-shadow:
    0 28px 80px rgba(31, 41, 55, 0.14),
    inset 0 1px 0 rgba(255,255,255,0.82),
    inset 0 -1px 0 rgba(255,255,255,0.28);
  backdrop-filter: blur(34px) saturate(1.65);
  -webkit-backdrop-filter: blur(34px) saturate(1.65);
  isolation: isolate;
}

.chart-card::before {
  content: '';
  position: absolute;
  inset: 0;
  pointer-events: none;
  background:
    linear-gradient(115deg, rgba(255,255,255,0.86), transparent 22%, transparent 72%, rgba(255,255,255,0.38)),
    repeating-linear-gradient(135deg, rgba(255,255,255,0.16) 0 1px, transparent 1px 10px);
  opacity: 0.54;
  z-index: -1;
}

.chart-card::after {
  content: '';
  position: absolute;
  inset: 1px;
  border-radius: 33px;
  pointer-events: none;
  box-shadow: inset 0 0 0 1px rgba(255,255,255,0.42);
}

.liquid-orb {
  position: absolute;
  border-radius: 999px;
  filter: blur(8px);
  opacity: 0.68;
  pointer-events: none;
  mix-blend-mode: screen;
}

.liquid-orb--blue {
  width: 210px;
  height: 210px;
  left: -70px;
  top: -78px;
  background: radial-gradient(circle, rgba(0,113,227,0.36), transparent 68%);
}

.liquid-orb--mint {
  width: 260px;
  height: 260px;
  right: 6%;
  top: -118px;
  background: radial-gradient(circle, rgba(52,199,123,0.24), transparent 66%);
}

.liquid-orb--gold {
  width: 180px;
  height: 180px;
  right: -48px;
  bottom: -70px;
  background: radial-gradient(circle, rgba(255,204,0,0.22), transparent 68%);
}

.chart-card__chrome {
  position: relative;
  z-index: 1;
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 16px;
  padding: 4px 4px 16px;
}

.chart-eyebrow,
.chart-pill {
  width: fit-content;
  border: 1px solid rgba(255,255,255,0.72);
  background: rgba(255,255,255,0.38);
  color: rgba(29,29,31,0.66);
  box-shadow: inset 0 1px 0 rgba(255,255,255,0.72), 0 8px 24px rgba(31,41,55,0.08);
  backdrop-filter: blur(18px) saturate(1.45);
  -webkit-backdrop-filter: blur(18px) saturate(1.45);
}

.chart-eyebrow {
  margin-bottom: 10px;
  padding: 5px 10px;
  border-radius: 999px;
  font-size: 11px;
  font-weight: 700;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}

.chart-pill {
  flex-shrink: 0;
  padding: 8px 12px;
  border-radius: 999px;
  font-size: 12px;
  font-weight: 700;
}

.chart-title {
  font-size: clamp(20px, 2.2vw, 28px);
  font-weight: 700;
  color: #1d1d1f;
  letter-spacing: -0.04em;
  margin: 0;
}

.chart-subtitle {
  font-size: var(--font-size-xs);
  color: rgba(60,60,67,0.66);
  margin: 6px 0 0;
}

.chart-stage {
  position: relative;
  z-index: 1;
  overflow: hidden;
  border-radius: 26px;
  background:
    linear-gradient(180deg, rgba(255,255,255,0.40), rgba(255,255,255,0.16)),
    rgba(255,255,255,0.26);
  border: 1px solid rgba(255,255,255,0.62);
  box-shadow:
    inset 0 1px 0 rgba(255,255,255,0.78),
    inset 0 -18px 42px rgba(255,255,255,0.18),
    0 18px 50px rgba(31,41,55,0.10);
  backdrop-filter: blur(22px) saturate(1.45);
  -webkit-backdrop-filter: blur(22px) saturate(1.45);
}

.chart-stage::before {
  content: '';
  position: absolute;
  inset: 0;
  pointer-events: none;
  background: radial-gradient(circle at 50% 0%, rgba(255,255,255,0.46), transparent 42%);
}

.chart-instance {
  position: relative;
  width: 100%;
  height: 500px;
}

@media (max-width: 800px) {
  .tab-bar { overflow-x: auto; width: 100%; }
  .filter-section { flex-direction: column; }
  .search-input, .provider-select { width: 100%; }
  .china-toggle { margin-left: 0; justify-content: center; }
}

@media (max-width: 480px) {
  .tab-btn { padding: 6px 12px; font-size: var(--font-size-xs); }
}
</style>
