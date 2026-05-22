<template>
  <div>
    <div class="page-header">
      <h2>{{ loc.t.dashboard.title }}</h2>
    </div>

    <SummaryCards />

    <div class="filter-card anim-fade-up" style="animation-delay: 240ms">
      <FilterBar @apply="onFilter" @reset="onFilter" />
    </div>

    <div class="charts-grid">
      <DailyTrendChart />
      <ModelBreakdownChart />
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

.charts-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: var(--spacing-md);
  margin-top: var(--spacing-md);
}

@media (max-width: 900px) {
  .charts-grid {
    grid-template-columns: 1fr;
  }
}
</style>
