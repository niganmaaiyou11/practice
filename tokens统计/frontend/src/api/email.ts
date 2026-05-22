import axios from 'axios'
import { ElMessage } from 'element-plus'
import type {
  EmailAccount, EmailAccountCreate, EmailAccountUpdate,
  SyncResult, PaginatedSyncLogs, SyncStatus, OAuthURL, IMAPTestRequest, IMAPTestResponse,
  PreviewResponse,
} from '../types'
import { useLocaleStore } from '../stores/locale'
import { useAuthStore } from '../stores/auth'

const api = axios.create({ baseURL: '/api', timeout: 30000 })

api.interceptors.request.use((config) => {
  const authStore = useAuthStore()
  if (authStore.accessToken) {
    config.headers.Authorization = `Bearer ${authStore.accessToken}`
  }
  return config
})

api.interceptors.response.use(
  (res) => res,
  (error) => {
    const loc = useLocaleStore()
    ElMessage.error(error.response?.data?.detail || error.message || loc.t.messages.requestFailed)
    return Promise.reject(error)
  },
)

export function fetchOAuthUrl(): Promise<OAuthURL> {
  return api.get('/email/oauth-url').then((res) => res.data)
}

export function fetchAccounts(): Promise<EmailAccount[]> {
  return api.get('/email/accounts').then((res) => res.data)
}

export function createAccount(data: EmailAccountCreate): Promise<EmailAccount> {
  return api.post('/email/accounts', data).then((res) => res.data)
}

export function updateAccount(id: number, data: EmailAccountUpdate): Promise<EmailAccount> {
  return api.put(`/email/accounts/${id}`, data).then((res) => res.data)
}

export function deleteAccount(id: number): Promise<void> {
  return api.delete(`/email/accounts/${id}`)
}

export function triggerSync(accountId: number): Promise<SyncResult> {
  return api.post(`/email/accounts/${accountId}/sync`, null, { timeout: 120000 }).then((res) => res.data)
}

export function fetchSyncLogs(params: {
  skip?: number; limit?: number; account_id?: number
}): Promise<PaginatedSyncLogs> {
  return api.get('/email/sync-logs', { params }).then((res) => res.data)
}

export function fetchSyncStatus(): Promise<SyncStatus> {
  return api.get('/email/sync-status').then((res) => res.data)
}

export function previewSync(accountId: number): Promise<PreviewResponse> {
  return api.post(`/email/accounts/${accountId}/preview`, null, { timeout: 120000 }).then((res) => res.data)
}

export function testIMAP(data: IMAPTestRequest): Promise<IMAPTestResponse> {
  return api.post('/email/test-imap', data).then((res) => res.data)
}
