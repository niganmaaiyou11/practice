<template>
  <div class="filter-bar">
    <el-date-picker
      v-model="dateRange"
      type="daterange"
      :shortcuts="shortcuts"
      :range-separator="loc.t.filter.to"
      :start-placeholder="loc.t.filter.startDate"
      :end-placeholder="loc.t.filter.endDate"
      format="YYYY-MM-DD"
      value-format="YYYY-MM-DD"
      class="filter-date"
      @change="onDateChange"
    />
    <el-select
      v-model="provider"
      :placeholder="loc.t.filter.provider"
      clearable
      class="filter-provider"
    >
      <el-option
        v-for="p in providers"
        :key="p"
        :label="p"
        :value="p"
      />
    </el-select>
    <el-button type="primary" @click="apply">{{ loc.t.filter.apply }}</el-button>
    <el-button @click="reset">{{ loc.t.filter.reset }}</el-button>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { ElMessage } from 'element-plus'
import { useTokenRecordsStore } from '../stores/tokenRecords'
import { useLocaleStore } from '../stores/locale'
import { useModelsStore } from '../stores/models'

const store = useTokenRecordsStore()
const loc = useLocaleStore()
const modelsStore = useModelsStore()
const emit = defineEmits<{
  (e: 'apply'): void
  (e: 'reset'): void
}>()

function todayStr(): string {
  const d = new Date()
  const y = d.getFullYear()
  const m = String(d.getMonth() + 1).padStart(2, '0')
  const day = String(d.getDate()).padStart(2, '0')
  return `${y}-${m}-${day}`
}

function firstOfMonthStr(): string {
  const d = new Date()
  const y = d.getFullYear()
  const m = String(d.getMonth() + 1).padStart(2, '0')
  return `${y}-${m}-01`
}

const shortcuts = computed(() => {
  const t = new Date()
  const td = (d: number) => {
    const r = new Date(t)
    r.setDate(r.getDate() - d)
    return `${r.getFullYear()}-${String(r.getMonth() + 1).padStart(2, '0')}-${String(r.getDate()).padStart(2, '0')}`
  }
  return [
    { text: `3 ${loc.t.filter.days}`, value: () => [td(3), todayStr()] },
    { text: `7 ${loc.t.filter.days}`, value: () => [td(7), todayStr()] },
    { text: `30 ${loc.t.filter.days}`, value: () => [td(30), todayStr()] },
    { text: `90 ${loc.t.filter.days}`, value: () => [td(90), todayStr()] },
    { text: `360 ${loc.t.filter.days}`, value: () => [td(360), todayStr()] },
  ]
})

const providers = computed(() => modelsStore.providerNames)

const dateRange = ref<[string, string] | null>([
  firstOfMonthStr(),
  todayStr(),
])
const provider = ref<string | undefined>(store.filters.provider)
let isResetting = false

function daysBetween(a: string, b: string): number {
  return (new Date(b + 'T00:00:00').getTime() - new Date(a + 'T00:00:00').getTime()) / 86400000
}

function onDateChange() {
  if (isResetting) return
  const s = dateRange.value?.[0]
  const e = dateRange.value?.[1]
  if (s && e) apply()
}

function apply() {
  const s = dateRange.value?.[0]
  const e = dateRange.value?.[1]
  if (s && e && daysBetween(s, e) > 365) {
    ElMessage.warning(loc.t.filter.maxRange || 'Date range cannot exceed 365 days')
    return
  }
  store.setFilter('start_date', s)
  store.setFilter('end_date', e)
  store.setFilter('provider', provider.value || undefined)
  emit('apply')
}

function reset() {
  isResetting = true
  dateRange.value = [firstOfMonthStr(), todayStr()]
  isResetting = false
  provider.value = undefined
  store.resetFilters()
  emit('reset')
}
</script>

<style scoped>
.filter-bar {
  display: flex;
  align-items: center;
  gap: 12px;
  flex-wrap: wrap;
}

.filter-date {
  width: 280px;
}

.filter-provider {
  width: 160px;
}
</style>
