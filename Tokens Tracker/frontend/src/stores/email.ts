import { defineStore } from 'pinia'
import { ref } from 'vue'
import type { EmailAccount, SyncLog, SyncStatus, PreviewResponse } from '../types'
import * as emailApi from '../api/email'

export const useEmailStore = defineStore('email', () => {
  const accounts = ref<EmailAccount[]>([])
  const syncStatus = ref<SyncStatus | null>(null)
  const syncLogs = ref<SyncLog[]>([])
  const logsTotal = ref(0)
  const syncingMap = ref<Record<number, boolean>>({})
  const previewingMap = ref<Record<number, boolean>>({})
  const previewData = ref<Record<number, PreviewResponse>>({})

  async function fetchAccounts() {
    accounts.value = await emailApi.fetchAccounts()
  }

  async function createAccount(data: Parameters<typeof emailApi.createAccount>[0]) {
    const account = await emailApi.createAccount(data)
    await fetchAccounts()
    return account
  }

  async function updateAccount(id: number, data: Parameters<typeof emailApi.updateAccount>[1]) {
    const account = await emailApi.updateAccount(id, data)
    await fetchAccounts()
    return account
  }

  async function deleteAccount(id: number) {
    await emailApi.deleteAccount(id)
    await fetchAccounts()
  }

  async function triggerSync(accountId: number) {
    syncingMap.value[accountId] = true
    try {
      const result = await emailApi.triggerSync(accountId)
      // If sync is running in background, poll for completion
      if (result.status === 'running' && result.sync_log_id) {
        await pollSyncCompletion(accountId, result.sync_log_id)
      }
      await fetchAccounts()
      await fetchSyncStatus()
      await fetchSyncLogs({ account_id: accountId, limit: 5 })
      return result
    } finally {
      syncingMap.value[accountId] = false
    }
  }

  async function pollSyncCompletion(accountId: number, logId: number, maxAttempts = 30) {
    for (let i = 0; i < maxAttempts; i++) {
      await new Promise((resolve) => setTimeout(resolve, 2000))
      const res = await emailApi.fetchSyncLogs({ account_id: accountId, limit: 5 })
      const log = res.logs.find((l) => l.id === logId)
      if (log && log.status !== 'running') {
        return
      }
    }
  }

  async function fetchSyncLogs(params: { skip?: number; limit?: number; account_id?: number } = {}) {
    const res = await emailApi.fetchSyncLogs(params)
    syncLogs.value = res.logs
    logsTotal.value = res.total
  }

  async function fetchSyncStatus() {
    syncStatus.value = await emailApi.fetchSyncStatus()
  }

  async function previewSync(accountId: number) {
    previewingMap.value[accountId] = true
    try {
      const result = await emailApi.previewSync(accountId)
      previewData.value[accountId] = result
      return result
    } finally {
      previewingMap.value[accountId] = false
    }
  }

  return {
    accounts, syncStatus, syncLogs, logsTotal, syncingMap,
    previewingMap, previewData,
    fetchAccounts, createAccount, updateAccount, deleteAccount,
    triggerSync, fetchSyncLogs, fetchSyncStatus, previewSync,
  }
})
