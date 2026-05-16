<template>
  <div class="rman-view">
    <el-tabs v-model="formTab" type="border-card">
      <el-tab-pane label="备份" name="backup">
        <el-form :model="backupForm" label-width="140px" :rules="backupRules" ref="backupFormRef">
          <CollapsibleSection title="备份类型">
            <el-row :gutter="16">
              <el-col :span="8">
                <el-form-item label="备份类型" prop="backup_type">
                  <el-select v-model="backupForm.backup_type" style="width: 100%">
                    <el-option label="全库备份" value="full" />
                    <el-option label="增量备份" value="incremental" />
                    <el-option label="归档日志备份" value="archivelog" />
                  </el-select>
                </el-form-item>
              </el-col>
              <el-col :span="8" v-if="backupForm.backup_type === 'incremental'">
                <el-form-item label="增量级别">
                  <el-select v-model="backupForm.incremental_level" style="width: 100%">
                    <el-option label="Level 0（全量基线）" :value="0" />
                    <el-option label="Level 1（增量）" :value="1" />
                  </el-select>
                </el-form-item>
              </el-col>
              <el-col :span="8">
                <el-form-item label="备份范围" prop="scope">
                  <el-select v-model="backupForm.scope" style="width: 100%">
                    <el-option label="整个数据库" value="database" />
                    <el-option label="表空间" value="tablespace" />
                    <el-option label="数据文件" value="datafile" />
                    <el-option label="控制文件" value="controlfile" />
                    <el-option label="SPFILE" value="spfile" />
                  </el-select>
                </el-form-item>
              </el-col>
            </el-row>
            <el-row :gutter="16" v-if="backupForm.scope === 'tablespace'">
              <el-col :span="8">
                <el-form-item label="表空间名称" prop="tablespace_name">
                  <el-input v-model="backupForm.tablespace_name" placeholder="如 USERS" />
                </el-form-item>
              </el-col>
            </el-row>
            <el-row :gutter="16" v-if="backupForm.scope === 'datafile'">
              <el-col :span="16">
                <el-form-item label="数据文件路径" prop="datafile_path">
                  <el-input v-model="backupForm.datafile_path" placeholder="如 /u01/app/oracle/oradata/users01.dbf" />
                </el-form-item>
              </el-col>
            </el-row>
          </CollapsibleSection>

          <CollapsibleSection title="通道与格式">
            <el-row :gutter="16">
              <el-col :span="8">
                <el-form-item label="通道数量">
                  <el-input-number v-model="backupForm.channel_count" :min="1" :max="16" />
                </el-form-item>
              </el-col>
              <el-col :span="8">
                <el-form-item label="备份路径">
                  <el-input v-model="backupForm.format_path" placeholder="/backup/rman" />
                </el-form-item>
              </el-col>
              <el-col :span="8">
                <el-form-item label="文件格式">
                  <el-input v-model="backupForm.format_pattern" placeholder="%d_%T_%U" />
                </el-form-item>
              </el-col>
            </el-row>
            <el-row :gutter="16">
              <el-col :span="8">
                <el-form-item label="备份标签 TAG">
                  <el-input v-model="backupForm.tag" placeholder="如 FULL_BACKUP_20260516" />
                </el-form-item>
              </el-col>
              <el-col :span="8">
                <el-form-item label="Section Size">
                  <el-input v-model="backupForm.section_size" placeholder="如 1G（多段备份）" />
                </el-form-item>
              </el-col>
            </el-row>
          </CollapsibleSection>

          <CollapsibleSection title="压缩与加密">
            <el-row :gutter="16">
              <el-col :span="8">
                <el-form-item label="压缩">
                  <el-select v-model="backupForm.compression" style="width: 100%">
                    <el-option label="不压缩" value="NONE" />
                    <el-option label="BASIC（免费）" value="BASIC" />
                    <el-option label="LOW" value="LOW" />
                    <el-option label="MEDIUM" value="MEDIUM" />
                    <el-option label="HIGH" value="HIGH" />
                  </el-select>
                </el-form-item>
              </el-col>
              <el-col :span="8">
                <el-form-item label="加密">
                  <el-select v-model="backupForm.encryption" style="width: 100%">
                    <el-option label="不加密" value="NONE" />
                    <el-option label="透明加密" value="TRANSPARENT" />
                    <el-option label="密码加密" value="PASSWORD" />
                    <el-option label="双模式" value="DUAL" />
                  </el-select>
                </el-form-item>
              </el-col>
              <el-col :span="8" v-if="backupForm.encryption === 'PASSWORD' || backupForm.encryption === 'DUAL'">
                <el-form-item label="加密密码" prop="encryption_password">
                  <el-input v-model="backupForm.encryption_password" type="password" show-password />
                </el-form-item>
              </el-col>
            </el-row>
          </CollapsibleSection>

          <CollapsibleSection title="高级选项">
            <el-row :gutter="16">
              <el-col :span="8">
                <el-form-item label="保留策略">
                  <el-input v-model="backupForm.retention_policy" placeholder="如 REDUNDANCY 3" />
                </el-form-item>
              </el-col>
              <el-col :span="8">
                <el-form-item label="ORACLE_HOME">
                  <el-input v-model="backupForm.oracle_home" />
                </el-form-item>
              </el-col>
            </el-row>
            <el-row :gutter="16">
              <el-col :span="24">
                <el-form-item label="选项">
                  <el-checkbox v-model="backupForm.skip_offline">跳过 OFFLINE</el-checkbox>
                  <el-checkbox v-model="backupForm.skip_readonly">跳过 READONLY</el-checkbox>
                  <el-checkbox v-model="backupForm.delete_input">备份后删除归档日志</el-checkbox>
                  <el-checkbox v-model="backupForm.crosscheck">交叉检查 + 清理过期</el-checkbox>
                  <el-checkbox v-model="backupForm.validate">备份后验证</el-checkbox>
                </el-form-item>
              </el-col>
            </el-row>
          </CollapsibleSection>

          <el-form-item>
            <el-button type="primary" @click="handleBackup" :loading="loading">生成备份命令</el-button>
          </el-form-item>
        </el-form>
      </el-tab-pane>

      <el-tab-pane label="恢复" name="restore">
        <el-form :model="restoreForm" label-width="140px" ref="restoreFormRef">
          <CollapsibleSection title="恢复类型">
            <el-row :gutter="16">
              <el-col :span="8">
                <el-form-item label="恢复类型">
                  <el-select v-model="restoreForm.restore_type" style="width: 100%">
                    <el-option label="整个数据库" value="database" />
                    <el-option label="表空间" value="tablespace" />
                    <el-option label="控制文件" value="controlfile" />
                    <el-option label="SPFILE" value="spfile" />
                    <el-option label="归档日志" value="archivelog" />
                  </el-select>
                </el-form-item>
              </el-col>
              <el-col :span="8" v-if="restoreForm.restore_type === 'tablespace'">
                <el-form-item label="表空间名称">
                  <el-input v-model="restoreForm.tablespace_name" placeholder="如 USERS" />
                </el-form-item>
              </el-col>
            </el-row>
          </CollapsibleSection>

          <CollapsibleSection title="恢复目标（可选）">
            <el-row :gutter="16">
              <el-col :span="8">
                <el-form-item label="基于时间">
                  <el-input v-model="restoreForm.pitr_time" placeholder="2026-05-16 12:00:00" />
                </el-form-item>
              </el-col>
              <el-col :span="8">
                <el-form-item label="基于 SCN">
                  <el-input v-model="restoreForm.pitr_scn" placeholder="如 1234567" />
                </el-form-item>
              </el-col>
              <el-col :span="8">
                <el-form-item label="基于日志序列">
                  <el-input v-model="restoreForm.until_sequence" placeholder="序列号" />
                </el-form-item>
              </el-col>
            </el-row>
            <el-row :gutter="16">
              <el-col :span="8">
                <el-form-item label="备份标签">
                  <el-input v-model="restoreForm.from_tag" placeholder="指定备份 TAG" />
                </el-form-item>
              </el-col>
              <el-col :span="8">
                <el-form-item label="ORACLE_HOME">
                  <el-input v-model="restoreForm.oracle_home" />
                </el-form-item>
              </el-col>
            </el-row>
          </CollapsibleSection>

          <el-form-item>
            <el-button type="primary" @click="handleRestore" :loading="loading">生成恢复命令</el-button>
          </el-form-item>
        </el-form>
      </el-tab-pane>
    </el-tabs>

    <!-- Result Drawer -->
    <el-drawer v-model="showResult" title="生成结果" direction="rtl" size="50%">
      <template v-if="result">
        <ValidationPanel :warnings="normalizedWarnings" :recommendations="result.recommendations || []" />
        <el-divider v-if="(result.warnings?.length || 0) > 0 || (result.recommendations?.length || 0) > 0" />
        <CommandSteps v-if="result.steps?.length" :steps="result.steps" />
        <el-divider v-if="result.steps?.length" />
        <div class="script-options">
          <el-button-group>
            <el-button :type="activeTab === 'command' ? 'primary' : ''" @click="activeTab = 'command'">命令</el-button>
            <el-button :type="activeTab === 'script' ? 'primary' : ''" @click="activeTab = 'script'">Shell脚本</el-button>
          </el-button-group>
          <div class="download-btns">
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
import type { FormInstance } from 'element-plus'
import CollapsibleSection from '@/components/common/CollapsibleSection.vue'
import CommandSteps from '@/components/common/CommandSteps.vue'
import ValidationPanel from '@/components/generator/ValidationPanel.vue'
import CodeBlock from '@/components/common/CodeBlock.vue'
import { generateRmanBackup, generateRmanRestore } from '@/api/rman'
import { useClipboard } from '@/composables/useClipboard'
import { downloadFile, timestamp } from '@/utils/helpers'

const formTab = ref('backup')
const loading = ref(false)
const showResult = ref(false)
const result = ref<any>(null)

const backupFormRef = ref<FormInstance>()
const restoreFormRef = ref<FormInstance>()

const backupRules = {
  backup_type: [{ required: true, message: '请选择备份类型', trigger: 'change' }],
  scope: [{ required: true, message: '请选择备份范围', trigger: 'change' }],
  tablespace_name: [{ required: true, message: '请输入表空间名称', trigger: 'blur' }],
  encryption_password: [{ required: true, message: '请输入加密密码', trigger: 'blur' }],
}

const backupForm = reactive({
  backup_type: 'full',
  scope: 'database',
  incremental_level: 1,
  tablespace_name: '',
  datafile_path: '',
  format_path: '/backup/rman',
  format_pattern: '%d_%T_%U',
  channel_count: 2,
  compression: 'BASIC',
  encryption: 'NONE',
  encryption_algorithm: 'AES128',
  encryption_password: '',
  section_size: '',
  skip_offline: false,
  skip_readonly: false,
  skip_inaccessible: false,
  delete_input: false,
  retention_policy: '',
  tag: '',
  oracle_home: '/u01/app/oracle/product/19.3.0/dbhome_1',
  include_housekeeping: true,
  crosscheck: false,
  validate: false,
})

const restoreForm = reactive({
  restore_type: 'database',
  tablespace_name: '',
  pitr_time: '',
  pitr_scn: '',
  until_sequence: '',
  until_thread: '',
  from_tag: '',
  preview: false,
  validate: false,
  oracle_home: '/u01/app/oracle/product/19.3.0/dbhome_1',
})

async function handleBackup() {
  if (!backupFormRef.value) return
  await backupFormRef.value.validate()
  loading.value = true
  try {
    const { data } = await generateRmanBackup(backupForm)
    result.value = data
    showResult.value = true
  } catch { /* handled by interceptor */ }
  finally { loading.value = false }
}

async function handleRestore() {
  loading.value = true
  try {
    const { data } = await generateRmanRestore(restoreForm)
    result.value = data
    showResult.value = true
  } catch { /* handled by interceptor */ }
  finally { loading.value = false }
}

const { copy } = useClipboard()

const tabLabels: Record<string, string> = { command: 'RMAN 命令', script: 'Shell 脚本' }
const activeTab = ref<'command' | 'script'>('command')

const currentCode = computed(() => {
  if (!result.value) return ''
  return activeTab.value === 'command' ? (result.value.command || '') : (result.value.script || '')
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

function handleDownload(type: string) {
  if (!result.value) return
  const ts = timestamp()
  if (type === 'sh') {
    downloadFile(result.value.script || '', `rman_backup_${ts}.sh`)
  }
}

</script>

<style scoped>
.script-options {
  display: flex; justify-content: space-between; align-items: center;
  margin-bottom: 12px;
}
.download-btns { display: flex; gap: 6px; }
</style>
