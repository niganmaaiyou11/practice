import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { Locale, Messages } from '../locales'
import { getMessages, localeNames } from '../locales'

export const useLocaleStore = defineStore('locale', () => {
  const current = ref<Locale>((localStorage.getItem('locale') as Locale) || 'en')

  const t = computed<Messages>(() => getMessages(current.value))

  function setLocale(locale: Locale) {
    current.value = locale
    localStorage.setItem('locale', locale)
  }

  return { current, t, setLocale, localeNames }
})
