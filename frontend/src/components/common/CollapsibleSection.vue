<template>
  <div class="collapsible-section">
    <div class="section-header" @click="expanded = !expanded">
      <el-icon :class="{ rotated: expanded }"><ArrowRight /></el-icon>
      <span class="section-title">{{ title }}</span>
      <span v-if="optional" class="section-badge">可选</span>
    </div>
    <el-collapse-transition>
      <div v-show="expanded" class="section-body">
        <slot />
      </div>
    </el-collapse-transition>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'

defineProps<{ title: string; optional?: boolean; defaultExpanded?: boolean }>()
const expanded = ref(true)
</script>

<style scoped>
.section-header {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 0;
  cursor: pointer;
  user-select: none;
  color: var(--text-primary);
  font-weight: 500;
  font-size: 14px;
}
.section-header:hover { color: var(--accent); }
.section-header .el-icon { transition: transform 0.2s; font-size: 14px; }
.section-header .el-icon.rotated { transform: rotate(90deg); }
.section-badge {
  font-size: 11px;
  padding: 1px 6px;
  border-radius: 10px;
  background: var(--bg-tertiary);
  color: var(--text-tertiary);
  font-weight: 400;
}
.section-body { padding-left: 22px; }
</style>
