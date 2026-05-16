<template>
  <div v-if="warnings.length > 0 || recommendations.length > 0" class="validation-panel">
    <div v-if="warnings.length > 0" class="warnings">
      <div v-for="(w, i) in warnings" :key="i" class="warn-item" :class="w.level">
        <el-icon v-if="w.level === 'error'"><CircleCloseFilled /></el-icon>
        <el-icon v-else-if="w.level === 'warning'"><WarningFilled /></el-icon>
        <el-icon v-else><InfoFilled /></el-icon>
        <div class="warn-content">
          <span class="warn-msg">{{ w.message }}</span>
          <span v-if="w.suggestion" class="warn-suggest">建议：{{ w.suggestion }}</span>
        </div>
      </div>
    </div>
    <div v-if="recommendations.length > 0" class="recommendations">
      <div class="rec-title">优化建议</div>
      <div v-for="(r, i) in recommendations" :key="i" class="rec-item">
        <el-icon><Promotion /></el-icon>
        <span>{{ r }}</span>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { ValidationWarning } from '@/types'
defineProps<{ warnings: ValidationWarning[]; recommendations: string[] }>()
</script>

<style scoped>
.validation-panel { display: flex; flex-direction: column; gap: 12px; }
.warnings { display: flex; flex-direction: column; gap: 8px; }
.warn-item {
  display: flex; gap: 8px; padding: 10px 12px;
  border-radius: var(--radius); font-size: 13px; line-height: 1.5;
}
.warn-item.error { background: var(--danger-light); color: var(--danger); }
.warn-item.warning { background: var(--warning-light); color: var(--warning); }
.warn-item.info { background: var(--info-light); color: var(--info); }
.warn-content { display: flex; flex-direction: column; gap: 2px; }
.warn-msg { font-weight: 500; }
.warn-suggest { font-size: 12px; opacity: 0.85; }
.recommendations { display: flex; flex-direction: column; gap: 6px; }
.rec-title { font-size: 13px; font-weight: 500; color: var(--text-secondary); margin-bottom: 2px; }
.rec-item {
  display: flex; align-items: flex-start; gap: 8px; padding: 8px 12px;
  border-radius: var(--radius); font-size: 13px; color: var(--text-secondary);
  background: var(--bg-tertiary); line-height: 1.5;
}
.rec-item .el-icon { margin-top: 2px; color: var(--accent); flex-shrink: 0; }
</style>
