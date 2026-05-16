<template>
  <header class="app-header">
    <div class="header-left">
      <span class="logo">Oracle Backup Tool</span>
    </div>
    <div class="header-right">
      <el-tooltip :content="settingsStore.theme === 'dark' ? '切换浅色模式' : '切换深色模式'" placement="bottom">
        <el-button :icon="settingsStore.theme === 'dark' ? 'Sunny' : 'Moon'" circle text @click="settingsStore.toggleTheme" />
      </el-tooltip>
      <el-dropdown trigger="click" @command="handleCommand">
        <span class="user-info">
          <el-icon><User /></el-icon>
          <span class="username">{{ authStore.user?.display_name || authStore.user?.username || '用户' }}</span>
        </span>
        <template #dropdown>
          <el-dropdown-menu>
            <el-dropdown-item command="settings">
              <el-icon><Setting /></el-icon>设置
            </el-dropdown-item>
            <el-dropdown-item divided command="logout">
              <el-icon><SwitchButton /></el-icon>退出登录
            </el-dropdown-item>
          </el-dropdown-menu>
        </template>
      </el-dropdown>
    </div>
  </header>
</template>

<script setup lang="ts">
import { useRouter } from 'vue-router'
import { useSettingsStore } from '@/stores/settingsStore'
import { useAuthStore } from '@/stores/authStore'

const router = useRouter()
const settingsStore = useSettingsStore()
const authStore = useAuthStore()

function handleCommand(cmd: string) {
  if (cmd === 'logout') {
    authStore.logout()
    router.push('/login')
  } else if (cmd === 'settings') {
    router.push('/settings')
  }
}
</script>

<style scoped>
.app-header {
  height: var(--header-height);
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 20px;
  background: var(--bg-secondary);
  border-bottom: 1px solid var(--border-color);
  position: fixed;
  top: 0;
  left: var(--sidebar-width);
  right: 0;
  z-index: 100;
}
.header-left { display: flex; align-items: center; gap: 12px; }
.logo { font-size: 16px; font-weight: 600; color: var(--text-primary); letter-spacing: 0.5px; }
.header-right { display: flex; align-items: center; gap: 8px; }
.user-info {
  display: flex; align-items: center; gap: 6px; padding: 6px 12px;
  border-radius: var(--radius); cursor: pointer; color: var(--text-secondary);
  transition: background var(--transition);
}
.user-info:hover { background: var(--bg-tertiary); }
.username { font-size: 13px; }
</style>
