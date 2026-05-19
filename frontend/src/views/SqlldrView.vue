<template>
  <div class="sqlldr-page">
    <div class="page-header">
      <h2>SQL*Loader 数据加载</h2>
      <span class="page-desc">Oracle SQL*Loader 数据导入命令与控制文件生成器</span>
    </div>

    <el-form :model="form" label-width="150px" ref="formRef">
      <CollapsibleSection title="基础参数" :optional="false">
        <el-row :gutter="16">
          <el-col :span="8">
            <el-form-item label="目标表名" required>
              <el-input v-model="form.table_name" placeholder="如 SCOTT.EMP" />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="数据文件" required>
              <el-input v-model="form.data_file" placeholder="如 /data/load/emp.csv" />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="加载方式">
              <el-select v-model="form.load_method" style="width: 100%">
                <el-option label="INSERT（默认）" value="insert" />
                <el-option label="APPEND（追加）" value="append" />
                <el-option label="REPLACE（替换）" value="replace" />
                <el-option label="TRUNCATE（清空后加载）" value="truncate" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
      </CollapsibleSection>

      <CollapsibleSection title="字段格式">
        <el-row :gutter="16">
          <el-col :span="8">
            <el-form-item label="字段分隔符">
              <el-input v-model="form.fields_terminated_by" placeholder="默认逗号 ," />
              <div class="param-hint">常用: , | \t ;</div>
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="字段包围符">
              <el-input v-model="form.fields_optionally_enclosed_by" placeholder='默认双引号 "' />
              <div class="param-hint">OPTIONALLY ENCLOSED BY</div>
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="行终止符">
              <el-input v-model="form.lines_terminated_by" placeholder="默认 \\n" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="16">
          <el-col :span="8">
            <el-form-item label="跳过行数">
              <el-input-number v-model="form.skip_rows" :min="0" :max="9999" style="width: 100%" controls-position="right" />
              <div class="param-hint">跳过文件头部行（如 CSV 标题行）</div>
            </el-form-item>
          </el-col>
        </el-row>
      </CollapsibleSection>

      <CollapsibleSection title="列定义" :optional="true">
        <el-form-item label="列定义">
          <el-input v-model="form.columns" type="textarea" :rows="4" placeholder="如: EMPNO INTEGER EXTERNAL, ENAME CHAR(20), HIREDATE DATE 'YYYY-MM-DD'" />
          <div class="param-hint">留空将由 SQL*Loader 自动推断。建议显式指定以避免数据错位。</div>
        </el-form-item>
      </CollapsibleSection>

      <CollapsibleSection title="性能选项" :optional="true">
        <el-row :gutter="16">
          <el-col :span="6">
            <el-form-item><el-checkbox v-model="form.direct_path">Direct Path</el-checkbox></el-form-item>
          </el-col>
          <el-col :span="6">
            <el-form-item><el-checkbox v-model="form.parallel">Parallel</el-checkbox></el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="16">
          <el-col :span="8">
            <el-form-item label="BINDSIZE">
              <el-input v-model="form.bindsize" placeholder="如 1048576" />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="ROWS">
              <el-input v-model="form.rows" placeholder="如 10000" />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="ERRORS">
              <el-input v-model="form.errors" placeholder="如 50" />
              <div class="param-hint">允许的最大错误行数</div>
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="16">
          <el-col :span="8">
            <el-form-item label="DISCARDMAX">
              <el-input v-model="form.discardmax" placeholder="如 999" />
              <div class="param-hint">允许的最大丢弃行数</div>
            </el-form-item>
          </el-col>
        </el-row>
      </CollapsibleSection>

      <CollapsibleSection title="日志与文件" :optional="true">
        <el-row :gutter="16">
          <el-col :span="8">
            <el-form-item label="LOG 文件">
              <el-input v-model="form.log_file" placeholder="如 /data/load/emp.log" />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="BAD 文件">
              <el-input v-model="form.bad_file" placeholder="如 /data/load/emp.bad" />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="DISCARD 文件">
              <el-input v-model="form.discard_file" placeholder="如 /data/load/emp.dsc" />
            </el-form-item>
          </el-col>
        </el-row>
      </CollapsibleSection>

      <CollapsibleSection title="数据库连接">
        <el-row :gutter="16">
          <el-col :span="8">
            <el-form-item label="主机">
              <el-input v-model="form.host" placeholder="localhost" />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="端口">
              <el-input-number v-model="form.port" :min="1" :max="65535" style="width: 100%" controls-position="right" />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="连接类型">
              <el-radio-group v-model="form.connect_type">
                <el-radio-button value="service">Service Name</el-radio-button>
                <el-radio-button value="sid">SID</el-radio-button>
              </el-radio-group>
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="16">
          <el-col :span="8">
            <el-form-item label="用户名">
              <el-input v-model="form.username" placeholder="system" />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="密码">
              <el-input v-model="form.password" type="password" show-password placeholder="数据库密码" />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item :label="form.connect_type === 'service' ? 'Service Name' : 'SID'">
              <el-input v-model="form.service_name" :placeholder="form.connect_type === 'service' ? 'orcl' : ''" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="16">
          <el-col :span="8">
            <el-form-item label="ORACLE_HOME">
              <el-input v-model="form.oracle_home" placeholder="/u01/app/oracle/product/19.3.0/dbhome_1" />
            </el-form-item>
          </el-col>
        </el-row>
      </CollapsibleSection>

      <el-form-item>
        <el-button type="primary" size="large" :loading="loading" @click="handleGenerate">
          <el-icon><Cpu /></el-icon> 生成命令
        </el-button>
      </el-form-item>
    </el-form>

    <!-- Result Drawer -->
    <el-drawer v-model="showResult" title="生成结果" direction="rtl" size="50%">
      <template v-if="result">
        <ValidationPanel :warnings="normalizedWarnings" :recommendations="result.recommendations || []" />
        <el-divider v-if="(result.warnings?.length || 0) > 0 || (result.recommendations?.length || 0) > 0" />

        <div class="script-options">
          <el-button-group>
            <el-button :type="activeTab === 'control' ? 'primary' : ''" @click="activeTab = 'control'">控制文件 (.ctl)</el-button>
            <el-button :type="activeTab === 'command' ? 'primary' : ''" @click="activeTab = 'command'">命令</el-button>
            <el-button :type="activeTab === 'script' ? 'primary' : ''" @click="activeTab = 'script'">Shell 脚本</el-button>
          </el-button-group>
          <div class="download-btns">
            <el-button size="small" @click="handleDownload('ctl')">
              <el-icon><Download /></el-icon> .ctl
            </el-button>
            <el-button size="small" @click="handleDownload('sh')">
              <el-icon><Download /></el-icon> .sh
            </el-button>
          </div>
        </div>
        <CodeBlock :code="currentCode" :label="tabLabels[activeTab]" />
      </template>
    </el-drawer>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed } from 'vue'
import { ElMessage } from 'element-plus'
import { Download } from '@element-plus/icons-vue'
import CollapsibleSection from '@/components/common/CollapsibleSection.vue'
import ValidationPanel from '@/components/generator/ValidationPanel.vue'
import CodeBlock from '@/components/common/CodeBlock.vue'
import { generateSqlldr } from '@/api/sqlldr'
import { downloadFile, timestamp } from '@/utils/helpers'

const loading = ref(false)
const showResult = ref(false)
const result = ref<any>(null)
const activeTab = ref<'control' | 'command' | 'script'>('control')

const form = reactive({
  table_name: '',
  data_file: '',
  load_method: 'insert',
  fields_terminated_by: ',',
  fields_optionally_enclosed_by: '"',
  lines_terminated_by: '\\n',
  skip_rows: 0,
  columns: '',
  direct_path: false,
  parallel: false,
  bindsize: '',
  rows: '',
  errors: '',
  discardmax: '',
  log_file: '',
  bad_file: '',
  discard_file: '',
  host: 'localhost',
  port: 1521,
  username: '',
  password: '',
  service_name: '',
  sid: '',
  connect_type: 'service',
  oracle_home: '/u01/app/oracle/product/19.3.0/dbhome_1',
})

const tabLabels: Record<string, string> = {
  control: '控制文件 (.ctl)',
  command: 'sqlldr 命令',
  script: 'Shell 脚本',
}

const currentCode = computed(() => {
  if (!result.value) return ''
  switch (activeTab.value) {
    case 'control': return result.value.control_file || ''
    case 'command': return result.value.command || ''
    case 'script': return result.value.script || ''
    default: return ''
  }
})

const normalizedWarnings = computed(() => {
  if (!result.value?.warnings) return []
  return result.value.warnings.map((w: any) => ({
    level: w.level || 'info',
    field: w.field || '',
    message: w.message || '',
    suggestion: w.suggestion || null,
  }))
})

async function handleGenerate() {
  if (!form.table_name.trim()) { ElMessage.warning('请输入目标表名'); return }
  if (!form.data_file.trim()) { ElMessage.warning('请输入数据文件路径'); return }

  loading.value = true
  try {
    const { data } = await generateSqlldr(form)
    result.value = data
    showResult.value = true
    if (data.warnings?.some((w: any) => w.level === 'error')) {
      ElMessage.warning('命令已生成，但存在参数错误，请检查')
    } else {
      ElMessage.success('命令生成成功')
    }
  } catch { /* handled by interceptor */ }
  finally { loading.value = false }
}

function handleDownload(type: string) {
  if (!result.value) return
  const ts = timestamp()
  const baseName = (form.table_name || 'load').toLowerCase().replace('.', '_')
  if (type === 'ctl') {
    downloadFile(result.value.control_file || '', `${baseName}_${ts}.ctl`)
  } else if (type === 'sh') {
    downloadFile(result.value.script || '', `sqlldr_${baseName}_${ts}.sh`)
  }
}
</script>

<style scoped>
.sqlldr-page { max-width: 1400px; margin: 0 auto; }
.page-header { margin-bottom: 20px; }
.page-header h2 { font-size: 18px; font-weight: 600; }
.page-desc { font-size: 13px; color: var(--el-text-color-secondary); }
.param-hint { font-size: 11px; color: var(--text-tertiary); margin-top: 4px; line-height: 1.4; }

.script-options {
  display: flex; justify-content: space-between; align-items: center;
  margin-bottom: 12px;
}
.download-btns { display: flex; gap: 6px; }
</style>
