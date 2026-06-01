<template>
  <div class="email-settings">
    <h2 class="page-title">{{ t.emailSettings?.title || 'Email Sync Settings' }}</h2>

    <!-- Account cards -->
    <div class="section">
      <div class="section-header">
        <span>{{ t.emailSettings?.connectedAccounts || 'Connected Accounts' }}</span>
        <div class="section-actions">
          <el-button @click="gmailDialog?.open()" type="primary" size="small">
            + {{ t.emailSettings?.connectGmail || 'Connect Gmail' }}
          </el-button>
          <el-button @click="imapDialog?.open()" size="small">
            + {{ t.emailSettings?.connectIMAP || 'Connect IMAP' }}
          </el-button>
        </div>
      </div>

      <div v-if="emailStore.accounts.length === 0" class="empty-state">
        {{ t.emailSettings?.noAccounts || 'No email accounts connected yet.' }}
      </div>

      <EmailAccountCard
        v-for="account in emailStore.accounts"
        :key="account.id"
        :account="account"
        :status-item="emailStore.syncStatus?.accounts?.find((a) => a.account_id === account.id)"
      />
    </div>

    <!-- Sync logs -->
    <div class="section">
      <div class="section-header">
        <span>{{ t.emailSettings?.syncLogs || 'Sync Logs' }}</span>
      </div>
      <SyncLogTable
        :logs="emailStore.syncLogs"
        :total="emailStore.logsTotal"
        @page-change="(p: number) => emailStore.fetchSyncLogs({ skip: (p - 1) * 20, limit: 20 })"
      />
    </div>

    <ConnectGmailDialog ref="gmailDialog" @success="onGmailSuccess" />
    <ConnectIMAPDialog ref="imapDialog" />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useLocaleStore } from '../stores/locale'
import { useEmailStore } from '../stores/email'
import EmailAccountCard from '../components/EmailAccountCard.vue'
import SyncLogTable from '../components/SyncLogTable.vue'
import ConnectGmailDialog from '../components/ConnectGmailDialog.vue'
import ConnectIMAPDialog from '../components/ConnectIMAPDialog.vue'

defineOptions({ name: 'EmailSettings' })

const store = useLocaleStore()
const emailStore = useEmailStore()
const gmailDialog = ref<InstanceType<typeof ConnectGmailDialog>>()
const imapDialog = ref<InstanceType<typeof ConnectIMAPDialog>>()

function onGmailSuccess() {
  emailStore.fetchAccounts()
  emailStore.fetchSyncStatus()
}

onMounted(() => {
  emailStore.fetchAccounts()
  emailStore.fetchSyncStatus()
  emailStore.fetchSyncLogs({ limit: 20 })
})

const t = computed(() => store.t)
</script>

<style scoped>
.email-settings {
  max-width: 800px;
  margin: 0 auto;
  padding: 24px 20px;
}
.page-title {
  font-size: 28px;
  font-weight: 600;
  margin-bottom: 24px;
  color: var(--color-text-primary);
}
.section {
  margin-bottom: 32px;
}
.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
  font-size: 16px;
  font-weight: 600;
  color: var(--color-text-primary);
}
.section-actions {
  display: flex;
  gap: 8px;
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
