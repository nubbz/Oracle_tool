<template>
  <div class="params-form">
    <CollapsibleSection title="基础参数" :optional="false">
      <el-row :gutter="16">
        <el-col :span="12">
          <el-form-item label="Directory" required>
            <el-input v-model="form.directory" placeholder="DP_DIR" />
            <div class="param-hint">Oracle Directory 对象名称（必填）</div>
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item label="Dump File">
            <el-input v-model="form.dumpfile" placeholder="backup_%U.dmp" />
          </el-form-item>
        </el-col>
      </el-row>
      <el-row :gutter="16">
        <el-col :span="12">
          <el-form-item label="Log File">
            <el-input v-model="form.logfile" placeholder="import.log" />
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item label="Content">
            <el-select v-model="form.content" style="width: 100%">
              <el-option label="ALL（全部）" value="ALL" />
              <el-option label="METADATA_ONLY（仅元数据）" value="METADATA_ONLY" />
              <el-option label="DATA_ONLY（仅数据）" value="DATA_ONLY" />
            </el-select>
          </el-form-item>
        </el-col>
      </el-row>
      <el-row :gutter="16">
        <el-col :span="12">
          <el-form-item label="Job Name">
            <el-input v-model="form.jobName" placeholder="如 IMPDP_SCOTT_20260508" />
            <div class="param-hint">指定作业名，便于 ATTACH 恢复中断的作业</div>
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item label="Logtime">
            <el-select v-model="form.logtime" style="width: 100%" clearable placeholder="不启用">
              <el-option label="ALL（所有消息加时间戳）" value="ALL" />
              <el-option label="HEADER（仅头部）" value="HEADER" />
              <el-option label="LOGFILE（仅日志文件）" value="LOGFILE" />
              <el-option label="STATUS（仅状态输出）" value="STATUS" />
            </el-select>
            <div class="param-hint">日志消息添加时间戳（12c+）</div>
          </el-form-item>
        </el-col>
      </el-row>
      <el-form-item>
        <el-checkbox v-model="form.metrics">METRICS（记录导入性能指标）</el-checkbox>
      </el-form-item>
    </CollapsibleSection>

    <CollapsibleSection title="导入范围">
      <el-form-item label="Schemas">
        <TagInput v-model="form.schemas" placeholder="输入 Schema 名称" />
      </el-form-item>
      <el-form-item label="Tables">
        <TagInput v-model="form.tables" placeholder="输入 表名 或 Schema.表名" />
      </el-form-item>
    </CollapsibleSection>

    <CollapsibleSection title="映射参数" :optional="true">
      <el-form-item label="REMAP_SCHEMA">
        <el-input v-model="form.remapSchema" placeholder="old_schema:new_schema" />
        <div class="param-hint">格式：源Schema:目标Schema</div>
      </el-form-item>
      <el-form-item label="REMAP_TABLESPACE">
        <el-input v-model="form.remapTablespace" placeholder="old_tbs:new_tbs" />
      </el-form-item>
      <el-form-item label="REMAP_DATAFILE">
        <el-input v-model="form.remapDatafile" placeholder="/old/path:/new/path" />
      </el-form-item>
      <el-form-item label="REMAP_TABLE">
        <el-input v-model="form.remapTable" placeholder="old_table:new_table" />
        <div class="param-hint">格式：源表名:目标表名，如 EMP:EMP_BAK</div>
      </el-form-item>
    </CollapsibleSection>

    <CollapsibleSection title="导入控制" :optional="true">
      <el-form-item label="TABLE_EXISTS_ACTION">
        <el-select v-model="form.tableExistsAction" style="width: 100%" clearable placeholder="表已存在时的处理方式">
          <el-option label="SKIP（跳过）" value="SKIP" />
          <el-option label="APPEND（追加）" value="APPEND" />
          <el-option label="TRUNCATE（清空后导入）" value="TRUNCATE" />
          <el-option label="REPLACE（删除重建）" value="REPLACE" />
        </el-select>
      </el-form-item>
      <el-form-item>
        <el-checkbox v-model="form.disableArchiveLogging">DISABLE_ARCHIVE_LOGGING</el-checkbox>
      </el-form-item>
    </CollapsibleSection>

    <CollapsibleSection title="过滤条件" :optional="true">
      <el-form-item label="Exclude">
        <div class="exclude-row">
          <el-select v-model="excludeType" placeholder="对象类型" style="width: 160px" @change="excludeType = $event">
            <el-option v-for="t in excludeTypes" :key="t.value" :label="t.label" :value="t.value" />
          </el-select>
          <el-input v-model="excludeName" placeholder="名称条件（可选）" style="width: 200px" />
          <el-button type="primary" :disabled="!excludeType" @click="addExclude">添加</el-button>
        </div>
        <div v-if="form.exclude.length > 0" class="param-examples" style="margin-top: 8px">
          <el-tag v-for="(val, i) in form.exclude" :key="i" closable size="default" @close="form.exclude = form.exclude.filter((_: any, idx: number) => idx !== i)" style="margin: 2px 4px 2px 0">
            {{ excludeLabels[val] || val }}
          </el-tag>
        </div>
      </el-form-item>
      <el-form-item label="Include">
        <div class="exclude-row">
          <el-select v-model="includeType" placeholder="对象类型" style="width: 160px" @change="includeType = $event">
            <el-option v-for="t in excludeTypes" :key="t.value" :label="t.label" :value="t.value" />
          </el-select>
          <el-input v-model="includeName" placeholder="名称条件（可选）" style="width: 200px" />
          <el-button type="primary" :disabled="!includeType" @click="addInclude">添加</el-button>
        </div>
        <div v-if="form.include.length > 0" class="param-examples" style="margin-top: 8px">
          <el-tag v-for="(val, i) in form.include" :key="i" closable size="default" @close="form.include = form.include.filter((_: any, idx: number) => idx !== i)" style="margin: 2px 4px 2px 0">
            {{ excludeLabels[val] || val }}
          </el-tag>
        </div>
      </el-form-item>
    </CollapsibleSection>

    <CollapsibleSection title="Transform" :optional="true">
      <el-form-item label="TRANSFORM">
        <el-input v-model="form.transform" placeholder="SEGMENT_ATTRIBUTES:n:disable_logging:Y" />
      </el-form-item>
      <el-form-item label="SQLFILE">
        <el-input v-model="form.sqlfile" placeholder="dump.sql（仅生成DDL，不执行导入）" />
      </el-form-item>
      <el-form-item label="PARTITION_OPTIONS">
        <el-select v-model="form.partitionOptions" style="width: 100%" clearable>
          <el-option label="NONE" value="NONE" />
          <el-option label="DEPARTITION" value="DEPARTITION" />
          <el-option label="MERGE" value="MERGE" />
        </el-select>
      </el-form-item>
      <el-form-item label="DATA_OPTIONS">
        <el-input v-model="form.dataOptions" placeholder="DISABLE_APPEND_HINT" />
      </el-form-item>
    </CollapsibleSection>

    <CollapsibleSection title="性能与分片" :optional="true">
      <el-row :gutter="16">
        <el-col :span="8">
          <el-form-item label="Parallel">
            <el-input-number v-model="form.parallel" :min="1" :max="32" style="width: 100%" controls-position="right" />
          </el-form-item>
        </el-col>
        <el-col :span="8">
          <el-form-item label="Compression">
            <el-select v-model="form.compression" style="width: 100%">
              <el-option label="NONE" value="NONE" />
              <el-option label="ALL" value="ALL" />
              <el-option label="DATA_ONLY" value="DATA_ONLY" />
              <el-option label="METADATA_ONLY" value="METADATA_ONLY" />
            </el-select>
          </el-form-item>
        </el-col>
      </el-row>
    </CollapsibleSection>

    <CollapsibleSection title="Flashback" :optional="true">
      <el-row :gutter="16">
        <el-col :span="12">
          <el-form-item label="Flashback SCN">
            <el-input v-model="form.flashbackScn" placeholder="如 123456789" />
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item label="Flashback Time">
            <el-input v-model="form.flashbackTime" placeholder="时间戳" />
          </el-form-item>
        </el-col>
      </el-row>
    </CollapsibleSection>

    <CollapsibleSection title="网络导入" :optional="true">
      <el-form-item label="NETWORK_LINK">
        <el-input v-model="form.networkLink" placeholder="远程数据库连接名" />
        <div class="param-hint">
          通过网络直接从源库导入，无需 dump 文件
          <el-link type="primary" :underline="false" style="font-size: 11px; vertical-align: baseline" @click="showNetworkGuide = true">查看配置步骤</el-link>
        </div>
      </el-form-item>
      <el-form-item>
        <el-checkbox v-model="form.reuseDatafiles">REUSE_DATAFILES</el-checkbox>
      </el-form-item>
      <el-form-item>
        <el-checkbox v-model="form.reuseDumpfiles">REUSE_DUMPFILES</el-checkbox>
      </el-form-item>
    </CollapsibleSection>

    <!-- 网络导入参考文档 -->
    <el-dialog v-model="showNetworkGuide" title="网络导入（NETWORK_LINK）配置指南" width="640px" :close-on-click-modal="true">
      <div class="guide-content">
        <h4>概述</h4>
        <p>NETWORK_LINK 允许 impdp 通过 Database Link 直接从源数据库读取数据并导入目标库，无需生成中间 dump 文件。适用于跨库迁移、数据同步等场景。</p>

        <h4>配置步骤</h4>
        <div class="guide-step">
          <div class="step-num">1</div>
          <div class="step-body">
            <strong>在源库创建 TNS 名称</strong>
            <p>确认源库的 <code>tnsnames.ora</code> 中已有目标库可访问的服务名，或直接在创建 DB Link 时使用连接描述符。</p>
          </div>
        </div>
        <div class="guide-step">
          <div class="step-num">2</div>
          <div class="step-body">
            <strong>在目标库创建 Database Link</strong>
            <pre class="code-block">-- 基础语法
CREATE DATABASE LINK remote_link
  CONNECT TO remote_user IDENTIFIED BY remote_password
  USING '(DESCRIPTION=
           (ADDRESS=(PROTOCOL=TCP)(HOST=源库IP)(PORT=1521))
           (CONNECT_DATA=(SERVICE_NAME=源库服务名))
         )';

-- 或使用 TNS 别名
CREATE DATABASE LINK remote_link
  CONNECT TO remote_user IDENTIFIED BY remote_password
  USING 'SOURCE_TNS_NAME';

-- 验证连接
SELECT * FROM dual@remote_link;</pre>
          </div>
        </div>
        <div class="guide-step">
          <div class="step-num">3</div>
          <div class="step-body">
            <strong>执行网络导入</strong>
            <pre class="code-block">-- 导入整个 Schema
impdp system/password DIRECTORY=DP_DIR \
  NETWORK_LINK=remote_link \
  SCHEMAS=hr \
  REMAP_SCHEMA=hr:hr_new

-- 仅导入元数据（用于数据比对）
impdp system/password DIRECTORY=DP_DIR \
  NETWORK_LINK=remote_link \
  SCHEMAS=hr \
  CONTENT=METADATA_ONLY \
  SQLFILE=hr_metadata.sql</pre>
          </div>
        </div>
        <div class="guide-step">
          <div class="step-num">4</div>
          <div class="step-body">
            <strong>清理</strong>
            <pre class="code-block">-- 导入完成后删除 DB Link
DROP DATABASE LINK remote_link;</pre>
          </div>
        </div>

        <h4>常用参数组合</h4>
        <el-table :data="networkExamples" size="small" border style="margin-top: 8px">
          <el-table-column prop="scene" label="场景" width="180" />
          <el-table-column prop="params" label="关键参数" />
        </el-table>

        <h4 style="margin-top: 16px">注意事项</h4>
        <ul class="guide-notes">
          <li>NETWORK_LINK 导入时不需要 DUMPFILE，但 DIRECTORY 仍需指定（用于日志和 SQLFILE）</li>
          <li>源库和目标库的字符集应一致，否则可能出现乱码</li>
          <li>网络导入速度受网络带宽限制，大数据量建议先 expdp 导出再 impdp 导入</li>
          <li>需确保目标库到源库的网络连通（非反向）</li>
          <li>CDB 环境下 DB Link 需在对应的 Container 中创建</li>
        </ul>
      </div>
      <template #footer>
        <el-button type="primary" @click="showNetworkGuide = false">知道了</el-button>
      </template>
    </el-dialog>

    <CollapsibleSection title="版本与加密" :optional="true">
      <el-row :gutter="16">
        <el-col :span="12">
          <el-form-item label="Version">
            <el-input v-model="form.version" placeholder="如 12.2" />
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item label="Encryption Password">
            <el-input v-model="form.encryptionPassword" type="password" show-password />
          </el-form-item>
        </el-col>
      </el-row>
    </CollapsibleSection>
  </div>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'
import CollapsibleSection from '@/components/common/CollapsibleSection.vue'
import TagInput from '@/components/common/TagInput.vue'
import { useGeneratorStore } from '@/stores/generatorStore'

const store = useGeneratorStore()
const form = computed(() => store.impdpParams)

const excludeType = ref('')
const excludeName = ref('')
const includeType = ref('')
const includeName = ref('')
const showNetworkGuide = ref(false)

const networkExamples = [
  { scene: '全 Schema 迁移', params: 'SCHEMAS + REMAP_SCHEMA' },
  { scene: '仅元数据比对', params: 'CONTENT=METADATA_ONLY + SQLFILE' },
  { scene: '仅数据同步', params: 'CONTENT=DATA_ONLY + TABLE_EXISTS_ACTION=APPEND' },
  { scene: '指定表导入', params: 'TABLES=hr.employees,hr.departments' },
]

const excludeTypes = [
  { value: 'TABLE', label: 'TABLE（表）' },
  { value: 'VIEW', label: 'VIEW（视图）' },
  { value: 'INDEX', label: 'INDEX（索引）' },
  { value: 'PROCEDURE', label: 'PROCEDURE（存储过程）' },
  { value: 'FUNCTION', label: 'FUNCTION（函数）' },
  { value: 'PACKAGE', label: 'PACKAGE（包）' },
  { value: 'TRIGGER', label: 'TRIGGER（触发器）' },
  { value: 'SEQUENCE', label: 'SEQUENCE（序列）' },
  { value: 'SYNONYM', label: 'SYNONYM（同义词）' },
  { value: 'GRANT', label: 'GRANT（权限）' },
  { value: 'USER', label: 'USER（用户）' },
  { value: 'TABLESPACE', label: 'TABLESPACE（表空间）' },
  { value: 'DATABASE_LINK', label: 'DATABASE_LINK（DB Link）' },
  { value: 'MATERIALIZED_VIEW', label: 'MATERIALIZED_VIEW（物化视图）' },
  { value: 'TYPE', label: 'TYPE（类型）' },
  { value: 'CONSTRAINT', label: 'CONSTRAINT（约束）' },
  { value: 'REF_CONSTRAINT', label: 'REF_CONSTRAINT（引用约束）' },
  { value: 'STATISTICS', label: 'STATISTICS（统计信息）' },
]

const excludeLabels: Record<string, string> = {}
for (const t of excludeTypes) {
  excludeLabels[t.value] = t.label
}

function buildExcludeVal(type: string, name: string): string {
  if (!name.trim()) return type
  return `${type}:"${name.trim()}"`
}

function addExclude() {
  const val = buildExcludeVal(excludeType.value, excludeName.value)
  form.value.exclude = [...form.value.exclude, val]
  excludeType.value = ''
  excludeName.value = ''
}

function addInclude() {
  const val = buildExcludeVal(includeType.value, includeName.value)
  form.value.include = [...form.value.include, val]
  includeType.value = ''
  includeName.value = ''
}
</script>

<style scoped>
.param-hint { font-size: 11px; color: var(--text-tertiary); margin-top: 4px; line-height: 1.4; }
.param-examples { display: flex; flex-wrap: wrap; align-items: center; gap: 6px; }
.exclude-row { display: flex; gap: 8px; align-items: center; }
.params-form :deep(.el-form-item) { margin-bottom: 16px; }

.guide-content h4 { font-size: 14px; font-weight: 600; margin: 16px 0 8px; color: var(--el-text-color-primary); }
.guide-content h4:first-child { margin-top: 0; }
.guide-content p { font-size: 13px; color: var(--el-text-color-regular); line-height: 1.6; margin: 4px 0; }
.guide-content code { background: var(--el-fill-color-light); padding: 1px 6px; border-radius: 3px; font-size: 12px; color: var(--el-color-primary); }
.code-block { background: #1e1e1e; color: #d4d4d4; padding: 12px 16px; border-radius: 6px; font-size: 12px; line-height: 1.5; overflow-x: auto; margin: 8px 0; font-family: 'Cascadia Code', 'Fira Code', Consolas, monospace; white-space: pre; }
.guide-step { display: flex; gap: 12px; margin: 12px 0; align-items: flex-start; }
.step-num { width: 24px; height: 24px; min-width: 24px; border-radius: 50%; background: var(--el-color-primary); color: #fff; display: flex; align-items: center; justify-content: center; font-size: 12px; font-weight: 600; margin-top: 2px; }
.step-body { flex: 1; }
.step-body strong { font-size: 13px; }
.guide-notes { font-size: 12px; color: var(--el-text-color-regular); padding-left: 18px; margin: 4px 0; }
.guide-notes li { line-height: 1.8; }
</style>
