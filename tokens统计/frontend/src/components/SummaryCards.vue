<template>
  <div class="stat-grid">
    <div class="stat-card anim-card-enter" style="animation-delay: 0ms">
      <span class="stat-label">{{ loc.t.summary.totalInput }}</span>
      <span class="stat-value">{{ inputDisplay }}</span>
    </div>
    <div class="stat-card anim-card-enter" style="animation-delay: 60ms">
      <span class="stat-label">{{ loc.t.summary.totalOutput }}</span>
      <span class="stat-value">{{ outputDisplay }}</span>
    </div>
    <div class="stat-card anim-card-enter" style="animation-delay: 120ms">
      <span class="stat-label">{{ loc.t.summary.totalTokens }}</span>
      <span class="stat-value is-accent">{{ totalDisplay }}</span>
    </div>
    <div class="stat-card anim-card-enter" style="animation-delay: 180ms">
      <span class="stat-label">{{ loc.t.summary.recordCount }}</span>
      <span class="stat-value">{{ countDisplay }}</span>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useTokenRecordsStore } from '../stores/tokenRecords'
import { useLocaleStore } from '../stores/locale'
import { useCountUp } from '../composables/useCountUp'

const store = useTokenRecordsStore()
const loc = useLocaleStore()

const inputTarget = computed(() => store.totals?.total_input_tokens)
const outputTarget = computed(() => store.totals?.total_output_tokens)
const totalTarget = computed(() => store.totals?.total_tokens)
const countTarget = computed(() => store.totals?.record_count)

const inputDisplay = useCountUp(inputTarget)
const outputDisplay = useCountUp(outputTarget)
const totalDisplay = useCountUp(totalTarget)
const countDisplay = useCountUp(countTarget)
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
  margin-bottom: var(--spacing-sm);
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
