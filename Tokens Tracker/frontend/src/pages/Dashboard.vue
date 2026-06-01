<template>
  <div>
    <div class="page-header">
      <h2>{{ loc.t.dashboard.title }}</h2>
    </div>

    <SummaryCards />

    <div class="filter-card anim-fade-up" style="animation-delay: 240ms">
      <FilterBar @apply="onFilter" @reset="onFilter" />
    </div>

    <section class="weekly-card anim-fade-up" style="animation-delay: 300ms">
      <div>
        <span class="weekly-eyebrow">AI Weekly</span>
        <h3>本周 AI 动态</h3>
        <p>查看模型发布、开源项目、AI 工具和国内 AI 的精选周报。</p>
      </div>
      <router-link to="/weekly" class="weekly-link">查看周报</router-link>
    </section>

    <div class="charts-grid">
      <DailyTrendChart />
      <ModelBreakdownChart />
      <ProviderBreakdownChart />
    </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted } from 'vue'
import { useTokenRecordsStore } from '../stores/tokenRecords'
import { useLocaleStore } from '../stores/locale'
import SummaryCards from '../components/SummaryCards.vue'
import FilterBar from '../components/FilterBar.vue'
import DailyTrendChart from '../components/DailyTrendChart.vue'
import ModelBreakdownChart from '../components/ModelBreakdownChart.vue'
import ProviderBreakdownChart from '../components/ProviderBreakdownChart.vue'

const store = useTokenRecordsStore()
const loc = useLocaleStore()

onMounted(() => {
  refreshAll()
})

function refreshAll() {
  store.fetchTotals()
  store.fetchDailySummary()
  store.fetchModelBreakdown()
  store.fetchProviderBreakdown()
}

function onFilter() {
  refreshAll()
}
</script>

<style scoped>
.filter-card {
  background: var(--color-bg-secondary);
  border-radius: var(--radius-xl);
  padding: var(--spacing-md) var(--spacing-lg);
  box-shadow: var(--shadow-sm);
  margin-top: var(--spacing-md);
}

.weekly-card {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: var(--spacing-lg);
  background: var(--color-bg-secondary);
  border-radius: var(--radius-xl);
  padding: var(--spacing-lg);
  box-shadow: var(--shadow-sm);
  margin-top: var(--spacing-md);
}

.weekly-eyebrow {
  display: inline-block;
  color: var(--color-accent);
  font-size: var(--font-size-xs);
  font-weight: var(--font-weight-semibold);
  text-transform: uppercase;
  letter-spacing: 0.08em;
  margin-bottom: var(--spacing-xs);
}

.weekly-card h3 {
  color: var(--color-text-primary);
  margin-bottom: var(--spacing-xs);
}

.weekly-card p {
  color: var(--color-text-secondary);
}

.weekly-link {
  flex-shrink: 0;
  color: var(--color-accent);
  font-weight: var(--font-weight-semibold);
  text-decoration: none;
}

.charts-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: var(--spacing-md);
  margin-top: var(--spacing-md);
}

.charts-grid > :nth-child(3) {
  grid-column: 1 / -1;
}

@media (max-width: 900px) {
  .weekly-card {
    align-items: flex-start;
    flex-direction: column;
  }

  .charts-grid {
    grid-template-columns: 1fr;
  }

  .charts-grid > :nth-child(3) {
    grid-column: auto;
  }
}
</style>
