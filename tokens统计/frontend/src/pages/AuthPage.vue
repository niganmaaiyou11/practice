<template>
  <div class="auth-page">
    <div class="auth-card">
      <div class="auth-card__header">
        <h1 class="auth-logo">{{ localeStore.t.app.title }}</h1>
        <div class="auth-tabs">
          <button
            class="auth-tab"
            :class="{ active: tab === 'login' }"
            @click="switchTab('login')"
          >
            {{ localeStore.t.auth?.login || 'Sign In' }}
          </button>
          <button
            class="auth-tab"
            :class="{ active: tab === 'register' }"
            @click="switchTab('register')"
          >
            {{ localeStore.t.auth?.register || 'Create Account' }}
          </button>
        </div>
      </div>

      <div class="auth-card__body">
        <el-form
          ref="formRef"
          :model="form"
          :rules="rules"
          label-position="top"
        >
          <el-form-item :label="localeStore.t.auth?.email || 'Email'" prop="email">
            <el-autocomplete
              v-model="form.email"
              :fetch-suggestions="queryHistory"
              :placeholder="localeStore.t.auth?.emailPlaceholder || 'Enter your email'"
              size="large"
              :trigger-on-focus="true"
              @select="onSelectHistory"
              @focus="onEmailFocus"
            >
              <template #default="{ item }">
                <div class="history-item">
                  <span class="history-email">{{ item.value }}</span>
                  <span class="history-badge" v-if="item.fresh">
                    {{ item.labelExtra || 'Last login' }}
                  </span>
                </div>
              </template>
            </el-autocomplete>
          </el-form-item>

          <el-form-item :label="localeStore.t.auth?.password || 'Password'" prop="password">
            <el-input
              v-model="form.password"
              type="password"
              show-password
              :placeholder="localeStore.t.auth?.passwordPlaceholder || 'Enter your password'"
              size="large"
            />
          </el-form-item>

          <el-form-item
            v-if="tab === 'register'"
            :label="localeStore.t.auth?.confirmPassword || 'Confirm Password'"
            prop="confirmPassword"
          >
            <el-input
              v-model="form.confirmPassword"
              type="password"
              show-password
              :placeholder="localeStore.t.auth?.confirmPasswordPlaceholder || 'Confirm your password'"
              size="large"
            />
          </el-form-item>

          <div class="captcha-row">
            <SlideCaptcha
              ref="captchaRef"
              @verify="onCaptchaVerify"
            />
          </div>

          <el-button
            type="primary"
            size="large"
            class="submit-btn"
            :loading="loading"
            @click="onSubmit"
          >
            {{
              tab === 'login'
                ? (localeStore.t.auth?.loginBtn || 'Sign In')
                : (localeStore.t.auth?.registerBtn || 'Create Account')
            }}
          </el-button>
        </el-form>

        <p class="auth-switch">
          {{ tab === 'login'
            ? (localeStore.t.auth?.noAccount || "Don't have an account?")
            : (localeStore.t.auth?.hasAccount || 'Already have an account?')
          }}
          <button class="switch-link" @click="switchTab(tab === 'login' ? 'register' : 'login')">
            {{ tab === 'login'
              ? (localeStore.t.auth?.register || 'Create one')
              : (localeStore.t.auth?.login || 'Sign in')
            }}
          </button>
        </p>
      </div>
    </div>

    <router-link to="/" class="auth-back-link">
      ← {{ localeStore.t.app.title }}
    </router-link>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import type { FormInstance, FormRules } from 'element-plus'
import SlideCaptcha from '../components/SlideCaptcha.vue'
import { useAuthStore } from '../stores/auth'
import { useLocaleStore } from '../stores/locale'

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()
const localeStore = useLocaleStore()

const tab = ref<'login' | 'register'>('login')
const loading = ref(false)
const captchaRef = ref<InstanceType<typeof SlideCaptcha> | null>(null)
const captchaToken = ref('')
const formRef = ref<FormInstance | null>(null)

const form = reactive({
  email: '',
  password: '',
  confirmPassword: '',
})

// --- Login history ---
const HOURS_72 = 72 * 60 * 60 * 1000
const LS_KEY = 'loginHistory'

interface LoginEntry {
  email: string
  password: string
  lastLogin: number
}

function loadHistory(): LoginEntry[] {
  try {
    const raw = localStorage.getItem(LS_KEY)
    return raw ? JSON.parse(raw) : []
  } catch {
    return []
  }
}

function saveHistory(entries: LoginEntry[]) {
  localStorage.setItem(LS_KEY, JSON.stringify(entries))
}

function obfuscate(s: string): string {
  // Simple reversible obfuscation for local-only convenience
  return btoa(s.split('').reverse().join('') + ':tk')
}

function deobfuscate(s: string): string {
  try {
    const inner = atob(s)
    if (inner.endsWith(':tk')) {
      return inner.slice(0, -3).split('').reverse().join('')
    }
  } catch { /* ignore */ }
  return ''
}

function queryHistory(qs: string, cb: (results: any[]) => void) {
  if (tab.value !== 'login') {
    cb([])
    return
  }
  const history = loadHistory()
  const now = Date.now()
  const results = history
    .filter((e) => !qs || e.email.toLowerCase().includes(qs.toLowerCase()))
    .sort((a, b) => b.lastLogin - a.lastLogin)
    .map((e) => ({
      value: e.email,
      password: e.password,
      fresh: now - e.lastLogin < HOURS_72,
      labelExtra: now - e.lastLogin < HOURS_72 ? 'Last login' : '',
    }))
  cb(results)
}

function onSelectHistory(item: { value: string; password: string; fresh: boolean }) {
  form.email = item.value
  if (item.fresh && tab.value === 'login') {
    form.password = deobfuscate(item.password)
  }
}

function onEmailFocus() {
  // Trigger suggestions on focus
}

function recordLogin(email: string, password: string) {
  const history = loadHistory().filter((e) => e.email !== email)
  history.push({
    email,
    password: obfuscate(password),
    lastLogin: Date.now(),
  })
  // Keep max 5 entries
  if (history.length > 5) {
    history.splice(0, history.length - 5)
  }
  saveHistory(history)
}

const validateConfirmPassword = (_rule: unknown, value: string, callback: (err?: Error) => void) => {
  if (tab.value === 'register' && value !== form.password) {
    callback(new Error(localeStore.t.auth?.passwordsDoNotMatch || 'Passwords do not match'))
  } else {
    callback()
  }
}

const rules = computed<FormRules>(() => ({
  email: [
    { required: true, message: localeStore.t.auth?.emailRequired || 'Email is required', trigger: 'blur' },
    { type: 'email', message: localeStore.t.auth?.emailInvalid || 'Invalid email format', trigger: 'blur' },
  ],
  password: [
    { required: true, message: localeStore.t.auth?.passwordRequired || 'Password is required', trigger: 'blur' },
    { min: 6, message: localeStore.t.auth?.passwordMinLength || 'Password must be at least 6 characters', trigger: 'blur' },
  ],
  confirmPassword: [
    { validator: validateConfirmPassword, trigger: 'blur' },
  ],
}))

function switchTab(t: 'login' | 'register') {
  tab.value = t
  form.email = ''
  form.password = ''
  form.confirmPassword = ''
  captchaToken.value = ''
  captchaRef.value?.reset()
  formRef.value?.resetFields()
}

function onCaptchaVerify(token: string) {
  captchaToken.value = token
}

async function onSubmit() {
  if (!formRef.value || loading.value) return

  try {
    await formRef.value.validate()
  } catch {
    return
  }

  if (!captchaToken.value) {
    ElMessage.warning(localeStore.t.auth?.slideToVerify || 'Please complete the captcha')
    return
  }

  loading.value = true
  try {
    if (tab.value === 'login') {
      await authStore.doLogin(form.email, form.password, captchaToken.value)
      recordLogin(form.email, form.password)
      ElMessage.success(localeStore.t.auth?.loginSuccess || 'Login successful')
    } else {
      await authStore.doRegister(form.email, form.password, captchaToken.value)
      ElMessage.success(localeStore.t.auth?.registerSuccess || 'Registration successful')
    }
    const redirect = (route.query.redirect as string) || '/'
    router.push(redirect)
  } catch (err: any) {
    captchaRef.value?.reset()
    captchaToken.value = ''
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.auth-page {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, var(--color-bg-primary) 0%, var(--color-bg-tertiary) 100%);
  padding: var(--spacing-lg);
}

.auth-card {
  width: 100%;
  max-width: 420px;
  background: var(--color-bg-secondary, #fff);
  border-radius: var(--radius-2xl, 24px);
  box-shadow: var(--shadow-lg, 0 8px 30px rgba(0, 0, 0, 0.08));
  overflow: hidden;
}

.auth-card__header {
  padding: var(--spacing-xl, 32px) var(--spacing-xl, 32px) 0;
  text-align: center;
}

.auth-logo {
  font-size: var(--font-size-xl, 20px);
  font-weight: var(--font-weight-bold, 700);
  color: var(--color-text-primary, #1d1d1f);
  letter-spacing: var(--letter-spacing-tight, -0.022em);
  margin-bottom: var(--spacing-lg, 24px);
}

.auth-tabs {
  display: flex;
  background: var(--color-bg-primary, #f5f5f7);
  border-radius: var(--radius-md, 12px);
  padding: 3px;
  gap: 2px;
}

.auth-tab {
  flex: 1;
  padding: 8px 16px;
  border: none;
  background: transparent;
  font-size: var(--font-size-sm, 13px);
  font-weight: var(--font-weight-medium, 500);
  color: var(--color-text-secondary, #86868b);
  cursor: pointer;
  border-radius: 10px;
  transition: all var(--transition-fast, 150ms ease);
  font-family: inherit;
}

.auth-tab.active {
  background: var(--color-bg-secondary, #fff);
  color: var(--color-text-primary, #1d1d1f);
  box-shadow: var(--shadow-sm, 0 1px 3px rgba(0, 0, 0, 0.04));
}

.auth-card__body {
  padding: var(--spacing-xl, 32px);
}

.captcha-row {
  margin-bottom: 20px;
}

.submit-btn {
  width: 100%;
  height: 48px;
  font-size: var(--font-size-base, 15px);
  font-weight: var(--font-weight-semibold, 600);
  border-radius: var(--radius-md, 12px);
}

.auth-switch {
  margin-top: var(--spacing-lg, 24px);
  text-align: center;
  font-size: var(--font-size-sm, 13px);
  color: var(--color-text-secondary, #86868b);
}

.switch-link {
  border: none;
  background: none;
  color: var(--color-accent, #0071e3);
  font-size: var(--font-size-sm, 13px);
  font-weight: var(--font-weight-medium, 500);
  cursor: pointer;
  font-family: inherit;
  padding: 0;
}

.switch-link:hover {
  text-decoration: underline;
}

.auth-back-link {
  margin-top: var(--spacing-lg, 24px);
  font-size: var(--font-size-sm, 13px);
  color: var(--color-text-secondary, #86868b);
  text-decoration: none;
  transition: color var(--transition-fast, 150ms ease);
}

.auth-back-link:hover {
  color: var(--color-text-primary, #1d1d1f);
}

/* Login history dropdown */
.history-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  width: 100%;
}

.history-email {
  font-size: var(--font-size-sm, 13px);
  color: var(--color-text-primary, #1d1d1f);
}

.history-badge {
  font-size: 11px;
  color: var(--color-accent, #0071e3);
  background: rgba(0, 113, 227, 0.08);
  padding: 1px 8px;
  border-radius: 10px;
  white-space: nowrap;
  margin-left: 8px;
}
</style>
