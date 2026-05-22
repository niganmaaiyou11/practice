<template>
  <div class="carousel-container">
    <div v-if="displayCards.length === 0" class="carousel-empty">
      <p>{{ t.home?.noRecords || 'No records yet. Start tracking!' }}</p>
    </div>
    <div v-else class="carousel-viewport" @mouseenter="paused = true" @mouseleave="paused = false">
      <div
        class="carousel-track"
        :class="{ paused }"
        :style="{ '--scroll-duration': scrollDuration + 's' }"
      >
        <div
          v-for="(record, i) in displayCards"
          :key="i"
          class="carousel-card"
        >
          <div class="card-header">
            <span class="provider-dot" :style="{ background: getColor(record.provider) }" />
            <span class="provider-name">{{ record.provider }}</span>
          </div>
          <p class="card-model">{{ record.model_name }}</p>
          <div class="card-tokens">
            <span class="token-count">{{ formatNum(record.total_tokens) }}</span>
            <span class="token-unit">tokens</span>
          </div>
          <p class="card-date">{{ record.date }}</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'
import { useModelsStore } from '../stores/models'
import { useLocaleStore } from '../stores/locale'
import type { TokenUsage } from '../types'

const props = defineProps<{
  records: TokenUsage[]
}>()

const modelsStore = useModelsStore()
const localeStore = useLocaleStore()
const t = localeStore.t

const paused = ref(false)

const displayCards = computed(() => {
  if (props.records.length === 0) return []
  const dup = [...props.records, ...props.records]
  while (dup.length < 10) {
    dup.push(...props.records)
  }
  return dup
})

const scrollDuration = computed(() => {
  const base = props.records.length * 3
  return Math.max(base, 20)
})

function getColor(provider: string): string {
  return modelsStore.providerColors[provider] || '#999'
}

function formatNum(n: number): string {
  if (n >= 1_000_000) return (n / 1_000_000).toFixed(1) + 'M'
  if (n >= 1_000) return (n / 1_000).toFixed(1) + 'K'
  return n.toLocaleString()
}
</script>

<style scoped>
.carousel-container {
  overflow: hidden;
}

.carousel-empty {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 140px;
  color: var(--color-text-secondary);
  font-size: var(--font-size-sm);
  background: var(--color-bg-tertiary);
  border-radius: var(--radius-xl);
}

.carousel-viewport {
  overflow: hidden;
  mask-image: linear-gradient(
    to right,
    transparent 0%,
    black 5%,
    black 95%,
    transparent 100%
  );
  -webkit-mask-image: linear-gradient(
    to right,
    transparent 0%,
    black 5%,
    black 95%,
    transparent 100%
  );
}

.carousel-track {
  display: flex;
  gap: var(--spacing-md);
  width: max-content;
  animation: scroll-announcements var(--scroll-duration) linear infinite;
  padding: var(--spacing-xs) 0;
}

.carousel-track.paused {
  animation-play-state: paused;
}

@keyframes scroll-announcements {
  0% {
    transform: translateX(0);
  }
  100% {
    transform: translateX(-50%);
  }
}

.carousel-card {
  flex-shrink: 0;
  width: 220px;
  padding: var(--spacing-md) var(--spacing-lg);
  background: var(--color-bg-secondary);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-xl);
  box-shadow: var(--shadow-sm);
  transition: transform var(--transition-smooth), box-shadow var(--transition-smooth);
  cursor: default;
}

.carousel-card:hover {
  transform: translateY(-4px);
  box-shadow: var(--shadow-hover);
}

.card-header {
  display: flex;
  align-items: center;
  gap: 6px;
  margin-bottom: var(--spacing-xs);
}

.provider-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  flex-shrink: 0;
}

.provider-name {
  font-size: var(--font-size-xs);
  font-weight: var(--font-weight-medium);
  color: var(--color-text-secondary);
  text-transform: uppercase;
  letter-spacing: 0.04em;
}

.card-model {
  font-size: var(--font-size-sm);
  font-weight: var(--font-weight-semibold);
  color: var(--color-text-primary);
  margin-bottom: var(--spacing-sm);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.card-tokens {
  display: flex;
  align-items: baseline;
  gap: 4px;
  margin-bottom: var(--spacing-xs);
}

.token-count {
  font-size: var(--font-size-xl);
  font-weight: var(--font-weight-bold);
  color: var(--color-accent);
  letter-spacing: var(--letter-spacing-tight);
  font-variant-numeric: tabular-nums;
}

.token-unit {
  font-size: var(--font-size-xs);
  color: var(--color-text-secondary);
}

.card-date {
  font-size: var(--font-size-xs);
  color: var(--color-text-tertiary);
}

@media (max-width: 768px) {
  .carousel-card {
    width: 180px;
    padding: var(--spacing-sm) var(--spacing-md);
  }
}
</style>
