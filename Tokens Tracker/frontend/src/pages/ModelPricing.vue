<template>
  <div class="pricing-page">
    <section class="page-header anim-fade-up">
      <div>
        <h1 class="page-title">模型价格</h1>
        <p class="page-subtitle">按供应商和模型查看每百万 tokens 的输入/输出价格</p>
      </div>
      <div class="header-actions">
        <span v-if="modelsStore.registry.updated_at" class="updated-at">
          更新时间：{{ formatDate(modelsStore.registry.updated_at) }}
        </span>
        <button class="sync-btn" :disabled="modelsStore.syncing" @click="onSync">
          {{ modelsStore.syncing ? '同步中...' : '同步价格' }}
        </button>
      </div>
    </section>

    <section class="filter-section">
      <el-select
        v-model="selectedProvider"
        class="provider-select"
        placeholder="选择供应商"
        clearable
        filterable
      >
        <el-option
          v-for="provider in providerOptions"
          :key="provider"
          :label="provider"
          :value="provider"
        />
      </el-select>
      <el-select
        v-model="selectedModel"
        class="model-select"
        placeholder="选择模型"
        clearable
        filterable
      >
        <el-option
          v-for="model in modelOptions"
          :key="model"
          :label="model"
          :value="model"
        />
      </el-select>
      <div class="currency-switch">
        <button
          v-for="item in currencies"
          :key="item.code"
          class="currency-btn"
          :class="{ 'is-active': currency === item.code }"
          @click="currency = item.code"
        >
          {{ item.code }}
        </button>
      </div>
    </section>

    <section v-if="selectedDetail" class="model-insight-card">
      <div class="model-insight-card__main">
        <div>
          <p class="model-insight-card__eyebrow">Selected Model</p>
          <h2 class="model-insight-card__title">{{ selectedDetail.model }}</h2>
          <p class="model-insight-card__provider">{{ selectedDetail.provider }}</p>
        </div>
        <div class="model-insight-card__actions">
          <RouterLink class="link-btn" :to="{ path: '/leaderboard/compare', query: { model: selectedDetail.model } }">加入对比</RouterLink>
          <RouterLink class="link-btn" :to="{ path: '/leaderboard', query: { search: selectedDetail.model } }">查看排行</RouterLink>
        </div>
      </div>
      <div class="insight-grid">
        <div class="insight-item">
          <span>输入价格</span>
          <strong>{{ selectedDetail.inputPrice != null ? formatPrice(selectedDetail.inputPrice) : '暂无数据' }}</strong>
        </div>
        <div class="insight-item">
          <span>输出价格</span>
          <strong>{{ selectedDetail.outputPrice != null ? formatPrice(selectedDetail.outputPrice) : '暂无数据' }}</strong>
        </div>
        <div class="insight-item">
          <span>综合分数</span>
          <strong>{{ formatScore(selectedLeaderboard?.overall_score ?? null) }}</strong>
        </div>
        <div class="insight-item">
          <span>速度</span>
          <strong>{{ formatSpeed(selectedLeaderboard?.tokens_per_second ?? null) }}</strong>
        </div>
        <div class="insight-item">
          <span>上下文</span>
          <strong>{{ formatContext(selectedLeaderboard?.context_window ?? null) }}</strong>
        </div>
      </div>
    </section>

    <section class="table-section">
      <el-table :data="filteredRows" stripe class="pricing-table" row-key="key" highlight-current-row @row-click="onRowClick">
        <el-table-column label="供应商" prop="provider" min-width="150">
          <template #default="{ row }">
            <span class="provider-name" :style="{ color: row.color }">{{ row.provider }}</span>
          </template>
        </el-table-column>
        <el-table-column label="模型" prop="model" min-width="260">
          <template #default="{ row }">
            <span class="model-name">{{ row.model }}</span>
          </template>
        </el-table-column>
        <el-table-column :label="`输入价格 / M tokens (${currency})`" min-width="180" align="right">
          <template #default="{ row }">
            <span v-if="row.inputPrice != null" class="price-cell">{{ formatPrice(row.inputPrice) }}</span>
            <span v-else class="empty-price">暂无数据</span>
          </template>
        </el-table-column>
        <el-table-column :label="`输出价格 / M tokens (${currency})`" min-width="180" align="right">
          <template #default="{ row }">
            <span v-if="row.outputPrice != null" class="price-cell">{{ formatPrice(row.outputPrice) }}</span>
            <span v-else class="empty-price">暂无数据</span>
          </template>
        </el-table-column>
        <el-table-column label="来源" width="140">
          <template #default="{ row }">
            <span class="source-cell">{{ row.source || '—' }}</span>
          </template>
        </el-table-column>
      </el-table>
    </section>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue'
import { ElMessage } from 'element-plus'
import { fetchLeaderboardModels } from '../api/leaderboard'
import { useModelsStore } from '../stores/models'
import type { LeaderboardEntry, ModelEntry } from '../types'

type CurrencyCode = 'USD' | 'CNY' | 'EUR' | 'JPY'

type PricingRow = {
  key: string
  provider: string
  color: string
  model: string
  inputPrice: number | null
  outputPrice: number | null
  source: string | null
  order: number
}

const modelsStore = useModelsStore()
const selectedProvider = ref<string>()
const selectedModel = ref<string>()
const currency = ref<CurrencyCode>('USD')
const leaderboardRows = ref<LeaderboardEntry[]>([])

const currencies: Array<{ code: CurrencyCode; symbol: string; rate: number }> = [
  { code: 'USD', symbol: '$', rate: 1 },
  { code: 'CNY', symbol: '¥', rate: 7.25 },
  { code: 'EUR', symbol: '€', rate: 0.92 },
  { code: 'JPY', symbol: '¥', rate: 156 },
]

const providerOptions = computed(() => modelsStore.registry.providers.map(provider => provider.name))

const rows = computed<PricingRow[]>(() => {
  const result: PricingRow[] = []
  for (const provider of modelsStore.registry.providers) {
    provider.models.forEach((model, index) => {
      const entry = normalizeModel(model)
      result.push({
        key: `${provider.id}:${entry.name}`,
        provider: provider.name,
        color: provider.color,
        model: entry.name,
        inputPrice: entry.pricing?.input ?? null,
        outputPrice: entry.pricing?.output ?? null,
        source: entry.pricing_source ?? null,
        order: index,
      })
    })
  }
  return result
})

const modelOptions = computed(() => {
  const source = selectedProvider.value
    ? rows.value.filter(row => row.provider === selectedProvider.value)
    : rows.value
  return source.map(row => row.model)
})

const filteredRows = computed(() => rows.value.filter(row => {
  if (selectedProvider.value && row.provider !== selectedProvider.value) return false
  if (selectedModel.value && row.model !== selectedModel.value) return false
  return true
}))

const selectedDetail = computed(() => {
  if (!selectedModel.value) return null
  return rows.value.find(row => row.model === selectedModel.value && (!selectedProvider.value || row.provider === selectedProvider.value)) ?? null
})

const selectedLeaderboard = computed(() => {
  if (!selectedModel.value) return null
  return leaderboardRows.value.find(row => isSameModel(row.model_name, selectedModel.value!) || isSameModel(row.model_slug, selectedModel.value!)) ?? null
})

watch(selectedProvider, () => {
  if (selectedModel.value && !modelOptions.value.includes(selectedModel.value)) {
    selectedModel.value = undefined
  }
})

watch(selectedModel, (model) => {
  if (model) fetchLeaderboardDetail(model)
})

onMounted(async () => {
  await modelsStore.fetchRegistry()
  if (rows.value.length > 0) {
    selectedProvider.value = rows.value[0].provider
    selectedModel.value = rows.value[0].model
  }
})

function normalizeModel(model: string | ModelEntry): ModelEntry {
  return typeof model === 'string' ? { name: model } : model
}

function onRowClick(row: PricingRow) {
  selectedProvider.value = row.provider
  selectedModel.value = row.model
}

async function fetchLeaderboardDetail(model: string) {
  const res = await fetchLeaderboardModels({
    search: model,
    sort_by: 'overall_score',
    sort_dir: 'desc',
    modality: 'text',
    skip: 0,
    limit: 20,
  })
  leaderboardRows.value = res.entries
}

function normalizeModelName(model: string): string {
  return model.trim().toLowerCase().replace(/\s+/g, '-').replace(/[^a-z0-9.:-]+/g, '-')
}

function isSameModel(left: string, right: string): boolean {
  return normalizeModelName(left) === normalizeModelName(right)
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

function formatContext(value: number | null): string {
  if (value == null) return '—'
  if (value >= 1_000_000) return `${(value / 1_000_000).toFixed(1)}M`
  if (value >= 1_000) return `${(value / 1_000).toFixed(0)}K`
  return value.toLocaleString()
}

function formatPrice(value: number): string {
  const item = currencies.find(c => c.code === currency.value)!
  const converted = value * item.rate
  if (currency.value === 'JPY') return `${item.symbol}${converted.toFixed(0)}`
  if (converted < 0.01) return `${item.symbol}${converted.toFixed(4)}`
  return `${item.symbol}${converted.toFixed(2)}`
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

async function onSync() {
  const result = await modelsStore.syncRegistry()
  if (result.ok) {
    ElMessage.success(`已同步 ${result.providers || 0} 个供应商 / ${result.models || 0} 个模型`)
  } else {
    ElMessage.error(result.detail || '同步失败')
  }
}
</script>

<style scoped>
.pricing-page {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-xl);
}

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

.page-subtitle {
  margin-top: 6px;
  color: var(--color-text-secondary);
  font-size: var(--font-size-sm);
}

.header-actions {
  display: flex;
  align-items: center;
  gap: var(--spacing-md);
}

.updated-at {
  font-size: var(--font-size-xs);
  color: var(--color-text-tertiary);
}

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

.sync-btn:hover:not(:disabled) {
  background: var(--color-accent);
  color: #fff;
}

.sync-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.filter-section {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: var(--spacing-sm);
}

.provider-select {
  width: 190px;
}

.model-select {
  width: 280px;
}

.currency-switch {
  display: flex;
  gap: 2px;
  background: var(--color-bg-tertiary);
  border-radius: var(--radius-lg);
  padding: 4px;
}

.currency-btn {
  border: none;
  background: transparent;
  color: var(--color-text-secondary);
  font-size: var(--font-size-sm);
  font-weight: var(--font-weight-medium);
  padding: 8px 16px;
  border-radius: var(--radius-md);
  cursor: pointer;
  transition: all var(--transition-fast);
  font-family: inherit;
}

.currency-btn.is-active {
  background: var(--color-bg-secondary);
  color: var(--color-accent);
  box-shadow: var(--shadow-sm);
  font-weight: var(--font-weight-semibold);
}

.model-insight-card {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-md);
  padding: var(--spacing-lg);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-xl);
  background: var(--color-bg-secondary);
}

.model-insight-card__main {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: var(--spacing-md);
  flex-wrap: wrap;
}

.model-insight-card__eyebrow {
  margin: 0 0 6px;
  font-size: var(--font-size-xs);
  font-weight: var(--font-weight-bold);
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: var(--color-accent);
}

.model-insight-card__title {
  margin: 0;
  color: var(--color-text-primary);
  font-size: var(--font-size-xl);
  font-weight: var(--font-weight-semibold);
}

.model-insight-card__provider {
  margin: 6px 0 0;
  color: var(--color-text-secondary);
  font-size: var(--font-size-sm);
}

.model-insight-card__actions {
  display: flex;
  gap: var(--spacing-sm);
}

.link-btn {
  border: 1px solid var(--color-accent);
  background: transparent;
  color: var(--color-accent);
  font-size: var(--font-size-sm);
  font-weight: var(--font-weight-medium);
  padding: 7px 14px;
  border-radius: var(--radius-md);
  text-decoration: none;
  transition: all var(--transition-fast);
}

.link-btn:hover {
  background: var(--color-accent);
  color: #fff;
}

.insight-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
  gap: var(--spacing-sm);
}

.insight-item {
  display: flex;
  flex-direction: column;
  gap: 6px;
  padding: var(--spacing-sm);
  border-radius: var(--radius-md);
  background: var(--color-bg-tertiary);
}

.insight-item span {
  color: var(--color-text-secondary);
  font-size: var(--font-size-xs);
}

.insight-item strong {
  color: var(--color-text-primary);
  font-size: var(--font-size-sm);
  font-variant-numeric: tabular-nums;
}

.pricing-table {
  border-radius: var(--radius-lg);
  overflow: hidden;
}

.pricing-table :deep(.el-table__body tr) {
  cursor: pointer;
}

.provider-name {
  font-size: var(--font-size-xs);
  font-weight: var(--font-weight-semibold);
  text-transform: uppercase;
  letter-spacing: 0.04em;
}

.model-name {
  font-weight: var(--font-weight-semibold);
  color: var(--color-text-primary);
}

.price-cell {
  font-size: var(--font-size-sm);
  font-weight: var(--font-weight-semibold);
  font-variant-numeric: tabular-nums;
  color: var(--color-text-primary);
}

.empty-price,
.source-cell {
  color: var(--color-text-tertiary);
  font-size: var(--font-size-sm);
}

@media (max-width: 800px) {
  .filter-section {
    flex-direction: column;
    align-items: stretch;
  }

  .provider-select,
  .model-select {
    width: 100%;
  }
}
</style>
