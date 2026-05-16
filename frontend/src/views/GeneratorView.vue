<template>
  <div class="generator-page">
    <div class="page-header">
      <h2>命令生成器</h2>
      <div class="header-actions">
        <el-select v-model="store.tool" style="width: 160px" @change="store.resetParams">
          <el-option v-for="t in TOOL_OPTIONS" :key="t.value" :label="t.label" :value="t.value" />
        </el-select>
        <el-select :model-value="settingsStore.oracleVersion" style="width: 140px" @change="(v: any) => settingsStore.setOracleVersion(v)">
          <el-option v-for="v in ORACLE_VERSIONS" :key="v.value" :label="v.label" :value="v.value" />
        </el-select>
      </div>
    </div>

    <el-card shadow="never" class="params-card">
      <!-- 工具选择 -->
      <ToolSelector v-model="store.tool" @update:model-value="store.resetParams" />

      <el-divider />

      <!-- 连接参数 -->
      <h3 class="section-label">
        数据库连接
        <el-select
          v-model="selectedEnv"
          placeholder="快速选择环境"
          clearable
          size="small"
          style="width: 200px"
          @change="applyEnvironment"
        >
          <el-option v-for="env in environments" :key="env.id" :label="env.name" :value="env.id">
            <span>{{ env.name }}</span>
            <el-tag size="small" :type="envTypeTag(env.env_type)" style="margin-left: 8px">{{ env.env_type }}</el-tag>
          </el-option>
        </el-select>
      </h3>
      <ConnectionForm v-model="store.connection" />

      <el-divider />

      <!-- 工具参数 -->
      <h3 class="section-label">
        {{ store.tool.toUpperCase() }} 参数
        <el-button size="small" text @click="store.resetParams">
          <el-icon><RefreshRight /></el-icon> 重置
        </el-button>
      </h3>
      <ExpdpParams v-if="store.tool === 'expdp'" />
      <ExpParams v-else-if="store.tool === 'exp'" />
      <ImpdpParams v-else-if="store.tool === 'impdp'" />
      <ImpParams v-else-if="store.tool === 'imp'" />

      <el-divider />

      <!-- 实时校验提示 -->
      <el-alert
        v-if="validation.errors.length > 0"
        type="error"
        :closable="false"
        show-icon
        style="margin-bottom: 16px"
      >
        <template #title>
          参数校验发现 {{ validation.errors.filter(e => e.level === 'error').length }} 个错误，{{ validation.errors.filter(e => e.level === 'warning').length }} 个警告
        </template>
        <div v-for="(err, i) in validation.errors" :key="i" style="font-size: 12px; line-height: 1.6">
          <span :style="{ color: err.level === 'error' ? '#F56C6C' : '#E6A23C' }">[{{ err.level === 'error' ? '错误' : '警告' }}]</span>
          {{ err.message }}
        </div>
      </el-alert>

      <!-- 生成按钮 -->
      <div style="display: flex; gap: 10px">
        <el-button type="primary" size="large" :loading="store.loading" style="flex: 1" @click="handleGenerate">
          <el-icon><Cpu /></el-icon> 生成命令
        </el-button>
        <el-button v-if="store.tool === 'expdp' || store.tool === 'exp'" size="large" :loading="reverseLoading" style="flex: 1" @click="handleReverseGenerate">
          <el-icon><Right /></el-icon> 反向生成导入命令
        </el-button>
      </div>
    </el-card>

    <!-- 右侧抽屉：结果面板 -->
    <el-drawer
      v-model="showResult"
      title="生成结果"
      direction="rtl"
      size="50%"
      :destroy-on-close="false"
    >
      <template v-if="store.result">
        <ValidationPanel :warnings="store.result.warnings" :recommendations="store.result.recommendations" />
        <el-divider v-if="store.result.warnings.length > 0 || store.result.recommendations.length > 0" />
        <CommandSteps v-if="store.result.steps?.length" :steps="store.result.steps" />
        <el-divider v-if="store.result.steps?.length" />
        <ScriptOptions :result="store.result" />
      </template>
    </el-drawer>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { ElMessage } from 'element-plus'
import { useGeneratorStore } from '@/stores/generatorStore'
import CommandSteps from '@/components/common/CommandSteps.vue'
import { useSettingsStore } from '@/stores/settingsStore'
import { generateCommand, generateReverse } from '@/api/generator'
import { getEnvironments } from '@/api/environment'
import { camelToSnake } from '@/utils/helpers'
import { TOOL_OPTIONS, ORACLE_VERSIONS } from '@/utils/constants'
import { useParamValidation } from '@/composables/useParamValidation'

import ToolSelector from '@/components/generator/ToolSelector.vue'
import ConnectionForm from '@/components/generator/ConnectionForm.vue'
import ValidationPanel from '@/components/generator/ValidationPanel.vue'
import ScriptOptions from '@/components/generator/ScriptOptions.vue'
import ExpdpParams from '@/components/params/ExpdpParams.vue'
import ExpParams from '@/components/params/ExpParams.vue'
import ImpdpParams from '@/components/params/ImpdpParams.vue'
import ImpParams from '@/components/params/ImpParams.vue'

const store = useGeneratorStore()
const settingsStore = useSettingsStore()
const showResult = ref(false)
const reverseLoading = ref(false)
const environments = ref<any[]>([])
const selectedEnv = ref<number | null>(null)

function loadEnvironments() {
  getEnvironments().then(({ data }) => { environments.value = data }).catch(() => {})
}

function applyEnvironment(envId: number | null) {
  if (!envId) return
  const env = environments.value.find(e => e.id === envId)
  if (!env) return
  store.connection.host = env.host
  store.connection.port = env.port
  store.connection.connectType = env.connect_type
  store.connection.serviceName = env.service_name || ''
  store.connection.sid = env.sid || ''
  store.connection.sshEnabled = env.ssh_enabled || false
  store.connection.sshHost = env.ssh_host || ''
  store.connection.sshPort = env.ssh_port || 22
  store.connection.sshUsername = env.ssh_username || ''
  store.connection.sshAuthMethod = env.ssh_auth_method || 'password'
  store.connection.sshKeyPath = env.ssh_key_path || ''
  store.connection.containerMode = env.container_mode || ''
  store.connection.pdbName = env.pdb_name || ''
  ElMessage.success(`已应用环境「${env.name}」`)
}

function envTypeTag(type: string) {
  return ({ dev: 'info', test: '', uat: 'warning', production: 'danger' } as Record<string, string>)[type] || ''
}

loadEnvironments()

const validation = useParamValidation(
  computed(() => store.tool),
  computed(() => store.currentParams),
  computed(() => settingsStore.oracleVersion),
)

function convertKeys(obj: any): any {
  const result: any = {}
  for (const [k, v] of Object.entries(obj)) {
    result[camelToSnake(k)] = v
  }
  return result
}

async function handleGenerate() {
  if (validation.hasErrors.value) {
    ElMessage.error('请先修正参数错误后再生成命令')
    return
  }
  store.loading = true
  try {
    const connSnake = convertKeys(store.connection)
    const paramsSnake = convertKeys(store.currentParams)
    const { data } = await generateCommand({
      tool: store.tool,
      oracleVersion: settingsStore.oracleVersion,
      connection: connSnake,
      params: paramsSnake,
    })
    store.result = data
    showResult.value = true
    if (data.warnings.some((w: any) => w.level === 'error')) {
      ElMessage.warning('命令已生成，但存在参数错误，请检查')
    } else {
      ElMessage.success('命令生成成功')
    }
  } catch {
    // error handled by interceptor
  } finally {
    store.loading = false
  }
}

async function handleReverseGenerate() {
  reverseLoading.value = true
  try {
    const connSnake = convertKeys(store.connection)
    const paramsSnake = convertKeys(store.currentParams)
    const { data } = await generateReverse({
      tool: store.tool,
      oracleVersion: settingsStore.oracleVersion,
      connection: connSnake,
      params: paramsSnake,
    })
    store.tool = store.tool === 'expdp' ? 'impdp' : 'imp'
    store.result = data
    showResult.value = true
    ElMessage.success(`已反向生成 ${store.tool.toUpperCase()} 导入命令`)
  } catch {
    // error handled by interceptor
  } finally {
    reverseLoading.value = false
  }
}
</script>

<style scoped>
.generator-page { max-width: 900px; margin: 0 auto; }
.page-header {
  display: flex; justify-content: space-between; align-items: center;
  margin-bottom: 20px;
}
.page-header h2 { font-size: 18px; font-weight: 600; color: var(--text-primary); }
.header-actions { display: flex; gap: 10px; align-items: center; }

.params-card :deep(.el-card__body) { padding: 24px 32px; }

.section-label {
  display: flex; justify-content: space-between; align-items: center;
  font-size: 15px; font-weight: 600; color: var(--text-primary); margin-bottom: 16px;
}
</style>
