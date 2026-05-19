<template>
  <aside class="app-sidebar" :class="{ collapsed: collapsed }">
    <div class="sidebar-logo">
      <el-icon :size="22" color="var(--accent)"><Coin /></el-icon>
      <span v-if="!collapsed" class="logo-text">OBCT</span>
      <el-button class="collapse-btn" :icon="collapsed ? 'Expand' : 'Fold'" text size="small" @click="collapsed = !collapsed" />
    </div>
    <nav class="sidebar-nav">
      <div v-for="group in menuGroups" :key="group.title" class="nav-group">
        <div v-if="!collapsed" class="nav-group-title">{{ group.title }}</div>
        <div v-else class="nav-divider"></div>
        <router-link v-for="item in group.items" :key="item.path" :to="item.path" class="nav-item" exact-active-class="active">
          <el-icon><component :is="item.icon" /></el-icon>
          <span v-if="!collapsed" class="nav-label">{{ item.label }}</span>
        </router-link>
      </div>
    </nav>
  </aside>
</template>

<script setup lang="ts">
import { ref } from 'vue'

const collapsed = ref(false)

const menuGroups = [
  {
    title: '命令工具',
    items: [
      { path: '/', icon: 'Cpu', label: '数据泵' },
      { path: '/rman', icon: 'Files', label: 'RMAN 备份' },
      { path: '/sqlldr', icon: 'UploadFilled', label: 'SQL*Loader' },
    ],
  },
  {
    title: '运维工具',
    items: [
      { path: '/optimizer', icon: 'Operation', label: 'DB 优化' },
      { path: '/installer', icon: 'Upload', label: 'DB 安装' },
    ],
  },
  {
    title: '资源管理',
    items: [
      { path: '/environments', icon: 'Monitor', label: '环境管理' },
      { path: '/templates', icon: 'Collection', label: '命令模板' },
      { path: '/history', icon: 'Clock', label: '历史记录' },
    ],
  },
  {
    title: '系统',
    items: [
      { path: '/settings', icon: 'Setting', label: '系统设置' },
      { path: '/audit', icon: 'List', label: '审计日志' },
    ],
  },
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
  transition: width 0.2s ease;
}
.app-sidebar.collapsed {
  width: 60px;
}
.sidebar-logo {
  height: var(--header-height);
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 0 12px;
  border-bottom: 1px solid var(--border-color);
  white-space: nowrap;
  overflow: hidden;
}
.logo-text {
  font-size: 18px;
  font-weight: 700;
  color: var(--text-primary);
}
.collapse-btn {
  margin-left: auto;
  flex-shrink: 0;
}
.sidebar-nav {
  flex: 1;
  padding: 8px 8px;
  display: flex;
  flex-direction: column;
  gap: 0;
  overflow-y: auto;
}
.nav-group {
  margin-bottom: 4px;
}
.nav-group-title {
  font-size: 11px;
  font-weight: 600;
  color: var(--text-tertiary);
  text-transform: uppercase;
  letter-spacing: 0.5px;
  padding: 8px 14px 4px;
}
.nav-divider {
  height: 1px;
  background: var(--border-color);
  margin: 6px 10px;
}
.nav-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 9px 14px;
  border-radius: var(--radius);
  color: var(--text-secondary);
  font-size: 13px;
  text-decoration: none;
  transition: all var(--transition);
  white-space: nowrap;
  overflow: hidden;
}
.nav-item:hover { background: var(--bg-tertiary); color: var(--text-primary); }
.nav-item.active {
  background: var(--accent-light);
  color: var(--accent);
  font-weight: 500;
}
.collapsed .nav-item {
  justify-content: center;
  padding: 9px;
}

@media (max-width: 768px) {
  .app-sidebar { width: 60px; }
  .app-sidebar .nav-label { display: none; }
  .app-sidebar .nav-group-title { display: none; }
  .app-sidebar .nav-item { justify-content: center; padding: 9px; }
  .app-sidebar .collapse-btn { display: none; }
  .app-sidebar .logo-text { display: none; }
}
</style>
