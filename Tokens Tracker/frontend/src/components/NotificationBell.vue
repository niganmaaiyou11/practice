<template>
  <div class="notification-bell" ref="bellRef">
    <button class="bell-btn" @click="togglePanel" :class="{ active: showPanel }">
      <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">
        <path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9"/>
        <path d="M13.73 21a2 2 0 0 1-3.46 0"/>
      </svg>
      <span v-if="unreadCount > 0" class="badge">{{ unreadCount > 99 ? '99+' : unreadCount }}</span>
    </button>

    <Transition name="panel-fade">
      <div v-if="showPanel" class="notification-panel">
        <div class="panel-header">
          <span class="panel-title">通知</span>
          <button v-if="unreadCount > 0" class="mark-all-btn" @click="onMarkAllRead">全部已读</button>
        </div>

        <div class="panel-body" v-if="notifications.length > 0">
          <div
            v-for="item in notifications"
            :key="item.id"
            class="notification-item"
            :class="{ unread: !item.is_read }"
            @click="onItemClick(item)"
          >
            <div class="item-dot" v-if="!item.is_read"></div>
            <div class="item-content">
              <p class="item-title">{{ item.title }}</p>
              <p class="item-message">{{ item.message }}</p>
              <span class="item-time">{{ formatTime(item.created_at) }}</span>
            </div>
          </div>
        </div>

        <div v-else class="panel-empty">
          <p>暂无通知</p>
        </div>
      </div>
    </Transition>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { fetchNotifications, fetchUnreadCount, markNotificationRead, markAllNotificationsRead } from '../api/notifications'
import type { Notification } from '../types'

const router = useRouter()
const showPanel = ref(false)
const unreadCount = ref(0)
const notifications = ref<Notification[]>([])
const bellRef = ref<HTMLElement | null>(null)

let pollTimer: ReturnType<typeof setInterval> | null = null

async function loadUnread() {
  try {
    const data = await fetchUnreadCount()
    unreadCount.value = data.count
  } catch {
    // silent
  }
}

async function loadNotifications() {
  try {
    const data = await fetchNotifications(0, 15)
    notifications.value = data.notifications
    unreadCount.value = data.unread_count
  } catch {
    // silent
  }
}

function togglePanel() {
  showPanel.value = !showPanel.value
  if (showPanel.value) {
    loadNotifications()
  }
}

async function onItemClick(item: Notification) {
  if (!item.is_read) {
    try {
      await markNotificationRead(item.id)
      item.is_read = true
      unreadCount.value = Math.max(0, unreadCount.value - 1)
    } catch {
      // silent
    }
  }
  if (item.link) {
    showPanel.value = false
    router.push(item.link)
  }
}

async function onMarkAllRead() {
  try {
    await markAllNotificationsRead()
    notifications.value.forEach((n) => (n.is_read = true))
    unreadCount.value = 0
  } catch {
    // silent
  }
}

function formatTime(value: string): string {
  const date = new Date(value)
  const now = new Date()
  const diffMs = now.getTime() - date.getTime()
  const diffMin = Math.floor(diffMs / 60000)
  if (diffMin < 1) return '刚刚'
  if (diffMin < 60) return `${diffMin} 分钟前`
  const diffHour = Math.floor(diffMin / 60)
  if (diffHour < 24) return `${diffHour} 小时前`
  const diffDay = Math.floor(diffHour / 24)
  if (diffDay < 7) return `${diffDay} 天前`
  return value.slice(0, 10)
}

function handleClickOutside(e: MouseEvent) {
  if (bellRef.value && !bellRef.value.contains(e.target as Node)) {
    showPanel.value = false
  }
}

onMounted(() => {
  loadUnread()
  pollTimer = setInterval(loadUnread, 60000)
  document.addEventListener('click', handleClickOutside)
})

onUnmounted(() => {
  if (pollTimer) clearInterval(pollTimer)
  document.removeEventListener('click', handleClickOutside)
})
</script>

<style scoped>
.notification-bell {
  position: relative;
}

.bell-btn {
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
  width: 36px;
  height: 36px;
  border: none;
  background: transparent;
  color: #5e5d59;
  cursor: pointer;
  border-radius: 10px;
  transition: background 160ms ease, color 160ms ease;
}

.bell-btn:hover,
.bell-btn.active {
  background: #f0eee6;
  color: #141413;
}

.badge {
  position: absolute;
  top: 2px;
  right: 2px;
  min-width: 16px;
  height: 16px;
  padding: 0 4px;
  border-radius: 999px;
  background: #c96442;
  color: #fff;
  font-size: 10px;
  font-weight: 500;
  line-height: 16px;
  text-align: center;
  letter-spacing: 0;
}

.notification-panel {
  position: absolute;
  top: calc(100% + 8px);
  right: 0;
  width: 360px;
  max-height: 480px;
  background: #faf9f5;
  border: 1px solid #f0eee6;
  border-radius: 18px;
  box-shadow: 0 12px 40px rgba(20, 20, 19, 0.08);
  overflow: hidden;
  z-index: 200;
}

.panel-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px 20px 12px;
  border-bottom: 1px solid #f0eee6;
}

.panel-title {
  font-family: Georgia, 'Times New Roman', serif;
  font-size: 17px;
  font-weight: 500;
  color: #141413;
}

.mark-all-btn {
  border: none;
  background: transparent;
  color: #c96442;
  font-size: 13px;
  cursor: pointer;
  padding: 4px 8px;
  border-radius: 8px;
  transition: background 160ms ease;
}

.mark-all-btn:hover {
  background: #f0eee6;
}

.panel-body {
  overflow-y: auto;
  max-height: 400px;
  padding: 8px 0;
}

.notification-item {
  display: flex;
  gap: 12px;
  padding: 14px 20px;
  cursor: pointer;
  transition: background 160ms ease;
}

.notification-item:hover {
  background: #f0eee6;
}

.notification-item.unread {
  background: rgba(201, 100, 66, 0.04);
}

.item-dot {
  flex-shrink: 0;
  width: 8px;
  height: 8px;
  border-radius: 999px;
  background: #c96442;
  margin-top: 6px;
}

.item-content {
  flex: 1;
  min-width: 0;
}

.item-title {
  font-size: 14px;
  font-weight: 500;
  color: #141413;
  margin-bottom: 4px;
}

.item-message {
  font-size: 13px;
  color: #5e5d59;
  line-height: 1.5;
  margin-bottom: 6px;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.item-time {
  font-size: 11px;
  color: #5e5d59;
  opacity: 0.7;
}

.panel-empty {
  padding: 40px 20px;
  text-align: center;
  color: #5e5d59;
  font-size: 14px;
}

/* Panel animation */
.panel-fade-enter-active,
.panel-fade-leave-active {
  transition: opacity 160ms ease, transform 160ms ease;
}

.panel-fade-enter-from,
.panel-fade-leave-to {
  opacity: 0;
  transform: translateY(-4px);
}

@media (max-width: 480px) {
  .notification-panel {
    width: calc(100vw - 32px);
    right: -8px;
  }
}
</style>
