<template>
  <div class="settings-page">
    <h2>系统设置</h2>
    <el-card shadow="never" style="max-width: 600px">
      <el-form label-position="left" label-width="140px">
        <el-form-item label="界面主题">
          <el-radio-group :model-value="settingsStore.theme" @change="(v: any) => settingsStore.setTheme(v)">
            <el-radio-button value="dark">深色模式</el-radio-button>
            <el-radio-button value="light">浅色模式</el-radio-button>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="默认 Oracle 版本">
          <el-select :model-value="settingsStore.oracleVersion" @change="(v: any) => settingsStore.setOracleVersion(v)" style="width: 200px">
            <el-option v-for="v in ORACLE_VERSIONS" :key="v.value" :label="v.label" :value="v.value" />
          </el-select>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { useSettingsStore } from '@/stores/settingsStore'
import { ORACLE_VERSIONS } from '@/utils/constants'
const settingsStore = useSettingsStore()
</script>

<style scoped>
.settings-page h2 { font-size: 18px; font-weight: 600; margin-bottom: 20px; color: var(--text-primary); }
</style>
