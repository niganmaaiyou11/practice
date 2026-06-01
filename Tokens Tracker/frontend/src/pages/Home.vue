<template>
  <div class="home-page">
    <!-- Welcome -->
    <section class="welcome-section anim-fade-up">
      <h1 class="welcome-title">
        {{ t.home?.welcomeBack || 'Welcome back' }}<span v-if="authStore.user">, {{ authStore.user.email }}</span>
      </h1>
    </section>

    <!-- Stat Cards -->
    <section class="stats-section">
      <div class="stat-grid">
        <div class="stat-card anim-card-enter" style="animation-delay: 0ms">
          <span class="stat-label">{{ t.home?.totalTokens || 'Total Tokens' }}</span>
          <span class="stat-value is-accent">{{ totalDisplay }}</span>
        </div>
        <div class="stat-card anim-card-enter" style="animation-delay: 60ms">
          <span class="stat-label">{{ t.home?.monthlyTokens || 'Monthly Tokens' }}</span>
          <span class="stat-value">{{ monthlyDisplay }}</span>
        </div>
        <div class="stat-card anim-card-enter" style="animation-delay: 120ms">
          <span class="stat-label">{{ t.home?.todayTokens || "Today's Tokens" }}</span>
          <span class="stat-value">{{ todayDisplay }}</span>
        </div>
        <div class="stat-card anim-card-enter" style="animation-delay: 180ms">
          <span class="stat-label">{{ t.home?.recordCount || 'Records' }}</span>
          <span class="stat-value">{{ countDisplay }}</span>
        </div>
      </div>
    </section>

    <!-- AI Leaderboard Preview -->
    <section class="carousel-section">
      <LeaderboardPreview />
    </section>

    <!-- Recent Activity Carousel -->
    <section class="carousel-section">
      <h2 class="section-title">{{ t.home?.recentActivity || 'Recent Activity' }}</h2>
      <AnnouncementCarousel :records="recentRecords" />
    </section>

    <!-- Quick Actions -->
    <section class="actions-section anim-fade-up">
      <router-link to="/dashboard" class="action-btn action-btn--primary">
        {{ t.home?.goToDashboard || 'Go to Dashboard' }}
      </router-link>
      <router-link to="/records" class="action-btn action-btn--secondary">
        {{ t.home?.viewAllRecords || 'View All Records' }}
      </router-link>
    </section>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useAuthStore } from '../stores/auth'
import { useLocaleStore } from '../stores/locale'
import { useCountUp } from '../composables/useCountUp'
import { fetchTotals, fetchRecords } from '../api/tokenRecords'
import AnnouncementCarousel from '../components/AnnouncementCarousel.vue'
import LeaderboardPreview from '../components/LeaderboardPreview.vue'
import type { TokenUsage } from '../types'

const authStore = useAuthStore()
const localeStore = useLocaleStore()
const t = localeStore.t

const recentRecords = ref<TokenUsage[]>([])

const totalsTarget = ref<number | undefined>(undefined)
const monthlyTarget = ref<number | undefined>(undefined)
const todayTarget = ref<number | undefined>(undefined)
const countTarget = ref<number | undefined>(undefined)

const totalDisplay = useCountUp(totalsTarget)
const monthlyDisplay = useCountUp(monthlyTarget)
const todayDisplay = useCountUp(todayTarget)
const countDisplay = useCountUp(countTarget, { duration: 1200 })

function getDateRange(daysBack: number) {
  const end = new Date()
  const start = new Date()
  start.setDate(start.getDate() - daysBack)
  return {
    start_date: start.toISOString().slice(0, 10),
    end_date: end.toISOString().slice(0, 10),
  }
}

onMounted(async () => {
  try {
    const [allTotals, monthTotals, todayTotals, recordsPage] = await Promise.all([
      fetchTotals({}),
      fetchTotals(getDateRange(30)),
      fetchTotals(getDateRange(0)),
      fetchRecords({ skip: 0, limit: 50 }),
    ])
    totalsTarget.value = allTotals.total_tokens
    monthlyTarget.value = monthTotals.total_tokens
    todayTarget.value = todayTotals.total_tokens
    countTarget.value = allTotals.record_count
    recentRecords.value = recordsPage.records
  } catch {
    // Silently degrade — counters stay at 0, carousel shows empty state
  }
})
</script>

<style scoped>
.home-page {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-xl);
}

/* Welcome */
.welcome-title {
  font-size: var(--font-size-2xl);
  font-weight: var(--font-weight-semibold);
  color: var(--color-text-primary);
  letter-spacing: var(--letter-spacing-tight);
}

.welcome-title span {
  color: var(--color-text-secondary);
  font-weight: var(--font-weight-normal);
}

/* Stat Cards */
.stat-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: var(--spacing-md);
}

.stat-card {
  background: var(--color-bg-secondary);
  border-radius: var(--radius-xl);
  padding: var(--spacing-lg) var(--spacing-lg) var(--spacing-md);
  box-shadow: var(--shadow-sm);
  display: flex;
  flex-direction: column;
  transition: transform var(--transition-ease-out), box-shadow var(--transition-ease-out);
  cursor: default;
}

.stat-card:hover {
  transform: translateY(-3px);
  box-shadow: var(--shadow-hover);
}

.stat-label {
  font-size: var(--font-size-xs);
  font-weight: var(--font-weight-semibold);
  color: var(--color-text-secondary);
  text-transform: uppercase;
  letter-spacing: 0.04em;
  margin-bottom: var(--spacing-sm);
}

.stat-value {
  font-size: var(--font-size-3xl);
  font-weight: var(--font-weight-bold);
  color: var(--color-text-primary);
  line-height: var(--line-height-tight);
  letter-spacing: var(--letter-spacing-tight);
  font-variant-numeric: tabular-nums;
}

.stat-value.is-accent {
  color: var(--color-accent);
}

/* Carousel Section */
.carousel-section {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-md);
}

.section-title {
  font-size: var(--font-size-xl);
  font-weight: var(--font-weight-semibold);
  color: var(--color-text-primary);
  letter-spacing: var(--letter-spacing-tight);
}

/* Quick Actions */
.actions-section {
  display: flex;
  gap: var(--spacing-md);
  flex-wrap: wrap;
}

.action-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  height: 48px;
  padding: 0 28px;
  font-size: var(--font-size-base);
  font-weight: var(--font-weight-semibold);
  border-radius: var(--radius-md);
  text-decoration: none;
  transition: all var(--transition-fast);
  letter-spacing: var(--letter-spacing-normal);
}

.action-btn--primary {
  color: #fff;
  background: var(--color-accent);
}

.action-btn--primary:hover {
  background: var(--color-accent-hover);
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(0, 113, 227, 0.3);
}

.action-btn--secondary {
  color: var(--color-accent);
  background: transparent;
  border: 1px solid var(--color-accent);
}

.action-btn--secondary:hover {
  background: rgba(0, 113, 227, 0.04);
}

@media (max-width: 800px) {
  .stat-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 480px) {
  .stat-grid {
    grid-template-columns: 1fr;
  }

  .welcome-title {
    font-size: var(--font-size-xl);
  }
}
</style>
