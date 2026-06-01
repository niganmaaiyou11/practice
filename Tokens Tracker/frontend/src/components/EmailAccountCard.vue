<template>
  <div class="account-card">
    <div class="card-header">
      <div class="account-info">
        <span class="provider-badge">{{ account.provider_type === 'gmail_oauth' ? 'Gmail' : 'IMAP' }}</span>
        <span class="email">{{ account.email_address }}</span>
      </div>
      <div class="card-actions">
        <el-switch v-model="syncEnabled" :disabled="saving" size="small" />
        <el-button size="small" :loading="previewing" @click="onPreview">
          {{ t.emailSettings?.preview || 'Preview' }}
        </el-button>
        <el-button size="small" :loading="syncing" @click="onSync">
          {{ t.emailSettings?.syncNow || 'Sync Now' }}
        </el-button>
        <el-button size="small" @click="showProviders = !showProviders">
          {{ t.emailSettings?.monitorProviders || 'Providers' }}
        </el-button>
        <el-popconfirm :title="t.emailSettings?.deleteConfirm || 'Delete this account?'" @confirm="onDelete">
          <template #reference>
            <el-button size="small" type="danger" text>{{ t.table?.delete || 'Delete' }}</el-button>
          </template>
        </el-popconfirm>
      </div>
    </div>
    <div class="card-meta">
      <span class="meta-item" :class="statusClass">
        ● {{ statusText }}
      </span>
      <span v-if="account.last_synced_at" class="meta-item">
        {{ t.emailSettings?.lastSync || 'Last sync' }}: {{ formatTime(account.last_synced_at) }}
      </span>
      <span v-if="lastSyncResult" class="meta-item sync-summary" :class="lastSyncResult.status === 'error' ? 'text-error' : 'text-ok'">
        {{ lastSyncResultText }}
      </span>
    </div>

    <!-- Last sync error/details -->
    <div v-if="lastSyncDetail" class="sync-detail">
      {{ lastSyncDetail }}
    </div>

    <!-- Preview dialog -->
    <el-dialog v-model="previewVisible" :title="t.emailSettings?.previewTitle || 'Sync Preview'" width="700px" :close-on-click-modal="true">
      <div v-if="previewLoading" style="text-align: center; padding: 24px;">
        <span style="font-size: 24px;">⟳</span> <span>{{ t.emailSettings?.loadingPreview || 'Loading preview...' }}</span>
      </div>
      <div v-else-if="previewResult">
        <div class="preview-summary">
          <el-tag type="info">{{ t.emailSettings?.foundLabel || 'Found' }}: {{ previewResult.emails_fetched }}</el-tag>
          <el-tag type="warning" style="margin-left: 8px;">{{ t.emailSettings?.parsedLabel || 'Parsed' }}: {{ previewResult.emails_parsed }}</el-tag>
          <el-tag type="success" style="margin-left: 8px;">{{ t.emailSettings?.wouldCreateLabel || 'Would create' }}: {{ previewResult.records_would_create }} {{ t.emailSettings?.records || 'records' }}</el-tag>
        </div>
        <div v-if="previewResult.items.length === 0" class="empty-state" style="margin-top: 16px;">
          {{ t.emailSettings?.noEmailsFound || 'No emails matching AI provider patterns found.' }}
        </div>
        <el-table :data="previewResult.items" style="margin-top: 12px;" max-height="400" size="small">
          <el-table-column :label="t.table?.provider || 'From'" prop="from_addr" width="180" show-overflow-tooltip />
          <el-table-column :label="t.table?.model || 'Subject'" prop="subject" min-width="200" show-overflow-tooltip />
          <el-table-column :label="t.table?.provider || 'Provider'" width="90">
            <template #default="{ row }">
              <el-tag v-if="row.parsed" size="small" :type="row.provider === 'Unknown' ? 'info' : 'success'">
                {{ row.provider }}
              </el-tag>
              <span v-else class="text-muted">—</span>
            </template>
          </el-table-column>
          <el-table-column :label="t.table?.model || 'Model'" width="120" show-overflow-tooltip>
            <template #default="{ row }">
              {{ row.model_name || '—' }}
            </template>
          </el-table-column>
          <el-table-column :label="t.table?.totalTokens || 'Tokens'" width="100">
            <template #default="{ row }">
              <span v-if="row.input_tokens || row.output_tokens">
                {{ (row.input_tokens || 0) + (row.output_tokens || 0) }}
              </span>
              <span v-else class="text-muted">—</span>
            </template>
          </el-table-column>
        </el-table>
      </div>
      <template #footer>
        <el-button @click="previewVisible = false">{{ t.emailSettings?.close || 'Close' }}</el-button>
      </template>
    </el-dialog>

    <!-- Monitored providers -->
    <div v-if="showProviders" class="providers-section">
      <el-select
        v-model="editProviders"
        multiple
        filterable
        placeholder="Select providers to monitor (empty = all)"
        style="width: 100%"
        @change="onProvidersChange"
      >
        <el-option
          v-for="name in modelsStore.providerNames"
          :key="name"
          :label="name"
          :value="name"
        />
      </el-select>
      <div v-if="parsedProviders.length === 0" class="providers-hint">{{ t.emailSettings?.monitoringAll || 'Monitoring all supported AI providers.' }}</div>
    </div>
    <div v-else-if="parsedProviders.length > 0" class="providers-tags">
      <el-tag v-for="p in parsedProviders" :key="p" size="small" type="info" style="margin-right: 4px; margin-bottom: 4px;">
        {{ p }}
      </el-tag>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, ref, watch } from 'vue'
import { useLocaleStore } from '../stores/locale'
import { useEmailStore } from '../stores/email'
import { useModelsStore } from '../stores/models'
import type { EmailAccount, PreviewResponse } from '../types'

defineOptions({ name: 'EmailAccountCard' })

const props = defineProps<{ account: EmailAccount; statusItem?: { last_sync_status: string | null; total_synced_emails: number } }>()

const store = useLocaleStore()
const emailStore = useEmailStore()
const modelsStore = useModelsStore()
const saving = ref(false)
const showProviders = ref(false)
const previewVisible = ref(false)
const previewLoading = ref(false)
const previewResult = ref<PreviewResponse | null>(null)

const syncEnabled = ref(props.account.sync_enabled)
const syncing = computed(() => emailStore.syncingMap[props.account.id])
const previewing = computed(() => emailStore.previewingMap[props.account.id])

const parsedProviders = computed(() => {
  if (!props.account.monitored_providers) return [] as string[]
  try {
    return JSON.parse(props.account.monitored_providers) as string[]
  } catch {
    return []
  }
})

const editProviders = ref<string[]>([...parsedProviders.value])

// Show last sync result summary from the most recent sync log
const lastSyncLog = computed(() => {
  return emailStore.syncLogs.find((l) => l.email_account_id === props.account.id)
})

const lastSyncResult = computed(() => {
  return lastSyncLog.value
})

const lastSyncResultText = computed(() => {
  const log = lastSyncLog.value
  if (!log) return ''
  if (log.status === 'running') return 'Syncing...'
  const parts = []
  if (log.emails_fetched > 0) parts.push(`Found ${log.emails_fetched}`)
  if (log.emails_parsed > 0) parts.push(`Parsed ${log.emails_parsed}`)
  if (log.records_created > 0) parts.push(`Created ${log.records_created}`)
  if (parts.length === 0 && log.status === 'success') return store.t.emailSettings?.syncCompleteNoRecords || 'Sync complete (no new records)'
  return parts.join(', ')
})

const lastSyncDetail = computed(() => {
  const log = lastSyncLog.value
  if (!log || !log.error_message) return ''
  if (log.status === 'error') return log.error_message
  // Show detail when no emails found, or when emails found but nothing parsed
  if (log.emails_fetched === 0 || (log.emails_fetched > 0 && log.emails_parsed === 0)) return log.error_message
  // Show detail when records created but we want to see more info
  if (log.records_created === 0 && log.emails_fetched > 0) return log.error_message
  return ''
})

watch(() => props.account.monitored_providers, () => {
  editProviders.value = [...parsedProviders.value]
})

watch(syncEnabled, (val) => {
  saving.value = true
  emailStore.updateAccount(props.account.id, { sync_enabled: val }).finally(() => { saving.value = false })
})

const statusClass = computed(() => {
  if (props.statusItem?.last_sync_status === 'error') return 'status-error'
  if (props.statusItem?.last_sync_status === 'success') return 'status-ok'
  return 'status-idle'
})

const statusText = computed(() => {
  if (syncEnabled.value === false) return (store.t.emailSettings?.disabled || 'Disabled')
  if (props.statusItem?.last_sync_status === 'error') return (store.t.emailSettings?.statusError || 'Error')
  if (props.statusItem?.last_sync_status === 'success') return (store.t.emailSettings?.statusSuccess || 'Running')
  return 'Idle'
})

function onSync() {
  emailStore.triggerSync(props.account.id)
}

function onDelete() {
  emailStore.deleteAccount(props.account.id)
}

function onProvidersChange() {
  emailStore.updateAccount(props.account.id, {
    monitored_providers: editProviders.value.length > 0 ? editProviders.value : [],
  })
}

async function onPreview() {
  previewVisible.value = true
  previewLoading.value = true
  previewResult.value = null
  try {
    const result = await emailStore.previewSync(props.account.id)
    previewResult.value = result
  } finally {
    previewLoading.value = false
  }
}

function formatTime(s: string) {
  const d = new Date(s)
  return d.toLocaleString()
}

const t = computed(() => store.t)
</script>

<style scoped>
.account-card {
  background: var(--color-bg-secondary);
  border-radius: 12px;
  padding: 16px 20px;
  box-shadow: var(--shadow-sm);
  margin-bottom: 12px;
}
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}
.account-info {
  display: flex;
  align-items: center;
  gap: 10px;
}
.provider-badge {
  background: var(--color-bg-tertiary);
  border-radius: 6px;
  padding: 2px 8px;
  font-size: 12px;
  color: var(--color-text-secondary);
}
.email {
  font-weight: 500;
  font-size: 15px;
  color: var(--color-text-primary);
}
.card-actions {
  display: flex;
  align-items: center;
  gap: 8px;
}
.card-meta {
  display: flex;
  gap: 20px;
  font-size: 13px;
  color: var(--color-text-secondary);
  flex-wrap: wrap;
}
.status-ok { color: #34c759; }
.status-error { color: #ff3b30; }
.status-idle { color: var(--color-text-secondary); }
.text-ok { color: #34c759; }
.text-error { color: #ff3b30; }
.text-muted { color: var(--color-text-tertiary); }
.sync-summary {
  font-weight: 500;
}
.sync-detail {
  margin-top: 6px;
  font-size: 12px;
  color: var(--color-text-secondary);
  background: var(--color-bg-tertiary);
  padding: 6px 10px;
  border-radius: 6px;
  word-break: break-all;
}
.preview-summary {
  display: flex;
  align-items: center;
}
.providers-section {
  margin-top: 12px;
  padding-top: 12px;
  border-top: 1px solid var(--color-divider);
}
.providers-tags {
  margin-top: 8px;
}
.providers-hint {
  font-size: 12px;
  color: var(--color-text-secondary);
  margin-top: 4px;
}
.empty-state {
  color: var(--color-text-secondary);
  font-size: 14px;
  padding: 32px;
  text-align: center;
  background: var(--color-bg-tertiary);
  border-radius: 12px;
}
</style>
