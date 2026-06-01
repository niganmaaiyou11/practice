<template>
  <el-dialog v-model="visible" :title="t.emailSettings?.connectIMAP || 'Connect IMAP'" width="480px" :close-on-click-modal="false">
    <el-form :model="form" label-position="top">
      <el-form-item :label="t.emailSettings?.emailAddress || 'Email Address'">
        <el-input v-model="form.email_address" :placeholder="t.auth?.emailPlaceholder || 'Email'" @input="onEmailChange" />
      </el-form-item>
      <div class="preset-providers">
        <span class="preset-label">{{ t.emailSettings?.quickFill || 'Quick Fill' }}:</span>
        <el-button size="small" @click="fillPreset('qq')">QQ邮箱</el-button>
        <el-button size="small" @click="fillPreset('163')">163邮箱</el-button>
        <el-button size="small" @click="fillPreset('126')">126邮箱</el-button>
        <el-button size="small" @click="fillPreset('outlook')">Outlook</el-button>
      </div>
      <el-form-item :label="t.emailSettings?.imapServer || 'IMAP Server'">
        <el-input v-model="form.imap_server" placeholder="imap.qq.com" />
      </el-form-item>
      <el-form-item :label="t.emailSettings?.imapUsername || 'Username'">
        <el-input v-model="form.imap_username" :placeholder="t.auth?.emailPlaceholder || 'Email'" />
      </el-form-item>
      <el-form-item :label="t.emailSettings?.imapPassword || 'Authorization Code'">
        <el-input v-model="form.imap_password" type="password" show-password />
        <div class="hint">
          QQ邮箱/163邮箱/126邮箱需使用<b>授权码</b>而非登录密码。<br/>
          QQ邮箱：设置 → 账户 → POP3/IMAP → 生成授权码<br/>
          163邮箱：设置 → POP3/SMTP/IMAP → 新增授权码
        </div>
      </el-form-item>
      <el-form-item :label="t.emailSettings?.monitorProviders || 'Monitor Providers'">
        <el-select
          v-model="form.monitored_providers"
          multiple
          filterable
          :placeholder="t.emailSettings?.selectProviders || 'Select providers to sync (leave empty = all)'"
          style="width: 100%"
        >
          <el-option
            v-for="name in modelsStore.providerNames"
            :key="name"
            :label="name"
            :value="name"
          />
        </el-select>
        <div class="hint">{{ t.emailSettings?.selectProviderHint || 'Select specific AI providers to sync. Leave empty to sync all supported providers.' }}</div>
      </el-form-item>
      <el-button :loading="testing" @click="onTest">
        {{ t.emailSettings?.testConnection || 'Test Connection' }}
      </el-button>
      <span v-if="testResult" :style="{ color: testResult.ok ? '#34c759' : '#ff3b30', marginLeft: '12px', fontSize: '13px' }">
        {{ testResult.message }}
      </span>
    </el-form>
    <template #footer>
      <el-button @click="visible = false">{{ t.form?.cancel || 'Cancel' }}</el-button>
      <el-button type="primary" @click="onCreate" :disabled="!testResult?.ok">
        {{ t.form?.create || 'Create' }}
      </el-button>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { reactive, ref, computed } from 'vue'
import { useLocaleStore } from '../stores/locale'
import { useEmailStore } from '../stores/email'
import { useModelsStore } from '../stores/models'
import * as emailApi from '../api/email'
import type { IMAPTestResponse } from '../types'

defineOptions({ name: 'ConnectIMAPDialog' })

const store = useLocaleStore()
const emailStore = useEmailStore()
const modelsStore = useModelsStore()

const visible = ref(false)
const testing = ref(false)
const testResult = ref<IMAPTestResponse | null>(null)

const PRESETS: Record<string, { server: string; suffix: string }> = {
  qq: { server: 'imap.qq.com', suffix: '@qq.com' },
  '163': { server: 'imap.163.com', suffix: '@163.com' },
  '126': { server: 'imap.126.com', suffix: '@126.com' },
  outlook: { server: 'outlook.office365.com', suffix: '@outlook.com' },
}

const form = reactive({
  email_address: '',
  imap_server: '',
  imap_username: '',
  imap_password: '',
  monitored_providers: [] as string[],
})

function fillPreset(key: string) {
  const preset = PRESETS[key]
  if (!preset) return
  form.imap_server = preset.server
  // Try to extract username from existing email, or use the suffix
  const at = form.email_address.lastIndexOf('@')
  if (at > 0) {
    form.imap_username = form.email_address
  }
}

function onEmailChange() {
  // Auto-detect IMAP server from email suffix
  const email = form.email_address.trim().toLowerCase()
  for (const preset of Object.values(PRESETS)) {
    if (email.endsWith(preset.suffix)) {
      form.imap_server = preset.server
      form.imap_username = email
      return
    }
  }
  // Also handle @vip.qq.com, @foxmail.com etc
  if (email.includes('@') && (email.endsWith('.com') || email.endsWith('.cn'))) {
    const domain = email.split('@')[1]
    for (const preset of Object.values(PRESETS)) {
      if (domain === preset.suffix.slice(1)) {
        form.imap_server = preset.server
        form.imap_username = email
        return
      }
    }
  }
}

function onTest() {
  testing.value = true
  testResult.value = null
  emailApi.testIMAP({
    imap_server: form.imap_server,
    imap_username: form.imap_username || form.email_address,
    imap_password: form.imap_password,
  }).then((res) => {
    testResult.value = res
  }).finally(() => {
    testing.value = false
  })
}

function onCreate() {
  emailStore.createAccount({
    provider_type: 'imap',
    email_address: form.email_address,
    imap_server: form.imap_server,
    imap_username: form.imap_username || form.email_address,
    imap_password: form.imap_password,
    monitored_providers: form.monitored_providers.length > 0 ? form.monitored_providers : undefined,
  }).then(() => {
    visible.value = false
  })
}

const t = computed(() => store.t)

function open() {
  testResult.value = null
  form.imap_server = ''
  form.imap_username = ''
  form.imap_password = ''
  form.monitored_providers = []
  visible.value = true
}

defineExpose({ open })
</script>

<style scoped>
.preset-providers {
  display: flex;
  align-items: center;
  gap: 6px;
  margin-bottom: 12px;
  flex-wrap: wrap;
}
.preset-label {
  font-size: 12px;
  color: var(--color-text-secondary);
  margin-right: 4px;
}
.hint {
  font-size: 12px;
  color: var(--color-text-secondary);
  line-height: 1.6;
  margin-top: 4px;
}
</style>
