import axios from 'axios'
import { ElMessage } from 'element-plus'
import type { NotificationListResponse, Notification, UnreadCount } from '../types'
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
    const message = error.response?.data?.detail || error.message || 'Request failed'
    ElMessage.error(message)
    return Promise.reject(error)
  },
)

export function fetchNotifications(skip = 0, limit = 20): Promise<NotificationListResponse> {
  return api.get('/notifications', { params: { skip, limit } }).then((res) => res.data)
}

export function fetchUnreadCount(): Promise<UnreadCount> {
  return api.get('/notifications/unread-count').then((res) => res.data)
}

export function markNotificationRead(id: number): Promise<Notification> {
  return api.put(`/notifications/${id}/read`).then((res) => res.data)
}

export function markAllNotificationsRead(): Promise<{ ok: boolean }> {
  return api.put('/notifications/read-all').then((res) => res.data)
}
