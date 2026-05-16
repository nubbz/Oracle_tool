<template>
  <div class="optimizer-page">
    <div class="page-header">
      <h2>DB 优化工具</h2>
      <span class="page-desc">Oracle 19c 数据库参数优化脚本命令生成器</span>
    </div>

    <el-alert type="warning" :closable="false" show-icon style="margin-bottom: 16px">
      本工具仅适用于 <b>Oracle 19c</b> 数据库版本优化，其他版本请勿使用。
    </el-alert>

    <el-form :model="form" label-width="auto">
    <!-- 基础配置 -->
    <el-card shadow="never" class="section-card">
      <template #header><span class="section-title">基础配置</span></template>
      <el-row :gutter="16">
        <el-col :span="8">
          <el-form-item label="数据库实例名 (-d)">
            <el-input v-model="form.db_name" />
          </el-form-item>
        </el-col>
        <el-col :span="8">
          <el-form-item label="安装模式 (-m)">
            <el-select v-model="form.mode" style="width: 100%">
              <el-option label="RAC" value="rac" />
              <el-option label="Standalone" value="standalone" />
              <el-option label="Single" value="single" />
            </el-select>
          </el-form-item>
        </el-col>
        <el-col :span="8">
          <el-form-item label="Oracle 用户 (-u)">
            <el-input v-model="form.oracle_user" />
          </el-form-item>
        </el-col>
      </el-row>
      <el-row :gutter="16">
        <el-col :span="12">
          <el-form-item label="Oracle Home (-o)">
            <el-input v-model="form.oracle_home" />
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item label="Grid Home (-g)">
            <el-input v-model="form.grid_home" />
          </el-form-item>
        </el-col>
      </el-row>
    </el-card>

    <!-- 数据库参数 -->
    <el-card shadow="never" class="section-card">
      <template #header><span class="section-title">数据库参数</span></template>
      <el-row :gutter="16">
        <el-col :span="6">
          <el-form-item label="Redo 日志 MB (-r)">
            <el-input-number v-model="form.redosize" :min="128" :step="128" style="width: 100%" controls-position="right" />
            <div class="preset-tags">
              <el-tag v-for="s in [512, 1024, 2048, 4096]" :key="s" size="small" class="preset-tag" @click="form.redosize = s">{{ s }}</el-tag>
            </div>
          </el-form-item>
        </el-col>
        <el-col :span="6">
          <el-form-item label="processes (-p)">
            <el-input-number v-model="form.processes" :min="100" style="width: 100%" controls-position="right" />
          </el-form-item>
        </el-col>
        <el-col :span="6">
          <el-form-item label="open_cursors (-c)">
            <el-input-number v-model="form.open_cursors" :min="100" style="width: 100%" controls-position="right" />
          </el-form-item>
        </el-col>
        <el-col :span="6">
          <el-form-item label="session_cached_cursors (-P)">
            <el-input-number v-model="form.session_cached_cursors" :min="10" style="width: 100%" controls-position="right" />
          </el-form-item>
        </el-col>
      </el-row>
      <el-row :gutter="16">
        <el-col :span="6">
          <el-form-item label="parallel_max_servers (-R)">
            <el-input-number v-model="form.parallel_max_servers" :min="1" style="width: 100%" controls-position="right" />
          </el-form-item>
        </el-col>
        <el-col :span="6">
          <el-form-item label="undo_retention (-U)">
            <el-input-number v-model="form.undo_retention" :min="300" :step="300" style="width: 100%" controls-position="right" />
          </el-form-item>
        </el-col>
        <el-col :span="6">
          <el-form-item label="db_files (-F)">
            <el-input-number v-model="form.db_files" :min="100" style="width: 100%" controls-position="right" />
          </el-form-item>
        </el-col>
      </el-row>
      <el-divider content-position="left">内存配置</el-divider>
      <el-row :gutter="16">
        <el-col :span="8">
          <el-form-item label="数据库总内存 (-M)">
            <el-input v-model="form.db_memory" placeholder="如 64G，按 SGA:PGA=80:20 分配" @input="onDbMemoryInput" />
          </el-form-item>
        </el-col>
        <el-col :span="8">
          <el-form-item label="SGA_TARGET (-S)">
            <el-input v-model="form.sga_target" :placeholder="sgaPlaceholder" @input="onSgaInput" />
          </el-form-item>
        </el-col>
        <el-col :span="8">
          <el-form-item label="PGA_AGGREGATE_TARGET (-G)">
            <el-input v-model="form.pga_target" :placeholder="pgaPlaceholder" @input="onPgaInput" />
          </el-form-item>
        </el-col>
      </el-row>
    </el-card>

    <!-- 存储配置 -->
    <el-card shadow="never" class="section-card">
      <template #header><span class="section-title">存储配置</span></template>
      <template v-if="isASM">
        <el-row :gutter="16">
          <el-col :span="8">
            <el-form-item label="ASM 数据磁盘组 (-A)">
              <el-input v-model="form.data_asm_group" />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="ASM 归档磁盘组 (-a)">
              <el-input v-model="form.arch_asm_group" />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="备份目录 (-b)">
              <el-input v-model="form.backup_dir" />
            </el-form-item>
          </el-col>
        </el-row>
      </template>
      <template v-else>
        <el-row :gutter="16">
          <el-col :span="8">
            <el-form-item label="数据目录 (-D)">
              <el-input v-model="form.oradata_dir" />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="归档目录">
              <el-input v-model="form.archive_dir" />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="备份目录 (-b)">
              <el-input v-model="form.backup_dir" />
            </el-form-item>
          </el-col>
        </el-row>
      </template>
    </el-card>

    <!-- 执行步骤 -->
    <el-card shadow="never" class="section-card">
      <template #header>
        <div style="display: flex; justify-content: space-between; align-items: center; width: 100%">
          <span class="section-title">执行步骤</span>
          <div style="display: flex; gap: 8px">
            <el-button size="small" text @click="toggleAllSteps(true)">全选</el-button>
            <el-button size="small" text @click="toggleAllSteps(false)">全不选</el-button>
          </div>
        </div>
      </template>
      <div class="steps-grid">
        <div
          v-for="step in stepOptions" :key="step.value"
          class="step-item" :class="{ active: form.steps.includes(step.value) }"
          @click="toggleStep(step.value)"
        >
          <div class="step-check">{{ form.steps.includes(step.value) ? '✓' : '' }}</div>
          <div class="step-info">
            <div class="step-label">{{ step.value }}</div>
            <div class="step-desc">{{ step.desc }}</div>
          </div>
        </div>
      </div>
      <el-divider />
      <el-checkbox v-model="form.restart_after">优化完成后重启数据库 (-z)</el-checkbox>
    </el-card>
    </el-form>

    <!-- 操作按钮 -->
    <div class="action-bar">
      <el-button type="primary" size="large" @click="drawerVisible = true">生成命令</el-button>
      <el-button size="large" @click="resetForm">重置</el-button>
    </div>

    <!-- 底部抽屉 -->
    <el-drawer v-model="drawerVisible" direction="rtl" size="50%" title="生成结果">
      <template v-if="generatedCommand">
        <CommandSteps v-if="generatedSteps.length" :steps="generatedSteps" />
        <el-divider v-if="generatedSteps.length" />
        <div class="script-options">
          <div class="tags-area">
            <el-tag v-for="tag in paramTags" :key="tag" size="small" type="info" style="margin: 2px">{{ tag }}</el-tag>
          </div>
          <div class="download-btns">
            <el-button size="small" @click="copyCommand">
              <el-icon><CopyDocument /></el-icon> 复制
            </el-button>
            <el-button size="small" @click="downloadScript">
              <el-icon><Download /></el-icon> .sh
            </el-button>
          </div>
        </div>
        <CodeBlock :code="generatedCommand" label="优化命令" />
      </template>
      <template #footer>
        <div class="drawer-footer">
          <el-button type="primary" :loading="saving" @click="handleSave">保存到历史</el-button>
        </div>
      </template>
    </el-drawer>
  </div>
</template>

<script setup lang="ts">
import { reactive, computed, ref } from 'vue'
import { ElMessage } from 'element-plus'
import { Download, CopyDocument } from '@element-plus/icons-vue'
import { generateOptimizerCommand } from '@/api/optimizer'
import CommandSteps from '@/components/common/CommandSteps.vue'
import CodeBlock from '@/components/common/CodeBlock.vue'

const stepOptions = [
  { value: 'omf', desc: 'OMF + 归档路径' },
  { value: 'redolog', desc: '在线重做日志' },
  { value: 'backup', desc: 'RMAN 备份脚本' },
  { value: 'para', desc: '核心参数优化' },
  { value: 'sqlnet', desc: 'sqlnet.ora' },
  { value: 'glogin', desc: 'glogin.sql' },
]

const ALL_STEPS = stepOptions.map(s => s.value)
const DEFAULTS: Record<string, any> = {
  db_name: 'orcl', mode: 'rac', oracle_user: 'oracle',
  oracle_home: '/u01/app/oracle/product/19.3.0/db',
  grid_home: '/u01/app/19.3.0/grid',
  redosize: 2048, processes: 3000, open_cursors: 1500,
  session_cached_cursors: 300, parallel_max_servers: 64,
  undo_retention: 10800, db_files: 5000,
  db_memory: '', sga_target: '', pga_target: '',
  data_asm_group: 'DATA', arch_asm_group: 'ARCH',
  oradata_dir: '/oradata', archive_dir: '/oradata/arch',
  backup_dir: '/backup',
}

const FLAG_MAP: [string, string][] = [
  ['db_name', '-d'], ['mode', '-m'], ['oracle_user', '-u'],
  ['oracle_home', '-o'], ['grid_home', '-g'],
  ['redosize', '-r'], ['processes', '-p'], ['open_cursors', '-c'],
  ['session_cached_cursors', '-P'], ['parallel_max_servers', '-R'],
  ['undo_retention', '-U'], ['db_files', '-F'],
  ['db_memory', '-M'], ['sga_target', '-S'], ['pga_target', '-G'],
  ['data_asm_group', '-A'], ['arch_asm_group', '-a'],
  ['backup_dir', '-b'], ['oradata_dir', '-D'],
]

const form = reactive({
  db_name: 'orcl', mode: 'rac' as string, oracle_user: 'oracle',
  oracle_home: '/u01/app/oracle/product/19.3.0/db',
  grid_home: '/u01/app/19.3.0/grid',
  redosize: 2048, processes: 3000, open_cursors: 1500,
  session_cached_cursors: 300, parallel_max_servers: 64,
  undo_retention: 10800, db_files: 5000,
  db_memory: '', sga_target: '', pga_target: '',
  data_asm_group: 'DATA', arch_asm_group: 'ARCH',
  oradata_dir: '/oradata', archive_dir: '/oradata/arch',
  backup_dir: '/backup',
  steps: [...ALL_STEPS],
  restart_after: false,
})

const saving = ref(false)
const drawerVisible = ref(false)

const isASM = computed(() => form.mode === 'rac' || form.mode === 'standalone')

function parseMemMB(val: string): number {
  if (!val) return 0
  const upper = val.toUpperCase()
  const num = parseFloat(upper.replace(/[MG]/g, ''))
  if (isNaN(num) || num <= 0) return 0
  return upper.includes('G') ? Math.round(num * 1024) : Math.round(num)
}

const sgaPlaceholder = computed(() => {
  const m = parseMemMB(form.db_memory)
  return m > 0 ? `(-M 分配) ${Math.round(m * 0.8)}M` : '优先级高于 -M，如 16G'
})

const pgaPlaceholder = computed(() => {
  const m = parseMemMB(form.db_memory)
  return m > 0 ? `(-M 分配) ${Math.round(m * 0.2)}M` : '优先级高于 -M，如 4G'
})

function onDbMemoryInput() {
  // no-op: placeholders auto-update via computed
}

function onSgaInput() {
  if (form.sga_target.trim()) form.db_memory = ''
}

function onPgaInput() {
  if (form.pga_target.trim()) form.db_memory = ''
}

function toggleStep(step: string) {
  const idx = form.steps.indexOf(step)
  if (idx >= 0) form.steps.splice(idx, 1)
  else form.steps.push(step)
}

function toggleAllSteps(state: boolean) {
  form.steps = state ? [...ALL_STEPS] : []
}

function resetForm() {
  Object.assign(form, {
    ...DEFAULTS,
    steps: [...ALL_STEPS],
    restart_after: false,
  })
}

const { generatedCommand, paramTags } = (() => {
  const result = computed(() => {
    const parts = ['./Oracle_19c_Optimize.sh']
    const tags: string[] = []
    const asm = isASM.value

    for (const [field, flag] of FLAG_MAP) {
      if (!asm && (field === 'data_asm_group' || field === 'arch_asm_group')) continue
      if (asm && field === 'oradata_dir') continue

      const val = (form as any)[field]
      const valStr = String(val ?? '')
      const defStr = String(DEFAULTS[field] ?? '')
      if (valStr && valStr !== defStr) {
        parts.push(`${flag} ${valStr}`)
        tags.push(`${flag} ${valStr}`)
      }
    }

    if (form.steps.length > 0 && form.steps.length < ALL_STEPS.length) {
      parts.push(`-s ${form.steps.join(',')}`)
    }
    if (form.steps.length === ALL_STEPS.length) tags.push('all steps')
    else tags.push(...form.steps)

    if (form.restart_after) {
      parts.push('-z')
      tags.push('-z')
    }

    return { cmd: parts.join(' \\\n    '), tags }
  })

  return {
    generatedCommand: computed(() => result.value.cmd),
    paramTags: computed(() => result.value.tags),
  }
})()

const STEP_DESCRIPTIONS: Record<string, string> = {
  db_name: '指定数据库实例名为 {value}',
  mode: '安装模式: {value}',
  oracle_user: '使用 {value} 用户执行优化',
  oracle_home: 'Oracle Home 路径: {value}',
  grid_home: 'Grid Home 路径: {value}',
  redosize: '调整 Redo 日志大小为 {value} MB',
  processes: '设置 processes 参数为 {value}',
  open_cursors: '设置 open_cursors 参数为 {value}',
  session_cached_cursors: '设置 session_cached_cursors 为 {value}',
  parallel_max_servers: '设置 parallel_max_servers 为 {value}',
  undo_retention: '设置 undo_retention 为 {value} 秒',
  db_files: '设置 db_files 为 {value}',
  db_memory: '配置数据库总内存为 {value}（SGA:PGA = 80:20 自动分配）',
  sga_target: '设置 SGA_TARGET 为 {value}',
  pga_target: '设置 PGA_AGGREGATE_TARGET 为 {value}',
  data_asm_group: '使用 ASM 磁盘组 {value} 存放数据文件',
  arch_asm_group: '使用 ASM 磁盘组 {value} 存放归档日志',
  backup_dir: '备份目录: {value}',
  oradata_dir: '数据文件目录: {value}',
}

const STEP_NAMES: Record<string, string> = {
  omf: '配置 OMF 和归档路径',
  redolog: '调整在线重做日志组大小和数量',
  backup: '生成 RMAN 备份配置脚本',
  para: '优化核心初始化参数',
  sqlnet: '配置 sqlnet.ora 网络参数',
  glogin: '配置 glogin.sql 登录脚本',
}

const generatedSteps = computed(() => {
  const steps: string[] = []
  const asm = isASM.value

  const activeSteps = form.steps.map(s => STEP_NAMES[s]).filter(Boolean)
  if (activeSteps.length) {
    steps.push('将执行以下优化步骤: ' + activeSteps.join('、'))
  }

  for (const [field] of FLAG_MAP) {
    if (!asm && (field === 'data_asm_group' || field === 'arch_asm_group')) continue
    if (asm && field === 'oradata_dir') continue
    const val = String((form as any)[field] ?? '')
    const def = String(DEFAULTS[field] ?? '')
    if (val && val !== def && STEP_DESCRIPTIONS[field]) {
      steps.push(STEP_DESCRIPTIONS[field].replace('{value}', val))
    }
  }

  if (form.restart_after) {
    steps.push('优化完成后自动重启数据库')
  }

  return steps
})

async function copyCommand() {
  try {
    await navigator.clipboard.writeText(generatedCommand.value)
    ElMessage.success('已复制')
  } catch {
    ElMessage.error('复制失败')
  }
}

async function handleSave() {
  saving.value = true
  try {
    await generateOptimizerCommand({ ...form })
    ElMessage.success('已保存到历史记录')
  } catch {
    // handled by interceptor
  } finally {
    saving.value = false
  }
}

async function downloadScript() {
  try {
    const token = localStorage.getItem('token')
    const res = await fetch('/api/v1/optimizer/download-script', {
      headers: { Authorization: `Bearer ${token}` },
    })
    if (!res.ok) {
      const data = await res.json()
      ElMessage.error(data.detail || '下载失败')
      return
    }
    const blob = await res.blob()
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = 'Oracle_19c_Optimize.sh'
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    URL.revokeObjectURL(url)
  } catch {
    ElMessage.error('下载失败')
  }
}
</script>

<style scoped>
.optimizer-page { max-width: 1400px; margin: 0 auto; }
.page-header { margin-bottom: 20px; }
.page-header h2 { font-size: 18px; font-weight: 600; }
.page-desc { font-size: 13px; color: var(--el-text-color-secondary); }

.section-card { margin-bottom: 16px; }
.section-title { font-size: 14px; font-weight: 600; }

.preset-tags { display: flex; gap: 6px; margin-top: 4px; }
.preset-tag { cursor: pointer; }

.steps-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 10px; }
.step-item {
  display: flex; align-items: center; gap: 10px;
  padding: 10px 14px; border: 1px solid var(--el-border-color-light);
  border-radius: 6px; cursor: pointer; transition: all 0.2s; user-select: none;
}
.step-item:hover { border-color: var(--el-color-primary); background: var(--el-color-primary-light-9); }
.step-item.active { border-color: var(--el-color-success); background: var(--el-color-success-light-9); }
.step-check {
  width: 18px; height: 18px; border: 2px solid var(--el-border-color);
  border-radius: 4px; display: flex; align-items: center; justify-content: center;
  font-size: 12px; color: transparent; flex-shrink: 0; transition: all 0.2s;
}
.step-item.active .step-check { border-color: var(--el-color-success); background: var(--el-color-success); color: #fff; }
.step-label { font-size: 13px; font-weight: 500; }
.step-desc { font-size: 11px; color: var(--el-text-color-secondary); }

.action-bar {
  display: flex; gap: 12px; padding: 16px 0;
  justify-content: center;
}

.script-options {
  display: flex; justify-content: space-between; align-items: center;
  margin-bottom: 12px;
}
.tags-area { display: flex; flex-wrap: wrap; gap: 4px; }
.download-btns { display: flex; gap: 6px; }
.drawer-footer { display: flex; gap: 8px; }
</style>
