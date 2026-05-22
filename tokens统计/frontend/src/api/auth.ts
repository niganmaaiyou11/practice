import axios from 'axios'
import { ElMessage } from 'element-plus'
import { useAuthStore } from '../stores/auth'
import type { TokenResponse, User, LoginRequest, RegisterRequest, CaptchaChallenge } from '../types'

const authApi = axios.create({
  baseURL: '/api/auth',
  timeout: 10000,
})

authApi.interceptors.request.use((config) => {
  const authStore = useAuthStore()
  if (authStore.accessToken) {
    config.headers.Authorization = `Bearer ${authStore.accessToken}`
  }
  return config
})

authApi.interceptors.response.use(
  (response) => response,
  (error) => {
    const message = error.response?.data?.detail || error.message || 'Request failed'
    ElMessage.error(message)
    return Promise.reject(error)
  },
)

export function fetchCaptcha(): Promise<CaptchaChallenge> {
  return authApi.get('/captcha').then((r) => r.data)
}

export function register(data: RegisterRequest): Promise<TokenResponse> {
  return authApi.post('/register', data).then((r) => r.data)
}

export function login(data: LoginRequest): Promise<TokenResponse> {
  return authApi.post('/login', data).then((r) => r.data)
}

export function refreshToken(token: string): Promise<TokenResponse> {
  return authApi.post('/refresh', { refresh_token: token }).then((r) => r.data)
}

export function fetchMe(): Promise<User> {
  return authApi.get('/me').then((r) => r.data)
}
