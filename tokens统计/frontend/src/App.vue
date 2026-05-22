<template>
  <el-config-provider :locale="elLocale">
    <div class="app-shell">
      <header v-if="layout === 'app'" class="app-header">
        <div class="header-inner">
          <router-link to="/" class="app-logo">{{ store.t.app.title }}</router-link>
          <LiquidNav :items="navItems" :active-menu="activeMenu" />
          <div class="header-actions">
            <ThemeToggle />
            <button
              v-if="authStore.isAuthenticated"
              class="logout-btn"
              @click="onLogout"
            >
              {{ store.t.auth?.logout || 'Logout' }}
            </button>
            <el-select
              v-model="store.current"
              class="locale-switcher"
              @change="onLocaleChange"
              size="small"
            >
              <el-option
                v-for="(name, code) in store.localeNames"
                :key="code"
                :label="name"
                :value="code"
              />
            </el-select>
          </div>
        </div>
      </header>
      <main :class="layout === 'app' ? 'app-main' : 'public-main'">
        <router-view v-slot="{ Component }">
          <Transition name="page-fade" mode="out-in">
            <component :is="Component" />
          </Transition>
        </router-view>
      </main>
    </div>
  </el-config-provider>
</template>

<script setup lang="ts">
import { computed, shallowRef, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useLocaleStore } from './stores/locale'
import { useAuthStore } from './stores/auth'
import { useModelsStore } from './stores/models'
import LiquidNav from './components/LiquidNav.vue'
import ThemeToggle from './components/ThemeToggle.vue'
import type { Locale } from './locales'

const route = useRoute()
const router = useRouter()
const store = useLocaleStore()
const authStore = useAuthStore()
const modelsStore = useModelsStore()

const layout = computed(() => {
  if (route.path === '/' && authStore.isAuthenticated) return 'app'
  return (route.meta.layout as string) || 'app'
})

const activeMenu = computed(() => {
  if (route.path.startsWith('/records/') && route.path !== '/records/add') {
    return '/records'
  }
  return route.path
})

const navItems = computed(() => [
  { path: '/dashboard', label: store.t.app.dashboard },
  { path: '/records', label: store.t.app.records },
  { path: '/records/add', label: store.t.app.addRecord },
  { path: '/leaderboard', label: store.t.leaderboard?.navLabel || 'Models' },
  { path: '/settings/email', label: store.t.app.settings || 'Settings' },
])

function onLogout() {
  authStore.doLogout()
  router.push('/')
}

const localeModules: Record<string, any> = {
  en: () => import('element-plus/dist/locale/en.mjs'),
  'zh-CN': () => import('element-plus/dist/locale/zh-cn.mjs'),
  ja: () => import('element-plus/dist/locale/ja.mjs'),
  ko: () => import('element-plus/dist/locale/ko.mjs'),
  ru: () => import('element-plus/dist/locale/ru.mjs'),
  fr: () => import('element-plus/dist/locale/fr.mjs'),
  es: () => import('element-plus/dist/locale/es.mjs'),
}

const elLocale = shallowRef()

async function loadLocale(locale: Locale) {
  const mod = await localeModules[locale]()
  elLocale.value = mod.default
}

function onLocaleChange(locale: Locale) {
  store.setLocale(locale)
  loadLocale(locale)
}

loadLocale(store.current)

onMounted(() => {
  modelsStore.fetchRegistry()
})

watch(() => authStore.isAuthenticated, (val) => {
  if (val) modelsStore.fetchRegistry()
})
</script>

<style scoped>
.app-shell {
  min-height: 100vh;
}

/* Glassmorphism sticky header */
.app-header {
  position: sticky;
  top: 0;
  z-index: 100;
  height: var(--header-height);
  background: var(--glass-bg);
  backdrop-filter: var(--glass-blur);
  -webkit-backdrop-filter: var(--glass-blur);
  border-bottom: 1px solid var(--color-border);
  transition: background-color 300ms cubic-bezier(0.25, 0.1, 0.25, 1),
    border-color 300ms cubic-bezier(0.25, 0.1, 0.25, 1);
}

.header-inner {
  max-width: 1200px;
  margin: 0 auto;
  height: 100%;
  display: flex;
  align-items: center;
  padding: 0 var(--spacing-lg);
  gap: var(--spacing-xl);
}

.app-logo {
  font-size: 17px;
  font-weight: var(--font-weight-bold);
  color: var(--color-text-primary);
  text-decoration: none;
  letter-spacing: var(--letter-spacing-tight);
  white-space: nowrap;
  transition: color 300ms cubic-bezier(0.25, 0.1, 0.25, 1);
}

.header-actions {
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
}

.logout-btn {
  border: none;
  background: transparent;
  font-size: var(--font-size-sm);
  font-weight: var(--font-weight-medium);
  color: var(--color-text-secondary);
  cursor: pointer;
  padding: 6px 12px;
  border-radius: var(--radius-sm);
  transition: color var(--transition-fast), background var(--transition-fast);
  font-family: inherit;
  letter-spacing: var(--letter-spacing-normal);
}

.logout-btn:hover {
  color: var(--color-text-primary);
  background: rgba(0, 0, 0, 0.04);
}

.locale-switcher {
  width: 130px;
}

.locale-switcher :deep(.el-input__wrapper) {
  border-radius: var(--radius-md) !important;
  background: rgba(0, 0, 0, 0.03);
  border: none;
  box-shadow: none !important;
  transition: background 300ms cubic-bezier(0.25, 0.1, 0.25, 1);
}

.locale-switcher :deep(.el-input__wrapper:hover) {
  background: rgba(0, 0, 0, 0.06);
}

/* Main content area */
.app-main {
  max-width: 1200px;
  margin: 0 auto;
  padding: var(--spacing-xl) var(--spacing-lg) var(--spacing-3xl);
}

.public-main {
  min-height: 100vh;
}
</style>
