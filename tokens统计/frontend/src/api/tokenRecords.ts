import axios from 'axios'
import { ElMessage } from 'element-plus'
import type {
  TokenUsage,
  TokenUsageCreate,
  TokenUsageUpdate,
  PaginatedResponse,
  DailySummary,
  ModelBreakdown,
  ProviderBreakdown,
  Totals,
  RecordQueryParams,
  FilterParams,
} from '../types'
import { useLocaleStore } from '../stores/locale'
import { useAuthStore } from '../stores/auth'

const api = axios.create({
  baseURL: '/api',
  timeout: 10000,
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

export function fetchRecords(params: RecordQueryParams): Promise<PaginatedResponse> {
  return api.get('/records', { params }).then((res) => res.data)
}

export function fetchRecordById(id: number): Promise<TokenUsage> {
  return api.get(`/records/${id}`).then((res) => res.data)
}

export function createRecord(data: TokenUsageCreate): Promise<TokenUsage> {
  return api.post('/records', data).then((res) => res.data)
}

export function updateRecord(id: number, data: TokenUsageUpdate): Promise<TokenUsage> {
  return api.put(`/records/${id}`, data).then((res) => res.data)
}

export function deleteRecord(id: number): Promise<void> {
  return api.delete(`/records/${id}`)
}

export function fetchDailySummary(params: FilterParams): Promise<DailySummary[]> {
  return api.get('/summary/daily', { params }).then((res) => res.data)
}

export function fetchModelBreakdown(params: FilterParams): Promise<ModelBreakdown[]> {
  return api.get('/summary/by-model', { params }).then((res) => res.data)
}

export function fetchProviderBreakdown(params: FilterParams): Promise<ProviderBreakdown[]> {
  return api.get('/summary/by-provider', { params }).then((res) => res.data)
}

export function fetchTotals(params: FilterParams): Promise<Totals> {
  return api.get('/summary/totals', { params }).then((res) => res.data)
}
