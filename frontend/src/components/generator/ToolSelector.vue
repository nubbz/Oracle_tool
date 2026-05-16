<template>
  <div class="tool-selector">
    <div
      v-for="item in TOOL_OPTIONS"
      :key="item.value"
      class="tool-card"
      :class="{ active: modelValue === item.value }"
      @click="$emit('update:modelValue', item.value)"
    >
      <el-icon :size="24"><component :is="item.icon" /></el-icon>
      <div class="tool-info">
        <span class="tool-name">{{ item.label }}</span>
        <span class="tool-desc">{{ item.desc }}</span>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { ToolType } from '@/types'
import { TOOL_OPTIONS } from '@/utils/constants'

defineProps<{ modelValue: ToolType }>()
defineEmits<{ 'update:modelValue': [val: ToolType] }>()
</script>

<style scoped>
.tool-selector { display: grid; grid-template-columns: repeat(2, 1fr); gap: 12px; }
.tool-card {
  display: flex; align-items: center; gap: 14px;
  padding: 16px; border: 2px solid var(--border-color);
  border-radius: var(--radius-lg); cursor: pointer;
  transition: all var(--transition); background: var(--bg-secondary);
}
.tool-card:hover { border-color: var(--accent); background: var(--accent-light); }
.tool-card.active { border-color: var(--accent); background: var(--accent-light); }
.tool-card .el-icon { color: var(--accent); }
.tool-info { display: flex; flex-direction: column; }
.tool-name { font-size: 16px; font-weight: 600; color: var(--text-primary); }
.tool-desc { font-size: 12px; color: var(--text-tertiary); margin-top: 2px; }
</style>
