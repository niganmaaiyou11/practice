import { defineStore } from 'pinia'
import { ref, reactive } from 'vue'
import type {
  TokenUsage,
  TokenUsageCreate,
  TokenUsageUpdate,
  DailySummary,
  ModelBreakdown,
  ProviderBreakdown,
  Totals,
  FilterParams,
} from '../types'
import * as api from '../api/tokenRecords'

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

function fillDailyGaps(rows: DailySummary[], start: string, end: string): DailySummary[] {
  const map = new Map<string, DailySummary>()
  for (const r of rows) {
    map.set(r.date, r)
  }
  const result: DailySummary[] = []
  const cursor = new Date(start + 'T00:00:00')
  const endDate = new Date(end + 'T00:00:00')
  while (cursor <= endDate) {
    const y = cursor.getFullYear()
    const m = String(cursor.getMonth() + 1).padStart(2, '0')
    const d = String(cursor.getDate()).padStart(2, '0')
    const key = `${y}-${m}-${d}`
    const existing = map.get(key)
    result.push(existing ?? { date: key, total_input_tokens: 0, total_output_tokens: 0, total_tokens: 0, record_count: 0, total_input_cost: 0, total_output_cost: 0, total_cost: 0 })
    cursor.setDate(cursor.getDate() + 1)
  }
  return result
}

export const useTokenRecordsStore = defineStore('tokenRecords', () => {
  const records = ref<TokenUsage[]>([])
  const total = ref(0)
  const dailySummary = ref<DailySummary[]>([])
  const modelBreakdown = ref<ModelBreakdown[]>([])
  const providerBreakdown = ref<ProviderBreakdown[]>([])
  const totals = ref<Totals | null>(null)
  const currentRecord = ref<TokenUsage | null>(null)
  const loading = ref(false)
  const filters = reactive<FilterParams>({
    start_date: firstOfMonthStr(),
    end_date: todayStr(),
    provider: undefined,
  })
  const pagination = reactive({ skip: 0, limit: 20 })

  async function fetchRecords() {
    loading.value = true
    try {
      const res = await api.fetchRecords({
        ...filters,
        skip: pagination.skip,
        limit: pagination.limit,
      })
      records.value = res.records
      total.value = res.total
    } finally {
      loading.value = false
    }
  }

  async function fetchRecordById(id: number) {
    loading.value = true
    try {
      currentRecord.value = await api.fetchRecordById(id)
    } finally {
      loading.value = false
    }
  }

  async function createRecord(data: TokenUsageCreate) {
    await api.createRecord(data)
    await fetchRecords()
  }

  async function updateRecord(id: number, data: TokenUsageUpdate) {
    await api.updateRecord(id, data)
    await fetchRecords()
  }

  async function deleteRecord(id: number) {
    await api.deleteRecord(id)
    await fetchRecords()
  }

  async function fetchDailySummary() {
    const data = await api.fetchDailySummary(filters)
    const start = filters.start_date || firstOfMonthStr()
    const end = filters.end_date || todayStr()
    dailySummary.value = fillDailyGaps(data, start, end)
  }

  async function fetchModelBreakdown() {
    const data = await api.fetchModelBreakdown(filters)
    modelBreakdown.value = data
  }

  async function fetchProviderBreakdown() {
    const data = await api.fetchProviderBreakdown(filters)
    providerBreakdown.value = data
  }

  async function fetchTotals() {
    totals.value = await api.fetchTotals(filters)
  }

  function setFilter(key: keyof FilterParams, value: string | undefined) {
    filters[key] = value as any
  }

  function resetFilters() {
    filters.start_date = firstOfMonthStr()
    filters.end_date = todayStr()
    filters.provider = undefined
  }

  return {
    records,
    total,
    dailySummary,
    modelBreakdown,
    providerBreakdown,
    totals,
    currentRecord,
    loading,
    filters,
    pagination,
    fetchRecords,
    fetchRecordById,
    createRecord,
    updateRecord,
    deleteRecord,
    fetchDailySummary,
    fetchModelBreakdown,
    fetchProviderBreakdown,
    fetchTotals,
    setFilter,
    resetFilters,
  }
})
