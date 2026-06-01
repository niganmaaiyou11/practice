<template>
  <section class="leaderboard-preview">
    <div class="lb-header">
      <h2 class="section-title">{{ t.leaderboard?.topModels || 'Top AI Models' }}</h2>
      <router-link to="/leaderboard" class="view-all-link">
        {{ t.leaderboard?.viewAll || 'View Full Leaderboard' }} →
      </router-link>
    </div>

    <div v-if="store.topModels.length === 0" class="lb-empty">
      <p class="empty-msg">{{ t.leaderboard?.noData || 'No leaderboard data yet' }}</p>
      <p class="empty-hint">{{ t.leaderboard?.noDataHint || 'Click "Sync Data" to fetch rankings' }}</p>
    </div>

    <div v-else class="lb-cards">
      <div
        v-for="(m, i) in store.topModels"
        :key="m.id"
        class="lb-card"
        :class="{ 'lb-card--gold': i === 0, 'lb-card--silver': i === 1, 'lb-card--bronze': i === 2 }"
      >
        <span class="lb-rank" :class="`lb-rank--${medalClass(i)}`">{{ i + 1 }}</span>
        <ProviderIcon :provider="m.provider" :size="36" radius="10px" class="lb-avatar" />
        <div class="lb-info">
          <div class="lb-model-row">
            <span class="lb-model-name">{{ m.model_name }}</span>
            <span class="lb-provider" :style="{ color: providerColor(m.provider) }">
              {{ m.provider }}
            </span>
          </div>
          <div class="lb-meta">
            <span v-if="m.overall_score != null" class="lb-score">
              {{ m.overall_score > 1 ? m.overall_score.toFixed(1) : (m.overall_score * 100).toFixed(1) }}
            </span>
            <span v-if="m.tokens_per_second != null" class="lb-speed">
              {{ formatSpeed(m.tokens_per_second) }}
            </span>
            <span v-if="m.price_input != null" class="lb-price">
              ${{ fmtPrice(m.price_input) }}/M
            </span>
          </div>
        </div>
      </div>
    </div>
  </section>
</template>

<script setup lang="ts">
import { onMounted } from 'vue'
import { useLeaderboardStore } from '../stores/leaderboard'
import { useLocaleStore } from '../stores/locale'
import { useModelsStore } from '../stores/models'
import ProviderIcon from './ProviderIcon.vue'

const store = useLeaderboardStore()
const t = useLocaleStore().t
const modelsStore = useModelsStore()

function medalClass(i: number): string {
  if (i === 0) return 'gold'
  if (i === 1) return 'silver'
  if (i === 2) return 'bronze'
  return ''
}

function providerColor(provider: string): string {
  return modelsStore.providerColors[provider] || '#999'
}

function formatSpeed(tps: number): string {
  if (tps >= 1000) return (tps / 1000).toFixed(1) + 'K t/s'
  return tps.toFixed(0) + ' t/s'
}

function fmtPrice(p: number): string {
  if (p < 1) return p.toFixed(2)
  return p.toFixed(1)
}

onMounted(() => {
  store.fetchTopModels(5)
})
</script>

<style scoped>
.leaderboard-preview {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-md);
}

.lb-header {
  display: flex;
  align-items: baseline;
  justify-content: space-between;
}

.section-title {
  font-size: var(--font-size-xl);
  font-weight: var(--font-weight-semibold);
  color: var(--color-text-primary);
  letter-spacing: var(--letter-spacing-tight);
}

.view-all-link {
  font-size: var(--font-size-sm);
  font-weight: var(--font-weight-medium);
  color: var(--color-accent);
  text-decoration: none;
  transition: opacity var(--transition-fast);
}

.view-all-link:hover {
  opacity: 0.7;
}

.lb-empty {
  background: var(--color-bg-tertiary);
  border-radius: var(--radius-xl);
  padding: var(--spacing-xl);
  text-align: center;
}

.empty-msg {
  font-size: var(--font-size-sm);
  color: var(--color-text-secondary);
  margin-bottom: var(--spacing-xs);
}

.empty-hint {
  font-size: var(--font-size-xs);
  color: var(--color-text-tertiary);
}

.lb-cards {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.lb-card {
  display: flex;
  align-items: center;
  gap: var(--spacing-md);
  padding: var(--spacing-sm) var(--spacing-md);
  background: var(--color-bg-secondary);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-sm);
  transition: transform var(--transition-fast), box-shadow var(--transition-fast);
}

.lb-card:hover {
  transform: translateX(4px);
  box-shadow: var(--shadow-hover);
}

.lb-rank {
  flex-shrink: 0;
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  font-size: var(--font-size-sm);
  font-weight: var(--font-weight-bold);
  color: var(--color-text-secondary);
  background: var(--color-bg-tertiary);
}

.lb-rank--gold {
  background: linear-gradient(135deg, #ffd700, #ffb800);
  color: #7c5e00;
}

.lb-rank--silver {
  background: linear-gradient(135deg, #c0c0c0, #a8a8a8);
  color: #4a4a4a;
}

.lb-rank--bronze {
  background: linear-gradient(135deg, #cd7f32, #b8722e);
  color: #4a2a0a;
}

/* Provider Avatar */
.lb-avatar {
  flex-shrink: 0;
  width: 36px;
  height: 36px;
  border-radius: var(--radius-md);
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 2px 8px rgba(0,0,0,0.12);
}

.lb-avatar__text {
  font-size: 14px;
  font-weight: var(--font-weight-bold);
  color: #fff;
  letter-spacing: 0;
  text-shadow: 0 1px 2px rgba(0,0,0,0.15);
}

.lb-info {
  flex: 1;
  min-width: 0;
}

.lb-model-row {
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
  margin-bottom: 2px;
}

.lb-model-name {
  font-size: var(--font-size-sm);
  font-weight: var(--font-weight-semibold);
  color: var(--color-text-primary);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.lb-provider {
  font-size: var(--font-size-xs);
  font-weight: var(--font-weight-medium);
  white-space: nowrap;
  text-transform: uppercase;
  letter-spacing: 0.04em;
  flex-shrink: 0;
}

.lb-meta {
  display: flex;
  gap: var(--spacing-md);
  font-size: var(--font-size-xs);
  color: var(--color-text-tertiary);
}

.lb-score {
  color: var(--color-accent);
  font-weight: var(--font-weight-semibold);
}

.lb-speed {
  color: var(--color-text-secondary);
}

.lb-price {
  color: var(--color-text-tertiary);
}
</style>
