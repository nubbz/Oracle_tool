<template>
  <aside class="app-sidebar">
    <div class="sidebar-logo">
      <el-icon :size="22" color="var(--accent)"><Coin /></el-icon>
      <span>OBCT</span>
    </div>
    <nav class="sidebar-nav">
      <router-link v-for="item in menuItems" :key="item.path" :to="item.path" class="nav-item" active-class="active">
        <el-icon><component :is="item.icon" /></el-icon>
        <span>{{ item.label }}</span>
      </router-link>
    </nav>
  </aside>
</template>

<script setup lang="ts">
const menuItems = [
  { path: '/', icon: 'Cpu', label: '命令生成' },
  { path: '/history', icon: 'Clock', label: '历史记录' },
  { path: '/environments', icon: 'Monitor', label: '环境管理' },
  { path: '/optimizer', icon: 'Operation', label: 'DB 优化' },
  { path: '/installer', icon: 'Upload', label: 'DB 安装' },
  { path: '/settings', icon: 'Setting', label: '系统设置' },
]
</script>

<style scoped>
.app-sidebar {
  width: var(--sidebar-width);
  height: 100vh;
  position: fixed;
  left: 0;
  top: 0;
  background: var(--bg-secondary);
  border-right: 1px solid var(--border-color);
  display: flex;
  flex-direction: column;
  z-index: 200;
}
.sidebar-logo {
  height: var(--header-height);
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 0 20px;
  border-bottom: 1px solid var(--border-color);
  font-size: 18px;
  font-weight: 700;
  color: var(--text-primary);
}
.sidebar-nav {
  flex: 1;
  padding: 12px 8px;
  display: flex;
  flex-direction: column;
  gap: 2px;
}
.nav-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 14px;
  border-radius: var(--radius);
  color: var(--text-secondary);
  font-size: 14px;
  text-decoration: none;
  transition: all var(--transition);
}
.nav-item:hover { background: var(--bg-tertiary); color: var(--text-primary); }
.nav-item.active {
  background: var(--accent-light);
  color: var(--accent);
  font-weight: 500;
}
</style>
