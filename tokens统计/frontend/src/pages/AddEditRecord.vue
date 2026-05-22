<template>
  <div>
    <div class="page-header">
      <h2>{{ isEdit ? loc.t.addRecord.editTitle : loc.t.addRecord.addTitle }}</h2>
    </div>
    <RecordForm :mode="isEdit ? 'edit' : 'add'" />
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { useTokenRecordsStore } from '../stores/tokenRecords'
import { useLocaleStore } from '../stores/locale'
import RecordForm from '../components/RecordForm.vue'

const route = useRoute()
const store = useTokenRecordsStore()
const loc = useLocaleStore()
const isEdit = computed(() => route.name === 'EditRecord')

onMounted(() => {
  if (isEdit.value) {
    const id = Number(route.params.id)
    store.fetchRecordById(id)
  } else {
    store.currentRecord = null
  }
})
</script>

