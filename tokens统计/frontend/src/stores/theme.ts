import { defineStore } from 'pinia'
import { ref, watch } from 'vue'

export type Theme = 'light' | 'dark'

function getSystemTheme(): Theme {
  if (window.matchMedia('(prefers-color-scheme: dark)').matches) return 'dark'
  return 'light'
}

function applyTheme(theme: Theme) {
  const el = document.documentElement
  if (theme === 'dark') {
    el.setAttribute('data-theme', 'dark')
    el.classList.add('dark')
  } else {
    el.removeAttribute('data-theme')
    el.classList.remove('dark')
  }
}

export const useThemeStore = defineStore('theme', () => {
  const stored = localStorage.getItem('theme') as Theme | null
  const current = ref<Theme>(stored || getSystemTheme())

  applyTheme(current.value)

  watch(current, (v) => {
    localStorage.setItem('theme', v)
    applyTheme(v)
  })

  function toggle() {
    current.value = current.value === 'dark' ? 'light' : 'dark'
  }

  function setTheme(theme: Theme) {
    current.value = theme
  }

  return { current, toggle, setTheme }
})
