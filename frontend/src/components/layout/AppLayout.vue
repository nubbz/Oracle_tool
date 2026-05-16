<template>
  <AppSidebar />
  <AppHeader />
  <main class="app-main">
    <router-view v-if="!error" />
    <div v-else class="error-boundary">
      <p>页面渲染出错</p>
      <el-button size="small" @click="retry">重试</el-button>
    </div>
  </main>
</template>

<script setup lang="ts">
import AppSidebar from './AppSidebar.vue'
import AppHeader from './AppHeader.vue'
import { ref, onErrorCaptured } from 'vue'
import { useAuthStore } from '@/stores/authStore'

const authStore = useAuthStore()
const error = ref(false)

onErrorCaptured((err) => {
  console.error('[AppLayout] child component error:', err)
  error.value = true
  return false
})

function retry() {
  error.value = false
}

authStore.fetchUser()
</script>

<style scoped>
.app-main {
  margin-left: var(--sidebar-width);
  margin-top: var(--header-height);
  padding: 24px;
  min-height: calc(100vh - var(--header-height));
  overflow-y: auto;
  transition: margin-left 0.2s ease;
}

.error-boundary {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 40px;
  color: var(--el-text-color-secondary);
  font-size: 14px;
}

@media (max-width: 768px) {
  .app-main {
    margin-left: 60px;
    padding: 16px;
  }
}
</style>
