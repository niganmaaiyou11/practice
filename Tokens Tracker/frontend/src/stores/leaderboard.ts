import { defineStore } from 'pinia'
import { ref, reactive } from 'vue'
import type {
  LeaderboardEntry,
  LeaderboardSummary,
  LeaderboardQueryParams,
} from '../types'
import * as api from '../api/leaderboard'

export const useLeaderboardStore = defineStore('leaderboard', () => {
  const entries = ref<LeaderboardEntry[]>([])
  const total = ref(0)
  const topModels = ref<LeaderboardEntry[]>([])
  const summary = ref<LeaderboardSummary | null>(null)
  const providers = ref<string[]>([])
  const loading = ref(false)
  const syncing = ref(false)

  const filters = reactive<LeaderboardQueryParams>({
    provider: undefined,
    search: undefined,
    sort_by: 'overall_score',
    sort_dir: 'desc',
    china_only: false,
    tags: undefined,
    modality: 'text',
  })
  const pagination = reactive({ skip: 0, limit: 20 })

  async function fetchEntries() {
    loading.value = true
    try {
      const res = await api.fetchLeaderboardModels({
        ...filters,
        skip: pagination.skip,
        limit: pagination.limit,
      })
      entries.value = res.entries
      total.value = res.total
    } finally {
      loading.value = false
    }
  }

  async function fetchTopModels(limit = 5) {
    topModels.value = await api.fetchLeaderboardTop(limit, filters.modality)
  }

  async function fetchSummary() {
    summary.value = await api.fetchLeaderboardSummary(filters.modality)
  }

  async function fetchProviders() {
    providers.value = await api.fetchLeaderboardProviders()
  }

  async function triggerSync(): Promise<{ ok: boolean; output: string; models?: number; providers?: number; last_fetched_at?: string | null; source?: string | null }> {
    syncing.value = true
    try {
      const result = await api.triggerLeaderboardSync()
      if (result.ok) {
        await Promise.all([fetchEntries(), fetchSummary(), fetchProviders(), fetchTopModels()])
      }
      return result
    } finally {
      syncing.value = false
    }
  }

  function setFilter(key: keyof LeaderboardQueryParams, value: string | undefined) {
    ;(filters as any)[key] = value
    pagination.skip = 0
  }

  function resetFilters() {
    filters.provider = undefined
    filters.search = undefined
    filters.sort_by = 'overall_score'
    filters.sort_dir = 'desc'
    filters.china_only = false
    filters.modality = undefined
    pagination.skip = 0
  }

  return {
    entries,
    total,
    topModels,
    summary,
    providers,
    loading,
    syncing,
    filters,
    pagination,
    fetchEntries,
    fetchTopModels,
    fetchSummary,
    fetchProviders,
    triggerSync,
    setFilter,
    resetFilters,
  }
})
