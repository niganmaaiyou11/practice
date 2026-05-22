<template>
  <Landing v-if="!authStore.isAuthenticated" />
  <Home v-else />
</template>

<script setup lang="ts">
import { useAuthStore } from '../stores/auth'
import Landing from './Landing.vue'
import Home from './Home.vue'

const authStore = useAuthStore()
</script>
