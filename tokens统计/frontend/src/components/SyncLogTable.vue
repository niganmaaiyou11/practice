<template>
  <div class="sync-log-table">
    <el-table :data="logs" stripe size="small" style="width: 100%">
      <el-table-column prop="started_at" :label="t.emailSettings?.logTime || 'Time'" width="170">
        <template #default="{ row }">
          {{ new Date(row.started_at).toLocaleString() }}
        </template>
      </el-table-column>
      <el-table-column prop="status" :label="t.emailSettings?.logStatus || 'Status'" width="100">
        <template #default="{ row }">
          <span :class="row.status === 'success' ? 'status-ok' : row.status === 'error' ? 'status-err' : 'status-run'">
            {{ row.status === 'success' ? (t.emailSettings?.statusSuccess || 'Success') : row.status === 'error' ? (t.emailSettings?.statusError || 'Error') : (t.emailSettings?.statusRunning || 'Running') }}
          </span>
        </template>
      </el-table-column>
      <el-table-column prop="emails_fetched" :label="t.emailSettings?.logFetched || 'Fetched'" width="80" />
      <el-table-column prop="emails_parsed" :label="t.emailSettings?.logParsed || 'Parsed'" width="80" />
      <el-table-column prop="records_created" :label="t.emailSettings?.logCreated || 'Created'" width="80" />
      <el-table-column prop="error_message" :label="t.emailSettings?.logDetail || 'Detail'" min-width="200">
        <template #default="{ row }">
          <span v-if="row.error_message" class="err-msg">{{ row.error_message }}</span>
          <span v-else>-</span>
        </template>
      </el-table-column>
    </el-table>
    <el-pagination
      v-if="total > 20"
      layout="prev, pager, next"
      :total="total"
      :page-size="20"
      @current-change="(p: number) => emit('pageChange', p)"
      small
      style="margin-top: 12px; justify-content: center;"
    />
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useLocaleStore } from '../stores/locale'
import type { SyncLog } from '../types'

const props = defineProps<{ logs: SyncLog[]; total: number }>()
const emit = defineEmits<{ pageChange: [page: number] }>()

defineOptions({ name: 'SyncLogTable' })

const store = useLocaleStore()
const t = computed(() => store.t)
</script>

<style scoped>
.sync-log-table {
  background: var(--color-bg-secondary);
  border-radius: 12px;
  padding: 12px;
  box-shadow: var(--shadow-sm);
}
.status-ok { color: #34c759; font-weight: 500; }
.status-err { color: #ff3b30; font-weight: 500; }
.status-run { color: #007aff; font-weight: 500; }
.err-msg { color: #ff3b30; font-size: 12px; }
</style>
