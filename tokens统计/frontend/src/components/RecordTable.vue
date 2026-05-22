<template>
  <el-table
    :data="store.records"
    v-loading="store.loading"
    stripe
    style="width: 100%"
    :empty-text="loc.t.table.noRecords"
  >
    <el-table-column prop="date" :label="loc.t.table.date" width="120" sortable />
    <el-table-column prop="provider" :label="loc.t.table.provider" width="120" />
    <el-table-column prop="model_name" :label="loc.t.table.model" min-width="160" />
    <el-table-column prop="input_tokens" :label="loc.t.table.inputTokens" width="140" sortable>
      <template #default="{ row }">
        {{ row.input_tokens.toLocaleString() }}
      </template>
    </el-table-column>
    <el-table-column prop="output_tokens" :label="loc.t.table.outputTokens" width="140" sortable>
      <template #default="{ row }">
        {{ row.output_tokens.toLocaleString() }}
      </template>
    </el-table-column>
    <el-table-column prop="total_tokens" :label="loc.t.table.totalTokens" width="140" sortable>
      <template #default="{ row }">
        {{ row.total_tokens.toLocaleString() }}
      </template>
    </el-table-column>
    <el-table-column prop="notes" :label="loc.t.table.notes" min-width="160" show-overflow-tooltip />
    <el-table-column :label="loc.t.table.actions" width="160" fixed="right">
      <template #default="{ row }">
        <el-button size="small" @click="$router.push(`/records/${row.id}/edit`)">
          {{ loc.t.table.edit }}
        </el-button>
        <el-popconfirm
          :title="loc.t.table.deleteConfirm"
          :confirm-button-text="loc.t.table.delete"
          @confirm="handleDelete(row.id)"
        >
          <template #reference>
            <el-button size="small" type="danger">{{ loc.t.table.delete }}</el-button>
          </template>
        </el-popconfirm>
      </template>
    </el-table-column>
  </el-table>

  <div class="pagination-wrapper">
    <el-pagination
      v-model:current-page="currentPage"
      v-model:page-size="pageSize"
      :total="store.total"
      :page-sizes="[10, 20, 50, 100]"
      layout="total, sizes, prev, pager, next, jumper"
      @current-change="onPageChange"
      @size-change="onSizeChange"
    />
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useTokenRecordsStore } from '../stores/tokenRecords'
import { useLocaleStore } from '../stores/locale'

const store = useTokenRecordsStore()
const loc = useLocaleStore()
const currentPage = ref(1)
const pageSize = ref(20)

function onPageChange(page: number) {
  currentPage.value = page
  store.pagination.skip = (page - 1) * pageSize.value
  store.fetchRecords()
}

function onSizeChange(size: number) {
  pageSize.value = size
  currentPage.value = 1
  store.pagination.skip = 0
  store.pagination.limit = size
  store.fetchRecords()
}

async function handleDelete(id: number) {
  await store.deleteRecord(id)
}
</script>

<style scoped>
.pagination-wrapper {
  display: flex;
  justify-content: flex-end;
  margin-top: 16px;
}
</style>
