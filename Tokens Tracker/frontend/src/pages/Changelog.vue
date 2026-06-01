<template>
  <div class="changelog-page">
    <div class="changelog-header">
      <h1 class="changelog-title">{{ store.t.changelog.title }}</h1>
      <div class="changelog-actions">
        <el-button size="small" @click="expandAll">{{ store.t.changelog.expandAll }}</el-button>
        <el-button size="small" @click="collapseAll">{{ store.t.changelog.collapseAll }}</el-button>
      </div>
    </div>

    <div v-if="items.length === 0" class="changelog-empty">
      {{ store.t.changelog.noEntries }}
    </div>

    <div v-for="(entry, index) in items" :key="entry.date" class="changelog-card">
      <div class="changelog-card-header" @click="toggle(index)">
        <div class="changelog-card-left">
          <span class="changelog-date">{{ entry.date }}</span>
          <span class="changelog-summary">{{ entry.summary }}</span>
        </div>
        <el-icon class="changelog-chevron" :class="{ open: expanded[index] }">
          <ArrowDown />
        </el-icon>
      </div>
      <Transition name="expand">
        <div v-show="expanded[index]" class="changelog-details">
          <ul>
            <li v-for="(detail, i) in entry.details" :key="i">{{ detail }}</li>
          </ul>
        </div>
      </Transition>
    </div>
  </div>
</template>

<script setup lang="ts">
import { reactive } from 'vue'
import { ArrowDown } from '@element-plus/icons-vue'
import { useLocaleStore } from '../stores/locale'
import { changelog } from '../data/changelog'

const store = useLocaleStore()
const items = changelog

const expanded = reactive<boolean[]>(items.map((_, i) => i === 0))

function toggle(index: number) {
  expanded[index] = !expanded[index]
}

function expandAll() {
  for (let i = 0; i < expanded.length; i++) expanded[i] = true
}

function collapseAll() {
  for (let i = 0; i < expanded.length; i++) expanded[i] = false
}
</script>

<style scoped>
.changelog-page {
  max-width: 720px;
  margin: 0 auto;
}

.changelog-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: var(--spacing-xl);
}

.changelog-title {
  font-size: var(--font-size-2xl);
  font-weight: var(--font-weight-bold);
  color: var(--color-text-primary);
  letter-spacing: var(--letter-spacing-tight);
}

.changelog-actions {
  display: flex;
  gap: var(--spacing-sm);
}

.changelog-empty {
  text-align: center;
  padding: var(--spacing-2xl) 0;
  color: var(--color-text-secondary);
  font-size: var(--font-size-base);
}

.changelog-card {
  background: var(--color-bg-secondary);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
  margin-bottom: var(--spacing-md);
  overflow: hidden;
  transition: border-color var(--transition-fast), box-shadow var(--transition-fast);
}

.changelog-card:hover {
  border-color: var(--color-border-strong);
  box-shadow: var(--shadow-sm);
}

.changelog-card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: var(--spacing-lg);
  cursor: pointer;
  user-select: none;
}

.changelog-card-left {
  display: flex;
  align-items: baseline;
  gap: var(--spacing-md);
  min-width: 0;
}

.changelog-date {
  font-size: var(--font-size-sm);
  font-weight: var(--font-weight-semibold);
  color: var(--color-accent);
  white-space: nowrap;
  flex-shrink: 0;
}

.changelog-summary {
  font-size: var(--font-size-base);
  font-weight: var(--font-weight-medium);
  color: var(--color-text-primary);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.changelog-chevron {
  flex-shrink: 0;
  font-size: 16px;
  color: var(--color-text-secondary);
  transition: transform var(--transition-smooth);
}

.changelog-chevron.open {
  transform: rotate(180deg);
}

.changelog-details {
  padding: 0 var(--spacing-lg) var(--spacing-lg);
  border-top: 1px solid var(--color-divider);
}

.changelog-details ul {
  list-style: none;
  padding: 0;
  margin: var(--spacing-md) 0 0;
}

.changelog-details li {
  position: relative;
  padding-left: 18px;
  margin-bottom: var(--spacing-sm);
  font-size: var(--font-size-sm);
  color: var(--color-text-secondary);
  line-height: var(--line-height-normal);
}

.changelog-details li::before {
  content: '';
  position: absolute;
  left: 0;
  top: 8px;
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: var(--color-accent);
  opacity: 0.5;
}

.changelog-details li:last-child {
  margin-bottom: 0;
}

/* Expand/collapse transition */
.expand-enter-active,
.expand-leave-active {
  transition: all var(--transition-smooth);
  overflow: hidden;
}

.expand-enter-from,
.expand-leave-to {
  opacity: 0;
  max-height: 0;
  padding-top: 0;
  padding-bottom: 0;
}

.expand-enter-to,
.expand-leave-from {
  opacity: 1;
  max-height: 500px;
}
</style>
