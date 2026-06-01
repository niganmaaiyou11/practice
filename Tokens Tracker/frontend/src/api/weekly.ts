import axios from 'axios'
import { ElMessage } from 'element-plus'
import type { WeeklyItem, WeeklyResponse } from '../types'
import { useLocaleStore } from '../stores/locale'
import { useAuthStore } from '../stores/auth'

const api = axios.create({
  baseURL: '/api',
  timeout: 15000,
})

api.interceptors.request.use((config) => {
  const authStore = useAuthStore()
  if (authStore.accessToken) {
    config.headers.Authorization = `Bearer ${authStore.accessToken}`
  }
  return config
})

api.interceptors.response.use(
  (response) => response,
  (error) => {
    const loc = useLocaleStore()
    const fallback = loc.t.messages.requestFailed
    const message = error.response?.data?.detail || error.message || fallback
    ElMessage.error(message)
    return Promise.reject(error)
  },
)

export function fetchWeekly(): Promise<WeeklyResponse> {
  return api.get('/weekly').then((res) => res.data)
}

export function fetchWeeklyItem(slug: string): Promise<WeeklyItem> {
  return api.get(`/weekly/${slug}`).then((res) => res.data)
}

export function triggerWeeklyRefresh(): Promise<{
  ok: boolean
  new_items: number
  sources_ok: number
  sources_failed: number
  total_fetched: number
}> {
  return api.post('/weekly/refresh').then((res) => res.data)
}

export interface FeedSourceStatus {
  name: string
  url: string
  ok: boolean
  items_count: number
  error: string
  fetched_at: string | null
}

export interface WeeklyStatusResponse {
  last_refresh_at: string | null
  last_refresh_count: number
  sources: FeedSourceStatus[]
}

export function fetchWeeklyStatus(): Promise<WeeklyStatusResponse> {
  return api.get('/weekly-status').then((res) => res.data)
}
