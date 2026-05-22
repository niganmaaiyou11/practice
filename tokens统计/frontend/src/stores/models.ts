import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import axios from 'axios'
import { useAuthStore } from './auth'
import type { ModelsRegistry } from '../types'

export const useModelsStore = defineStore('models', () => {
  const registry = ref<ModelsRegistry>(getStaticFallback())
  const loaded = ref(false)

  const providerNames = computed(() =>
    registry.value.providers.map((p) => p.name)
  )

  const modelsByProvider = computed(() => {
    const map: Record<string, string[]> = {}
    for (const p of registry.value.providers) {
      map[p.name] = [...p.models]
    }
    return map
  })

  const providerColors = computed(() => {
    const map: Record<string, string> = {}
    for (const p of registry.value.providers) {
      map[p.name] = p.color
    }
    return map
  })

  const providerCount = computed(() => registry.value.providers.length)
  const modelCount = computed(() =>
    registry.value.providers.reduce((sum, p) => sum + p.models.length, 0)
  )

  const syncing = ref(false)

  async function fetchRegistry() {
    if (loaded.value) return
    try {
      const authStore = useAuthStore()
      const headers: Record<string, string> = {}
      if (authStore.accessToken) {
        headers.Authorization = `Bearer ${authStore.accessToken}`
      }
      const res = await axios.get('/api/models', { headers })
      registry.value = res.data
      loaded.value = true
    } catch {
      // keep the static fallback, allow retry next time
    }
  }

  async function syncRegistry(): Promise<{ ok: boolean; providers?: number; models?: number; detail?: string }> {
    syncing.value = true
    try {
      const authStore = useAuthStore()
      const headers: Record<string, string> = {}
      if (authStore.accessToken) {
        headers.Authorization = `Bearer ${authStore.accessToken}`
      }
      const res = await axios.post('/api/models/sync', null, { headers })
      if (res.data.ok) {
        await fetchRegistryForce()
      }
      return res.data
    } catch (e: any) {
      return { ok: false, detail: e.response?.data?.detail || e.message }
    } finally {
      syncing.value = false
    }
  }

  async function fetchRegistryForce() {
    try {
      const authStore = useAuthStore()
      const headers: Record<string, string> = {}
      if (authStore.accessToken) {
        headers.Authorization = `Bearer ${authStore.accessToken}`
      }
      const res = await axios.get('/api/models', { headers })
      registry.value = res.data
      loaded.value = true
    } catch {
      // keep current data
    }
  }

  return {
    registry,
    loaded,
    syncing,
    providerNames,
    modelsByProvider,
    providerColors,
    providerCount,
    modelCount,
    fetchRegistry,
    syncRegistry,
  }
})

function getStaticFallback(): ModelsRegistry {
  return {
    providers: [
      { id: 'openai', name: 'OpenAI', color: '#10a37f', models: ['gpt-4o', 'gpt-3.5-turbo'] },
      { id: 'anthropic', name: 'Anthropic', color: '#d97757', models: ['claude-sonnet-4-6', 'claude-haiku-4-5'] },
      { id: 'google', name: 'Google', color: '#4285f4', models: ['gemini-2.5-pro', 'gemini-2.5-flash'] },
      { id: 'deepseek', name: 'DeepSeek', color: '#4d6bfe', models: ['deepseek-v3', 'deepseek-r1'] },
    ],
    updated_at: null,
  }
}
