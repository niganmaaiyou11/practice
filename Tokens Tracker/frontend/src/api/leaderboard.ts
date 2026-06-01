import axios from 'axios'
import { ElMessage } from 'element-plus'
import type {
  LeaderboardEntry,
  LeaderboardPaginatedResponse,
  LeaderboardSummary,
  LeaderboardQueryParams,
} from '../types'
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

let isRefreshing = false
let pendingRequests: Array<{
  resolve: (token: string) => void
  reject: (err: unknown) => void
}> = []

api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const authStore = useAuthStore()
    const originalRequest = error.config

    if (error.response?.status === 401 && !originalRequest._retry) {
      if (isRefreshing) {
        return new Promise<string>((resolve, reject) => {
          pendingRequests.push({ resolve, reject })
        }).then((token) => {
          originalRequest.headers.Authorization = `Bearer ${token}`
          return api(originalRequest)
        })
      }

      originalRequest._retry = true
      isRefreshing = true

      try {
        await authStore.doRefresh()
        const newToken = authStore.accessToken
        pendingRequests.forEach(({ resolve }) => resolve(newToken!))
        pendingRequests = []
        originalRequest.headers.Authorization = `Bearer ${newToken}`
        return api(originalRequest)
      } catch (refreshError) {
        pendingRequests.forEach(({ reject }) => reject(refreshError))
        pendingRequests = []
        authStore.doLogout()
        return Promise.reject(refreshError)
      } finally {
        isRefreshing = false
      }
    }

    const loc = useLocaleStore()
    const fallback = loc.t.messages.requestFailed
    const message = error.response?.data?.detail || error.message || fallback
    ElMessage.error(message)
    return Promise.reject(error)
  },
)

export function fetchLeaderboardModels(params: LeaderboardQueryParams): Promise<LeaderboardPaginatedResponse> {
  return api.get('/leaderboard/models', { params }).then((res) => res.data)
}

export function fetchLeaderboardTop(limit = 5, modality?: string): Promise<LeaderboardEntry[]> {
  return api.get('/leaderboard/top', { params: { limit, ...(modality ? { modality } : {}) } }).then((res) => res.data)
}

export function fetchLeaderboardSummary(modality?: string): Promise<LeaderboardSummary> {
  return api.get('/leaderboard/summary', { params: modality ? { modality } : {} }).then((res) => res.data)
}

export function fetchLeaderboardProviders(): Promise<string[]> {
  return api.get('/leaderboard/providers').then((res) => res.data)
}

type LeaderboardSyncResult = {
  ok: boolean
  output: string
  models?: number
  providers?: number
  last_fetched_at?: string | null
  source?: string | null
}

export function triggerLeaderboardSync(): Promise<LeaderboardSyncResult> {
  return api.post('/leaderboard/sync').then((res) => res.data)
}
