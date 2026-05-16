<template>
  <div class="tag-input">
    <el-tag v-for="(tag, idx) in modelValue" :key="idx" closable size="default" @close="removeTag(idx)" style="margin: 2px 4px 2px 0">
      {{ tag }}
    </el-tag>
    <el-input
      v-if="!limit || modelValue.length < limit"
      ref="inputRef"
      v-model="inputVal"
      :placeholder="placeholder || '输入后按回车添加'"
      size="small"
      style="width: 180px; margin-top: 2px;"
      @keyup.enter="addTag"
    />
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'

const props = defineProps<{ modelValue: string[]; placeholder?: string; limit?: number }>()
const emit = defineEmits<{ 'update:modelValue': [val: string[]] }>()
const inputVal = ref('')
const inputRef = ref()

function addTag() {
  const val = inputVal.value.trim()
  if (val && !props.modelValue.includes(val)) {
    emit('update:modelValue', [...props.modelValue, val])
  }
  inputVal.value = ''
}

function removeTag(idx: number) {
  emit('update:modelValue', props.modelValue.filter((_, i) => i !== idx))
}
</script>

<style scoped>
.tag-input {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 0;
}
</style>
