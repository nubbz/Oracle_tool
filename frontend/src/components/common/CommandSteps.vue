<template>
  <div v-if="steps.length > 0" class="command-steps">
    <div class="steps-header" @click="expanded = !expanded">
      <el-icon class="arrow-icon" :class="{ rotated: expanded }"><ArrowRight /></el-icon>
      <span class="steps-title">命令执行说明</span>
      <el-tag size="small" type="info" round>{{ steps.length }} 步</el-tag>
    </div>
    <el-collapse-transition>
      <div v-show="expanded" class="steps-body">
        <div v-for="(step, i) in steps" :key="i" class="step-row">
          <span class="step-num">{{ i + 1 }}</span>
          <span class="step-text">{{ step }}</span>
        </div>
      </div>
    </el-collapse-transition>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { ArrowRight } from '@element-plus/icons-vue'

defineProps<{ steps: string[] }>()
const expanded = ref(true)
</script>

<style scoped>
.command-steps {
  background: var(--el-fill-color-lighter, #f5f7fa);
  border-radius: 6px;
  overflow: hidden;
}
.steps-header {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 14px;
  cursor: pointer;
  user-select: none;
}
.steps-header:hover { background: var(--el-fill-color, #ebeef5); }
.arrow-icon { transition: transform 0.2s; font-size: 12px; }
.arrow-icon.rotated { transform: rotate(90deg); }
.steps-title { font-size: 13px; font-weight: 600; color: var(--el-text-color-primary); }
.steps-body {
  padding: 4px 14px 12px;
  display: flex;
  flex-direction: column;
  gap: 6px;
}
.step-row {
  display: flex;
  align-items: flex-start;
  gap: 10px;
  font-size: 13px;
  line-height: 1.5;
}
.step-num {
  flex-shrink: 0;
  width: 20px;
  height: 20px;
  border-radius: 50%;
  background: var(--el-color-primary, #409eff);
  color: #fff;
  font-size: 11px;
  font-weight: 600;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-top: 1px;
}
.step-text { color: var(--el-text-color-regular); }
</style>
