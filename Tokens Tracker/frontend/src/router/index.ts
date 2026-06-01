import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '../stores/auth'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/',
      name: 'Home',
      component: () => import('../pages/HomeRouter.vue'),
      meta: { layout: 'public' },
    },
    {
      path: '/auth',
      name: 'Auth',
      component: () => import('../pages/AuthPage.vue'),
      meta: { layout: 'public' },
    },
    {
      path: '/dashboard',
      name: 'Dashboard',
      component: () => import('../pages/Dashboard.vue'),
      meta: { layout: 'app', requiresAuth: true },
    },
    {
      path: '/records',
      name: 'RecordList',
      component: () => import('../pages/RecordList.vue'),
      meta: { layout: 'app', requiresAuth: true },
    },
    {
      path: '/records/add',
      name: 'AddRecord',
      component: () => import('../pages/AddEditRecord.vue'),
      meta: { layout: 'app', requiresAuth: true },
    },
    {
      path: '/records/:id/edit',
      name: 'EditRecord',
      component: () => import('../pages/AddEditRecord.vue'),
      meta: { layout: 'app', requiresAuth: true },
    },
    {
      path: '/leaderboard',
      name: 'Leaderboard',
      component: () => import('../pages/Leaderboard.vue'),
      meta: { layout: 'app', requiresAuth: true },
    },
    {
      path: '/leaderboard/compare',
      name: 'LeaderboardCompare',
      component: () => import('../pages/LeaderboardCompare.vue'),
      meta: { layout: 'app', requiresAuth: true },
    },
    {
      path: '/pricing',
      name: 'ModelPricing',
      component: () => import('../pages/ModelPricing.vue'),
      meta: { layout: 'app', requiresAuth: true },
    },
    {
      path: '/weekly',
      name: 'AIWeekly',
      component: () => import('../pages/AIWeekly.vue'),
      meta: { layout: 'app', requiresAuth: true },
    },
    {
      path: '/weekly/:slug',
      name: 'AIWeeklyDetail',
      component: () => import('../pages/AIWeeklyDetail.vue'),
      meta: { layout: 'app', requiresAuth: true },
    },
    {
      path: '/changelog',
      name: 'Changelog',
      component: () => import('../pages/Changelog.vue'),
      meta: { layout: 'app', requiresAuth: true },
    },
    {
      path: '/settings/email',
      name: 'EmailSettings',
      component: () => import('../pages/EmailSettings.vue'),
      meta: { layout: 'app', requiresAuth: true },
    },
  ],
})

router.beforeEach(async (to, _from, next) => {
  const authStore = useAuthStore()

  if (!authStore.initialized) {
    await authStore.init()
  }

  if (to.meta.requiresAuth && !authStore.isAuthenticated) {
    next({ name: 'Auth', query: { redirect: to.fullPath } })
  } else if (to.name === 'Auth' && authStore.isAuthenticated) {
    next({ name: 'Home' })
  } else {
    next()
  }
})

export default router
