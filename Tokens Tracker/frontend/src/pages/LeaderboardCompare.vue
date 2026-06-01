<template>
  <div class="compare-page">
    <section class="page-header anim-fade-up">
      <div>
        <p class="page-eyebrow">Model Comparison</p>
        <h1 class="page-title">模型横向对比</h1>
        <p class="page-subtitle">勾选 2-4 个模型，对比价格、速度、上下文、能力分和知识截止日期。</p>
      </div>
      <RouterLink class="back-link" to="/leaderboard">返回排行榜</RouterLink>
    </section>

    <section class="filter-section">
      <el-input
        v-model="searchText"
        placeholder="搜索模型..."
        class="search-input"
        clearable
        @input="onSearchDebounced"
      />
      <el-select
        v-model="providerFilter"
        placeholder="Provider"
        class="provider-select"
        clearable
        @change="fetchModels"
      >
        <el-option
          v-for="provider in providers"
          :key="provider"
          :label="provider"
          :value="provider"
        />
      </el-select>
      <span class="selection-hint" :class="{ 'is-ready': canCompare }">
        已选择 {{ selectedModels.length }}/4
      </span>
    </section>

    <section v-if="selectedModels.length > 0" class="comparison-section">
      <div v-if="!canCompare" class="compare-empty">至少选择 2 个模型开始对比。</div>
      <div v-else class="comparison-card">
        <table class="comparison-table">
          <thead>
            <tr>
              <th>指标</th>
              <th v-for="model in selectedModels" :key="model.id">
                <div class="model-heading">
                  <ProviderIcon :provider="model.provider" :size="28" />
                  <span>{{ model.model_name }}</span>
                </div>
              </th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="row in comparisonRows" :key="row.key">
              <td class="metric-label">{{ row.label }}</td>
              <td v-for="model in selectedModels" :key="model.id" class="metric-value">
                {{ row.value(model) }}
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </section>

    <section class="table-section">
      <el-table
        ref="tableRef"
        :data="models"
        v-loading="loading"
        stripe
        class="compare-table"
        row-key="id"
        @selection-change="onSelectionChange"
      >
        <el-table-column type="selection" width="52" :selectable="isSelectable" />
        <el-table-column label="模型" min-width="220">
          <template #default="{ row }">
            <div class="model-cell">
              <ProviderIcon :provider="row.provider" :size="32" />
              <div>
                <div class="model-name">{{ row.model_name }}</div>
                <div class="model-provider">{{ row.provider }}</div>
              </div>
            </div>
          </template>
        </el-table-column>
        <el-table-column label="能力分" width="110" align="right">
          <template #default="{ row }">{{ formatScore(row.overall_score) }}</template>
        </el-table-column>
        <el-table-column label="速度" width="110" align="right">
          <template #default="{ row }">{{ formatSpeed(row.tokens_per_second) }}</template>
        </el-table-column>
        <el-table-column label="输入价格" width="120" align="right">
          <template #default="{ row }">{{ formatPrice(pricingFor(row).inputPrice) }}</template>
        </el-table-column>
        <el-table-column label="输出价格" width="120" align="right">
          <template #default="{ row }">{{ formatPrice(pricingFor(row).outputPrice) }}</template>
        </el-table-column>
        <el-table-column label="上下文" width="110" align="right">
          <template #default="{ row }">{{ formatContext(row.context_window) }}</template>
        </el-table-column>
      </el-table>
    </section>
  </div>
</template>

<script setup lang="ts">
import { computed, nextTick, onMounted, ref } from 'vue'
import { useRoute } from 'vue-router'
import type { TableInstance } from 'element-plus'
import { fetchLeaderboardModels, fetchLeaderboardProviders } from '../api/leaderboard'
import { useModelsStore } from '../stores/models'
import ProviderIcon from '../components/ProviderIcon.vue'
import type { LeaderboardEntry, ModelEntry } from '../types'

type PricingInfo = {
  inputPrice: number | null
  outputPrice: number | null
  source: string | null
}

const route = useRoute()
const modelsStore = useModelsStore()
const models = ref<LeaderboardEntry[]>([])
const providers = ref<string[]>([])
const selectedModels = ref<LeaderboardEntry[]>([])
const loading = ref(false)
const searchText = ref('')
const providerFilter = ref<string>()
const tableRef = ref<TableInstance>()
let searchTimer: ReturnType<typeof setTimeout> | null = null
let querySelectionApplied = false

const canCompare = computed(() => selectedModels.value.length >= 2)

const pricingLookup = computed(() => {
  const map = new Map<string, PricingInfo>()
  for (const provider of modelsStore.registry.providers) {
    for (const model of provider.models) {
      const entry = normalizeModel(model)
      const info = {
        inputPrice: entry.pricing?.input ?? null,
        outputPrice: entry.pricing?.output ?? null,
        source: entry.pricing_source ?? null,
      }
      setPricing(map, provider.name, entry.name, info)
      setPricing(map, provider.id, entry.name, info)
      setPricing(map, '', entry.name, info)
    }
  }
  return map
})

const comparisonRows = computed(() => [
  { key: 'provider', label: 'Provider', value: (model: LeaderboardEntry) => model.provider || '—' },
  { key: 'price', label: '价格（输入/输出）', value: (model: LeaderboardEntry) => formatPricing(model) },
  { key: 'context', label: '上下文', value: (model: LeaderboardEntry) => formatContext(model.context_window) },
  { key: 'speed', label: '速度', value: (model: LeaderboardEntry) => formatSpeed(model.tokens_per_second) },
  { key: 'coding', label: '编程', value: (model: LeaderboardEntry) => formatScore(model.score_coding) },
  { key: 'math', label: '数学', value: (model: LeaderboardEntry) => formatScore(model.category_math_score ?? model.score_math) },
  { key: 'reasoning', label: '推理', value: (model: LeaderboardEntry) => formatScore(model.score_reasoning) },
  { key: 'writing', label: '写作', value: (model: LeaderboardEntry) => formatScore(model.category_writing_score) },
  { key: 'overall', label: '综合分数', value: (model: LeaderboardEntry) => formatScore(model.overall_score) },
])

async function fetchModels() {
  loading.value = true
  try {
    const res = await fetchLeaderboardModels({
      search: searchText.value || undefined,
      provider: providerFilter.value,
      sort_by: 'overall_score',
      sort_dir: 'desc',
      modality: 'text',
      skip: 0,
      limit: 100,
    })
    models.value = res.entries
    await nextTick()
    syncSelectionAfterFetch()
  } finally {
    loading.value = false
  }
}

function syncSelectionAfterFetch() {
  applyQuerySelection()
  const selectedIds = new Set(selectedModels.value.map((model) => model.id))
  selectedModels.value = models.value.filter((model) => selectedIds.has(model.id))
  tableRef.value?.clearSelection()
  selectedModels.value.forEach((model) => {
    tableRef.value?.toggleRowSelection(model, true)
  })
}

function applyQuerySelection() {
  if (querySelectionApplied) return
  const modelName = typeof route.query.model === 'string' ? route.query.model : ''
  if (!modelName) return
  const matched = models.value.find((model) => isSameModel(model.model_name, modelName))
  if (matched) {
    selectedModels.value = [matched]
    querySelectionApplied = true
  }
}

function onSearchDebounced() {
  if (searchTimer) clearTimeout(searchTimer)
  searchTimer = setTimeout(fetchModels, 300)
}

function onSelectionChange(selection: LeaderboardEntry[]) {
  selectedModels.value = selection.slice(0, 4)
  if (selection.length > 4) {
    tableRef.value?.toggleRowSelection(selection[selection.length - 1], false)
  }
}

function isSelectable(row: LeaderboardEntry): boolean {
  return selectedModels.value.length < 4 || selectedModels.value.some((model) => model.id === row.id)
}

function normalizeModel(model: string | ModelEntry): ModelEntry {
  return typeof model === 'string' ? { name: model } : model
}

function setPricing(map: Map<string, PricingInfo>, provider: string, model: string, info: PricingInfo) {
  map.set(pricingKey(provider, model), info)
}

function pricingKey(provider: string, model: string): string {
  return `${provider.trim().toLowerCase()}::${normalizeModelName(model)}`
}

function normalizeModelName(model: string): string {
  return model.trim().toLowerCase().replace(/\s+/g, '-').replace(/[^a-z0-9.:-]+/g, '-')
}

function isSameModel(left: string, right: string): boolean {
  return normalizeModelName(left) === normalizeModelName(right)
}

function pricingFor(model: LeaderboardEntry): PricingInfo {
  return pricingLookup.value.get(pricingKey(model.provider, model.model_slug))
    || pricingLookup.value.get(pricingKey(model.provider, model.model_name))
    || pricingLookup.value.get(pricingKey('', model.model_slug))
    || pricingLookup.value.get(pricingKey('', model.model_name))
    || { inputPrice: null, outputPrice: null, source: null }
}

function formatPricing(model: LeaderboardEntry): string {
  const pricing = pricingFor(model)
  return `${formatPrice(pricing.inputPrice)} / ${formatPrice(pricing.outputPrice)}`
}

function formatScore(value: number | null): string {
  if (value == null) return '—'
  return value > 1 ? value.toFixed(1) : (value * 100).toFixed(1)
}

function formatSpeed(value: number | null): string {
  if (value == null) return '—'
  if (value >= 1000) return `${(value / 1000).toFixed(1)}K t/s`
  return `${value.toFixed(0)} t/s`
}

function formatPrice(value: number | null): string {
  if (value == null) return '—'
  return `$${value.toFixed(2)}/M`
}

function formatContext(value: number | null): string {
  if (value == null) return '—'
  if (value >= 1_000_000) return `${(value / 1_000_000).toFixed(1)}M`
  if (value >= 1_000) return `${(value / 1_000).toFixed(0)}K`
  return value.toLocaleString()
}

onMounted(async () => {
  await Promise.all([
    modelsStore.fetchRegistry(),
    fetchModels(),
    fetchLeaderboardProviders().then((res) => { providers.value = res }),
  ])
})
</script>

<style scoped>
.compare-page {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-xl);
}

.page-header {
  display: flex;
  align-items: flex-end;
  justify-content: space-between;
  gap: var(--spacing-md);
  flex-wrap: wrap;
}

.page-eyebrow {
  margin: 0 0 6px;
  font-size: var(--font-size-xs);
  font-weight: var(--font-weight-bold);
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: var(--color-accent);
}

.page-title {
  margin: 0;
  font-size: var(--font-size-2xl);
  font-weight: var(--font-weight-semibold);
  color: var(--color-text-primary);
  letter-spacing: var(--letter-spacing-tight);
}

.page-subtitle {
  margin: 8px 0 0;
  color: var(--color-text-secondary);
  font-size: var(--font-size-sm);
}

.back-link {
  border: 1px solid var(--color-border);
  background: var(--color-bg-secondary);
  color: var(--color-text-primary);
  font-size: var(--font-size-sm);
  font-weight: var(--font-weight-medium);
  padding: 8px 16px;
  border-radius: var(--radius-md);
  text-decoration: none;
  transition: all var(--transition-fast);
}

.back-link:hover {
  border-color: var(--color-accent);
  color: var(--color-accent);
}

.filter-section {
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
  flex-wrap: wrap;
}

.search-input {
  width: 260px;
}

.provider-select {
  width: 180px;
}

.selection-hint {
  display: inline-flex;
  align-items: center;
  min-height: 32px;
  padding: 0 12px;
  border-radius: 999px;
  background: var(--color-bg-tertiary);
  color: var(--color-text-secondary);
  font-size: var(--font-size-xs);
  font-weight: var(--font-weight-semibold);
}

.selection-hint.is-ready {
  background: color-mix(in srgb, var(--color-accent) 12%, transparent);
  color: var(--color-accent);
}

.comparison-section {
  overflow-x: auto;
}

.compare-empty,
.comparison-card {
  border-radius: var(--radius-xl);
  background: var(--color-bg-secondary);
  border: 1px solid var(--color-border);
}

.compare-empty {
  padding: var(--spacing-lg);
  color: var(--color-text-secondary);
  font-size: var(--font-size-sm);
}

.comparison-card {
  overflow: hidden;
}

.comparison-table {
  width: 100%;
  min-width: 720px;
  border-collapse: collapse;
}

.comparison-table th,
.comparison-table td {
  padding: 14px 16px;
  border-bottom: 1px solid var(--color-border);
  text-align: left;
  vertical-align: middle;
}

.comparison-table tr:last-child td {
  border-bottom: none;
}

.comparison-table th {
  background: var(--color-bg-tertiary);
  color: var(--color-text-secondary);
  font-size: var(--font-size-xs);
  font-weight: var(--font-weight-semibold);
}

.model-heading,
.model-cell {
  display: flex;
  align-items: center;
  gap: 10px;
}

.model-heading {
  color: var(--color-text-primary);
  font-size: var(--font-size-sm);
}

.metric-label {
  width: 140px;
  color: var(--color-text-secondary);
  font-size: var(--font-size-sm);
  font-weight: var(--font-weight-semibold);
}

.metric-value {
  color: var(--color-text-primary);
  font-size: var(--font-size-sm);
  font-weight: var(--font-weight-medium);
  font-variant-numeric: tabular-nums;
}

.compare-table {
  border-radius: var(--radius-lg);
  overflow: hidden;
}

.model-name {
  color: var(--color-text-primary);
  font-weight: var(--font-weight-semibold);
}

.model-provider {
  margin-top: 2px;
  color: var(--color-text-tertiary);
  font-size: var(--font-size-xs);
}

@media (max-width: 800px) {
  .filter-section {
    align-items: stretch;
    flex-direction: column;
  }

  .search-input,
  .provider-select {
    width: 100%;
  }
}
</style>
