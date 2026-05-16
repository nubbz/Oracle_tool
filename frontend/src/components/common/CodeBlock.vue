<template>
  <div class="code-block-wrapper">
    <div class="code-header">
      <span class="code-lang">{{ label }}</span>
      <el-button size="small" text @click="handleCopy">
        <el-icon><CopyDocument /></el-icon> 复制
      </el-button>
    </div>
    <pre class="code-block">{{ code }}</pre>
  </div>
</template>

<script setup lang="ts">
import { useClipboard } from '@/composables/useClipboard'
const props = defineProps<{ code: string; label?: string }>()
const { copy } = useClipboard()
function handleCopy() { copy(props.code, props.label || '代码') }
</script>

<style scoped>
.code-block-wrapper { border: 1px solid var(--border-color); border-radius: var(--radius); overflow: hidden; }
.code-header {
  display: flex; justify-content: space-between; align-items: center;
  padding: 8px 12px; background: var(--bg-tertiary); border-bottom: 1px solid var(--border-color);
}
.code-lang { font-size: 12px; color: var(--text-tertiary); font-weight: 500; text-transform: uppercase; }
.code-block {
  background: var(--bg-code); padding: 16px; margin: 0;
  font-family: var(--font-mono); font-size: 13px; line-height: 1.6;
  overflow-x: auto; white-space: pre-wrap; word-break: break-all; color: var(--text-primary);
  max-height: 500px; overflow-y: auto;
}
</style>
