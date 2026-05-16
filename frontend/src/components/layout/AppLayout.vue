<template>
  <AppSidebar />
  <AppHeader />
  <main class="app-main">
    <router-view />
  </main>
</template>

<script setup lang="ts">
import AppSidebar from './AppSidebar.vue'
import AppHeader from './AppHeader.vue'
import { onMounted } from 'vue'
import { useAuthStore } from '@/stores/authStore'

const authStore = useAuthStore()
onMounted(() => { authStore.fetchUser() })
</script>

<style scoped>
.app-main {
  margin-left: var(--sidebar-width);
  margin-top: var(--header-height);
  padding: 24px;
  min-height: calc(100vh - var(--header-height));
  overflow-y: auto;
}
</style>
