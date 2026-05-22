<template>
  <div>
    <div class="page-header">
      <h2>{{ loc.t.records.title }}</h2>
    </div>
    <div class="card">
      <FilterBar @apply="onFilter" @reset="onFilter" />
    </div>
    <div class="card" style="margin-top: var(--spacing-md)">
      <RecordTable />
    </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted } from 'vue'
import { useTokenRecordsStore } from '../stores/tokenRecords'
import { useLocaleStore } from '../stores/locale'
import FilterBar from '../components/FilterBar.vue'
import RecordTable from '../components/RecordTable.vue'

const store = useTokenRecordsStore()
const loc = useLocaleStore()

onMounted(() => {
  store.fetchRecords()
})

function onFilter() {
  store.pagination.skip = 0
  store.fetchRecords()
}
</script>

<style scoped>
.card {
  background: var(--color-bg-secondary);
  border-radius: var(--radius-xl);
  padding: var(--spacing-md) var(--spacing-lg);
  box-shadow: var(--shadow-sm);
}
</style>
