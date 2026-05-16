<template>
  <el-input v-model="model" :type="showPwd ? 'text' : 'password'" v-bind="$attrs" show-password />
</template>

<script setup lang="ts">
const model = defineModel<string>({ default: '' })
</script>
