import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import * as authApi from '../api/auth'
import type { User } from '../types'

export const useAuthStore = defineStore('auth', () => {
  const user = ref<User | null>(null)
  const accessToken = ref<string | null>(null)
  const refreshToken = ref<string | null>(localStorage.getItem('refreshToken'))
  const initialized = ref(false)

  const isAuthenticated = computed(() => !!accessToken.value)

  async function init() {
    if (initialized.value) return
    initialized.value = true

    if (refreshToken.value) {
      try {
        const tokens = await authApi.refreshToken(refreshToken.value)
        accessToken.value = tokens.access_token
        refreshToken.value = tokens.refresh_token
        localStorage.setItem('refreshToken', tokens.refresh_token)

        const me = await authApi.fetchMe()
        user.value = me
      } catch {
        doLogout()
      }
    }
  }

  async function doLogin(email: string, password: string, captchaToken: string) {
    const tokens = await authApi.login({ email, password, captcha_token: captchaToken })
    accessToken.value = tokens.access_token
    refreshToken.value = tokens.refresh_token
    localStorage.setItem('refreshToken', tokens.refresh_token)

    const me = await authApi.fetchMe()
    user.value = me
  }

  async function doRegister(email: string, password: string, captchaToken: string) {
    const tokens = await authApi.register({ email, password, captcha_token: captchaToken })
    accessToken.value = tokens.access_token
    refreshToken.value = tokens.refresh_token
    localStorage.setItem('refreshToken', tokens.refresh_token)

    const me = await authApi.fetchMe()
    user.value = me
  }

  async function doRefresh() {
    if (!refreshToken.value) throw new Error('No refresh token')
    const tokens = await authApi.refreshToken(refreshToken.value)
    accessToken.value = tokens.access_token
    refreshToken.value = tokens.refresh_token
    localStorage.setItem('refreshToken', tokens.refresh_token)
  }

  function doLogout() {
    user.value = null
    accessToken.value = null
    refreshToken.value = null
    localStorage.removeItem('refreshToken')
  }

  async function fetchCaptcha(): Promise<string> {
    const data = await authApi.fetchCaptcha()
    return data.token
  }

  return {
    user,
    accessToken,
    refreshToken,
    initialized,
    isAuthenticated,
    init,
    doLogin,
    doRegister,
    doRefresh,
    doLogout,
    fetchCaptcha,
  }
})
