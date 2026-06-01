<template>
  <el-form
    ref="formRef"
    :model="form"
    :rules="rules"
    label-width="130px"
    class="record-form"
  >
    <!-- Model sync status bar -->
    <div class="sync-bar">
      <span class="sync-info">
        {{ modelsStore.providerCount }} providers · {{ modelsStore.modelCount }} models
        <template v-if="modelsStore.registry.updated_at">
          · {{ new Date(modelsStore.registry.updated_at).toLocaleDateString() }}
        </template>
      </span>
      <el-button
        :loading="modelsStore.syncing"
        :icon="Refresh"
        circle
        size="small"
        class="sync-btn"
        @click="onSyncModels"
      />
    </div>

    <div class="section-divider" />

    <el-form-item :label="loc.t.form.date" prop="date">
      <el-date-picker
        v-model="form.date"
        type="date"
        :placeholder="loc.t.form.selectDate"
        format="YYYY-MM-DD"
        value-format="YYYY-MM-DD"
      />
    </el-form-item>

    <div class="form-row">
      <el-form-item :label="loc.t.form.provider" prop="provider">
        <el-select
          v-model="form.provider"
          :placeholder="loc.t.form.selectProvider"
          filterable
          allow-create
        >
          <el-option
            v-for="p in providers"
            :key="p.name"
            :label="`${p.name} (${p.count})`"
            :value="p.name"
          />
        </el-select>
      </el-form-item>
      <el-form-item :label="loc.t.form.model" prop="model_name">
        <el-select
          v-model="form.model_name"
          :placeholder="loc.t.form.selectModel"
          filterable
          allow-create
          remote
          :remote-method="filterModels"
          @visible-change="onModelDropdownVisible"
        >
          <el-option
            v-for="m in filteredModelOptions"
            :key="m"
            :label="m"
            :value="m"
          />
        </el-select>
      </el-form-item>
    </div>

    <div class="form-row">
      <el-form-item :label="loc.t.form.inputTokens" prop="input_tokens">
        <el-input-number
          v-model="form.input_tokens"
          :min="0"
          :step="1000"
          controls-position="right"
          style="width: 100%"
        />
      </el-form-item>
      <el-form-item :label="loc.t.form.outputTokens" prop="output_tokens">
        <el-input-number
          v-model="form.output_tokens"
          :min="0"
          :step="1000"
          controls-position="right"
          style="width: 100%"
        />
      </el-form-item>
    </div>

    <div class="total-stat-card">
      <span class="total-stat-label">{{ loc.t.form.total }}</span>
      <span class="total-stat-value">{{ totalTokens.toLocaleString() }}</span>
    </div>

    <el-form-item :label="loc.t.form.notes" prop="notes">
      <el-input
        v-model="form.notes"
        type="textarea"
        :rows="3"
        :placeholder="loc.t.form.optionalNotes"
      />
    </el-form-item>

    <div class="form-actions">
      <el-button @click="$router.back()">{{ loc.t.form.cancel }}</el-button>
      <el-button type="primary" @click="submit" :loading="submitting">
        {{ loc.t.form[props.mode === 'add' ? 'create' : 'update'] }}
      </el-button>
    </div>
  </el-form>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { Refresh } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import type { FormInstance, FormRules } from 'element-plus'
import { useTokenRecordsStore } from '../stores/tokenRecords'
import { useLocaleStore } from '../stores/locale'
import { useModelsStore } from '../stores/models'
import router from '../router'
import type { TokenUsageCreate } from '../types'

const props = defineProps<{
  mode: 'add' | 'edit'
}>()

const store = useTokenRecordsStore()
const loc = useLocaleStore()
const modelsStore = useModelsStore()
const formRef = ref<FormInstance>()
const submitting = ref(false)

const modelSearch = ref('')

const providers = computed(() =>
  modelsStore.registry.providers.map((provider) => ({
    name: provider.name,
    count: provider.models.length,
  })),
)

const modelOptions = computed(() => {
  if (!form.value.provider) return []
  return modelsStore.modelsByProvider[form.value.provider] || []
})

const filteredModelOptions = computed(() => {
  const keyword = modelSearch.value.trim().toLowerCase()
  if (!keyword) return modelOptions.value
  return modelOptions.value.filter((model) => model.toLowerCase().includes(keyword))
})

const form = ref<TokenUsageCreate>({
  date: '',
  model_name: '',
  provider: '',
  input_tokens: 0,
  output_tokens: 0,
  notes: '',
})

const totalTokens = computed(() => form.value.input_tokens + form.value.output_tokens)

const rules = computed<FormRules>(() => ({
  date: [{ required: true, message: loc.t.validation.dateRequired, trigger: 'change' }],
  provider: [{ required: true, message: loc.t.validation.providerRequired, trigger: 'change' }],
  model_name: [{ required: true, message: loc.t.validation.modelRequired, trigger: 'change' }],
  input_tokens: [{ required: true, message: loc.t.validation.inputRequired, trigger: 'blur' }],
  output_tokens: [{ required: true, message: loc.t.validation.outputRequired, trigger: 'blur' }],
}))

watch(() => form.value.provider, () => {
  form.value.model_name = ''
  modelSearch.value = ''
})

if (props.mode === 'edit') {
  watch(
    () => store.currentRecord,
    (record) => {
      if (record) {
        form.value = {
          date: record.date,
          model_name: record.model_name,
          provider: record.provider,
          input_tokens: record.input_tokens,
          output_tokens: record.output_tokens,
          notes: record.notes || '',
        }
      }
    },
    { immediate: true },
  )
}

function filterModels(keyword: string) {
  modelSearch.value = keyword
}

function onModelDropdownVisible(visible: boolean) {
  if (visible) modelSearch.value = ''
}

async function onSyncModels() {
  const result = await modelsStore.syncRegistry()
  if (result.ok) {
    ElMessage.success(`${result.providers} providers, ${result.models} models synced`)
  } else {
    ElMessage.error(result.detail || 'Sync failed')
  }
}

async function submit() {
  if (!formRef.value) return
  await formRef.value.validate(async (valid) => {
    if (!valid) return
    submitting.value = true
    try {
      if (props.mode === 'add') {
        await store.createRecord({ ...form.value })
      } else {
        const id = store.currentRecord!.id
        await store.updateRecord(id, { ...form.value })
      }
      ElMessage.success(loc.t.messages[props.mode === 'add' ? 'created' : 'updated'])
      router.push('/records')
    } finally {
      submitting.value = false
    }
  })
}
</script>

<style scoped>
.record-form {
  max-width: 720px;
  margin: 0 auto;
  background: var(--color-bg-secondary);
  border-radius: var(--radius-xl);
  padding: var(--spacing-xl) var(--spacing-lg);
  box-shadow: var(--shadow-sm);
}

/* Sync bar */
.sync-bar {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  gap: var(--spacing-sm);
  margin-bottom: var(--spacing-sm);
  padding: var(--spacing-xs) var(--spacing-md);
  background: rgba(0, 113, 227, 0.04);
  border-radius: var(--radius-sm);
  font-size: var(--font-size-xs);
  color: var(--color-text-secondary);
}

.sync-info {
  white-space: nowrap;
}

.sync-btn {
  flex-shrink: 0;
}

/* Section divider */
.section-divider {
  height: 1px;
  background: var(--color-divider);
  margin: 0 0 var(--spacing-lg) 0;
}

/* Two-column row */
.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: var(--spacing-md);
}

.form-row :deep(.el-form-item) {
  margin-bottom: var(--spacing-md);
}

@media (max-width: 640px) {
  .form-row {
    grid-template-columns: 1fr;
  }
}

/* Total stat card */
.total-stat-card {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: var(--spacing-md) var(--spacing-lg);
  margin-bottom: var(--spacing-md);
  background: linear-gradient(
    135deg,
    rgba(0, 113, 227, 0.07) 0%,
    rgba(0, 113, 227, 0.02) 100%
  );
  border: 1px solid rgba(0, 113, 227, 0.12);
  border-radius: var(--radius-md);
}

.total-stat-label {
  font-size: var(--font-size-sm);
  font-weight: var(--font-weight-medium);
  color: var(--color-text-secondary);
  text-transform: uppercase;
  letter-spacing: 0.04em;
}

.total-stat-value {
  font-size: var(--font-size-xl);
  font-weight: var(--font-weight-bold);
  color: var(--color-accent);
  font-variant-numeric: tabular-nums;
}

/* Action buttons */
.form-actions {
  display: flex;
  justify-content: flex-end;
  gap: var(--spacing-sm);
  padding-top: var(--spacing-md);
  border-top: 1px solid var(--color-divider);
  margin-top: var(--spacing-xs);
}
</style>
