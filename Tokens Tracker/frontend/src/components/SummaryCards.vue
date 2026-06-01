<template>
  <div class="stat-grid">
    <div class="stat-card anim-card-enter" style="animation-delay: 0ms">
      <div class="stat-card-top">
        <span class="stat-label">{{ inputLabel }}</span>
        <div class="metric-switcher">
          <button
            v-for="opt in metricOptions"
            :key="opt.key"
            class="metric-btn"
            :class="{ active: inputMetric === opt.key }"
            @click="inputMetric = opt.key"
          >
            {{ opt.label }}
          </button>
        </div>
      </div>
      <span class="stat-value">{{ inputDisplay }}</span>
    </div>
    <div class="stat-card anim-card-enter" style="animation-delay: 60ms">
      <div class="stat-card-top">
        <span class="stat-label">{{ outputLabel }}</span>
        <div class="metric-switcher">
          <button
            v-for="opt in metricOptions"
            :key="opt.key"
            class="metric-btn"
            :class="{ active: outputMetric === opt.key }"
            @click="outputMetric = opt.key"
          >
            {{ opt.label }}
          </button>
        </div>
      </div>
      <span class="stat-value">{{ outputDisplay }}</span>
    </div>
    <div class="stat-card anim-card-enter" style="animation-delay: 120ms">
      <div class="stat-card-top">
        <span class="stat-label">{{ totalLabel }}</span>
        <div class="metric-switcher">
          <button
            v-for="opt in metricOptions"
            :key="opt.key"
            class="metric-btn"
            :class="{ active: totalMetric === opt.key }"
            @click="totalMetric = opt.key"
          >
            {{ opt.label }}
          </button>
        </div>
      </div>
      <span class="stat-value is-accent">{{ totalDisplay }}</span>
    </div>
    <div class="stat-card anim-card-enter" style="animation-delay: 180ms">
      <div class="stat-card-top">
        <span class="stat-label">{{ loc.t.summary.recordCount }}</span>
      </div>
      <span class="stat-value">{{ countDisplay }}</span>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'
import { useTokenRecordsStore } from '../stores/tokenRecords'
import { useLocaleStore } from '../stores/locale'
import { useCountUp } from '../composables/useCountUp'

type Metric = 'tokens' | 'cost'

const store = useTokenRecordsStore()
const loc = useLocaleStore()

const inputMetric = ref<Metric>('tokens')
const outputMetric = ref<Metric>('tokens')
const totalMetric = ref<Metric>('tokens')

const metricOptions = computed(() => [
  { key: 'tokens' as Metric, label: loc.t.charts.metricTokens },
  { key: 'cost' as Metric, label: loc.t.charts.metricCost },
])

const formatCost = (v?: number) => '$' + (v ?? 0).toFixed(4)

const inputLabel = computed(() => inputMetric.value === 'cost' ? loc.t.summary.totalInputCost : loc.t.summary.totalInput)
const outputLabel = computed(() => outputMetric.value === 'cost' ? loc.t.summary.totalOutputCost : loc.t.summary.totalOutput)
const totalLabel = computed(() => totalMetric.value === 'cost' ? loc.t.summary.totalCost : loc.t.summary.totalTokens)

const inputTarget = computed(() => store.totals?.total_input_tokens)
const outputTarget = computed(() => store.totals?.total_output_tokens)
const totalTarget = computed(() => store.totals?.total_tokens)
const countTarget = computed(() => store.totals?.record_count)

const inputTokensDisplay = useCountUp(inputTarget)
const outputTokensDisplay = useCountUp(outputTarget)
const totalTokensDisplay = useCountUp(totalTarget)
const countDisplay = useCountUp(countTarget)

const inputDisplay = computed(() => inputMetric.value === 'cost' ? formatCost(store.totals?.total_input_cost) : inputTokensDisplay.value)
const outputDisplay = computed(() => outputMetric.value === 'cost' ? formatCost(store.totals?.total_output_cost) : outputTokensDisplay.value)
const totalDisplay = computed(() => totalMetric.value === 'cost' ? formatCost(store.totals?.total_cost) : totalTokensDisplay.value)
</script>

<style scoped>
.stat-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: var(--spacing-md);
}

.stat-card {
  background: var(--color-bg-secondary);
  border-radius: var(--radius-xl);
  padding: var(--spacing-lg) var(--spacing-lg) var(--spacing-md);
  box-shadow: var(--shadow-sm);
  display: flex;
  flex-direction: column;
  transition: transform var(--transition-ease-out), box-shadow var(--transition-ease-out);
  cursor: default;
}

.stat-card-top {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 8px;
  margin-bottom: var(--spacing-sm);
}

.stat-card:hover {
  transform: translateY(-3px);
  box-shadow: var(--shadow-hover);
}

.stat-label {
  font-size: var(--font-size-xs);
  font-weight: var(--font-weight-semibold);
  color: var(--color-text-secondary);
  text-transform: uppercase;
  letter-spacing: 0.04em;
}

.metric-switcher {
  display: flex;
  background: var(--color-bg-tertiary);
  border-radius: var(--radius-md);
  padding: 2px;
  gap: 1px;
  flex-shrink: 0;
}

.metric-btn {
  border: none;
  background: transparent;
  padding: 3px 8px;
  font-size: var(--font-size-xs);
  font-weight: var(--font-weight-medium);
  color: var(--color-text-secondary);
  border-radius: calc(var(--radius-md) - 2px);
  cursor: pointer;
  transition: all var(--transition-fast);
  font-family: inherit;
  white-space: nowrap;
}

.metric-btn:hover {
  color: var(--color-text-primary);
}

.metric-btn.active {
  color: var(--color-accent);
  background: var(--color-bg-secondary);
  box-shadow: var(--shadow-sm);
}

.stat-value {
  font-size: var(--font-size-3xl);
  font-weight: var(--font-weight-bold);
  color: var(--color-text-primary);
  line-height: var(--line-height-tight);
  letter-spacing: var(--letter-spacing-tight);
  font-variant-numeric: tabular-nums;
}

.stat-value.is-accent {
  color: var(--color-accent);
}

@media (max-width: 800px) {
  .stat-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 480px) {
  .stat-grid {
    grid-template-columns: 1fr;
  }
}
</style>
