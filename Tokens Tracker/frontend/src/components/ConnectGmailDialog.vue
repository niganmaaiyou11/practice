<template>
  <el-dialog v-model="visible" :title="t.emailSettings?.gmailDialogTitle || 'Connect Gmail'" width="480px" :close-on-click-modal="false">
    <p style="color: var(--color-text-secondary); margin-bottom: 16px;">
      {{ t.emailSettings?.gmailDialogDesc || 'Authorize this app to read your emails from AI providers to automatically track token usage.' }}
    </p>
    <div class="oauth-scope-info">
      <div class="scope-item">Read emails (readonly)</div>
      <div class="scope-item">Only from AI providers</div>
    </div>
    <template #footer>
      <el-button @click="visible = false">{{ t.form?.cancel || 'Cancel' }}</el-button>
      <el-button type="primary" @click="startOAuth" :loading="loading">
        {{ t.emailSettings?.gotoGoogleAuth || 'Go to Google Authorization' }}
      </el-button>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useLocaleStore } from '../stores/locale'
import * as emailApi from '../api/email'

defineOptions({ name: 'ConnectGmailDialog' })

const store = useLocaleStore()
const t = computed(() => store.t)

const visible = ref(false)
const loading = ref(false)

const emit = defineEmits<{
  success: [email: string]
}>()

let oauthWindow: Window | null = null

function startOAuth() {
  loading.value = true
  emailApi.fetchOAuthUrl().then(({ url }) => {
    const w = 600
    const h = 700
    const left = (screen.width - w) / 2
    const top = (screen.height - h) / 2
    oauthWindow = window.open(url, 'gmail-oauth', `width=${w},height=${h},left=${left},top=${top}`)

    const handler = (event: MessageEvent) => {
      if (event.data?.type === 'gmail-oauth-success') {
        window.removeEventListener('message', handler)
        visible.value = false
        emit('success', event.data.email)
        loading.value = false
      } else if (event.data?.type === 'gmail-oauth-error') {
        window.removeEventListener('message', handler)
        loading.value = false
      }
    }
    window.addEventListener('message', handler)

    // Check if popup was closed
    const timer = setInterval(() => {
      if (oauthWindow?.closed) {
        clearInterval(timer)
        loading.value = false
        window.removeEventListener('message', handler)
      }
    }, 500)
  }).catch(() => {
    loading.value = false
  })
}

function open() {
  visible.value = true
}

defineExpose({ open })
</script>

<style scoped>
.oauth-scope-info {
  background: var(--color-bg-tertiary);
  border-radius: 8px;
  padding: 12px 16px;
  font-size: 13px;
  color: var(--color-text-secondary);
}
.scope-item::before {
  content: '✓ ';
  color: #34c759;
}
</style>
