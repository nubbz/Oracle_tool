<template>
  <div class="params-form">
    <CollapsibleSection title="基础参数" :optional="false">
      <el-row :gutter="16">
        <el-col :span="12">
          <el-form-item label="Directory" required>
            <el-input v-model="form.directory" placeholder="DP_DIR" />
            <div class="param-examples">
              <el-tag v-for="e in dirExamples" :key="e" size="small" class="example-tag" @click="form.directory = e">{{ e }}</el-tag>
            </div>
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item label="Dump File">
            <el-input v-model="form.dumpfile" placeholder="backup_%U.dmp" />
            <div class="param-examples">
              <el-tag v-for="e in dumpExamples" :key="e" size="small" class="example-tag" @click="form.dumpfile = e">{{ e }}</el-tag>
            </div>
          </el-form-item>
        </el-col>
      </el-row>
      <el-row :gutter="16">
        <el-col :span="12">
          <el-form-item label="Log File">
            <el-input v-model="form.logfile" placeholder="export.log" />
            <div class="param-examples">
              <el-tag v-for="e in logExamples" :key="e" size="small" class="example-tag" @click="form.logfile = e">{{ e }}</el-tag>
            </div>
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
            <el-input v-model="form.jobName" placeholder="如 EXPDP_SCOTT_20260508" />
            <div class="param-examples">
              <span class="example-title">示例：</span>
              <el-tag size="small" class="example-tag" @click="form.jobName = 'EXPDP_' + new Date().toISOString().slice(0,10).replace(/-/g,'')">自动生成</el-tag>
            </div>
            <div class="param-hint">指定作业名，便于 ATTACH 恢复中断的作业</div>
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item label="Estimate">
            <el-select v-model="form.estimate" style="width: 100%" clearable placeholder="不估算">
              <el-option label="BLOCKS（按块估算）" value="BLOCKS" />
              <el-option label="STATISTICS（按统计信息估算）" value="STATISTICS" />
            </el-select>
            <div class="param-hint">导出前估算 dump 文件大小</div>
          </el-form-item>
        </el-col>
      </el-row>
    </CollapsibleSection>

    <CollapsibleSection title="导出范围">
      <el-form-item label="Schemas">
        <TagInput v-model="form.schemas" placeholder="输入 Schema 名称后按回车" />
        <div class="param-examples">
          <span class="example-title">示例：</span>
          <el-tag size="small" class="example-tag" @click="form.schemas = ['SCOTT']">SCOTT</el-tag>
          <el-tag size="small" class="example-tag" @click="form.schemas = ['HR']">HR</el-tag>
          <el-tag size="small" class="example-tag" @click="form.schemas = ['SCOTT', 'HR']">多Schema</el-tag>
        </div>
      </el-form-item>
      <el-form-item label="Tables">
        <TagInput v-model="form.tables" placeholder="输入 表名 或 Schema.表名" />
        <div class="param-examples">
          <span class="example-title">示例：</span>
          <el-tag size="small" class="example-tag" @click="form.tables = ['EMP']">EMP</el-tag>
          <el-tag size="small" class="example-tag" @click="form.tables = ['SCOTT.EMP', 'SCOTT.DEPT']">Schema.表名</el-tag>
        </div>
      </el-form-item>
      <el-form-item label="Tablespaces">
        <TagInput v-model="form.tablespaces" placeholder="输入表空间名称" />
        <div class="param-examples">
          <span class="example-title">示例：</span>
          <el-tag size="small" class="example-tag" @click="form.tablespaces = ['USERS']">USERS</el-tag>
          <el-tag size="small" class="example-tag" @click="form.tablespaces = ['TBS_DATA']">TBS_DATA</el-tag>
        </div>
      </el-form-item>
      <el-form-item label="Query">
        <el-input v-model="form.query" type="textarea" :rows="2" placeholder="WHERE created_at > TO_TIMESTAMP('2026-01-01','YYYY-MM-DD')" />
        <div class="param-examples">
          <span class="example-title">常用示例：</span>
          <el-tag v-for="(q, i) in queryExamples" :key="i" size="small" class="example-tag" @click="form.query = q.sql">{{ q.label }}</el-tag>
        </div>
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

    <CollapsibleSection title="性能与分片" :optional="true">
      <el-row :gutter="16">
        <el-col :span="8">
          <el-form-item label="Parallel">
            <el-input-number v-model="form.parallel" :min="1" :max="32" style="width: 100%" controls-position="right" />
            <div class="param-examples">
              <el-tag size="small" class="example-tag" @click="form.parallel = 1">1</el-tag>
              <el-tag size="small" class="example-tag" @click="form.parallel = 4">4</el-tag>
              <el-tag size="small" class="example-tag" @click="form.parallel = 8">8</el-tag>
            </div>
          </el-form-item>
        </el-col>
        <el-col :span="8">
          <el-form-item label="File Size">
            <el-input v-model="form.filesize" placeholder="10G" />
            <div class="param-examples">
              <el-tag size="small" class="example-tag" @click="form.filesize = '10G'">10G</el-tag>
              <el-tag size="small" class="example-tag" @click="form.filesize = '20G'">20G</el-tag>
              <el-tag size="small" class="example-tag" @click="form.filesize = '50G'">50G</el-tag>
            </div>
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
      <el-form-item>
        <el-checkbox v-model="form.reuseDumpfiles">REUSE_DUMPFILES（覆盖已有 dump 文件）</el-checkbox>
      </el-form-item>
    </CollapsibleSection>

    <CollapsibleSection title="Flashback" :optional="true">
      <el-row :gutter="16">
        <el-col :span="12">
          <el-form-item label="Flashback SCN">
            <el-input v-model="form.flashbackScn" placeholder="如 123456789" />
            <div class="param-examples">
              <el-tag size="small" class="example-tag" @click="form.flashbackScn = '123456789'">示例SCN</el-tag>
            </div>
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item label="Flashback Time">
            <el-input v-model="form.flashbackTime" placeholder="TO_TIMESTAMP(日期时间, 格式)" />
            <div class="param-examples">
              <span class="example-title">示例：</span>
              <el-tag v-for="(e, i) in flashbackTimeExamples" :key="i" size="small" class="example-tag" @click="form.flashbackTime = e.val">{{ e.label }}</el-tag>
            </div>
          </el-form-item>
        </el-col>
      </el-row>
    </CollapsibleSection>

    <CollapsibleSection title="加密" :optional="true">
      <el-row :gutter="16">
        <el-col :span="8">
          <el-form-item label="Encryption">
            <el-select v-model="form.encryption" style="width: 100%" clearable>
              <el-option label="ALL" value="ALL" />
              <el-option label="DATA_ONLY" value="DATA_ONLY" />
              <el-option label="METADATA_ONLY" value="METADATA_ONLY" />
              <el-option label="ENCRYPTED_COLUMNS_ONLY" value="ENCRYPTED_COLUMNS_ONLY" />
              <el-option label="NONE" value="NONE" />
            </el-select>
          </el-form-item>
        </el-col>
        <el-col :span="8">
          <el-form-item label="Encryption Password">
            <el-input v-model="form.encryptionPassword" type="password" show-password />
          </el-form-item>
        </el-col>
        <el-col :span="8">
          <el-form-item label="Encryption Mode">
            <el-select v-model="form.encryptionMode" style="width: 100%" clearable>
              <el-option label="PASSWORD" value="PASSWORD" />
              <el-option label="TRANSPARENT" value="TRANSPARENT" />
              <el-option label="DUAL" value="DUAL" />
              <el-option label="NONE" value="NONE" />
            </el-select>
          </el-form-item>
        </el-col>
      </el-row>
      <el-form-item label="Encryption Columns Only">
        <TagInput v-model="form.encryptionColumnsOnly" placeholder="指定仅加密的列" />
      </el-form-item>
    </CollapsibleSection>

    <CollapsibleSection title="传输表空间" :optional="true">
      <el-form-item>
        <el-checkbox v-model="form.transportable">TRANSPORTABLE</el-checkbox>
      </el-form-item>
      <el-form-item>
        <el-checkbox v-model="form.transportFullCheck">TRANSPORT_FULL_CHECK</el-checkbox>
      </el-form-item>
    </CollapsibleSection>

    <CollapsibleSection title="版本兼容" :optional="true">
      <el-form-item label="Version">
        <el-input v-model="form.version" placeholder="如 12.2" />
        <div class="param-examples">
          <el-tag size="small" class="example-tag" @click="form.version = '11.2'">11.2</el-tag>
          <el-tag size="small" class="example-tag" @click="form.version = '12.2'">12.2</el-tag>
          <el-tag size="small" class="example-tag" @click="form.version = '19.0'">19.0</el-tag>
        </div>
        <div class="param-hint">指定目标数据库版本，用于跨版本导出</div>
      </el-form-item>
    </CollapsibleSection>
  </div>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'
import CollapsibleSection from '@/components/common/CollapsibleSection.vue'
import TagInput from '@/components/common/TagInput.vue'
import { useGeneratorStore } from '@/stores/generatorStore'

const store = useGeneratorStore()
const form = computed(() => store.expdpParams)

const excludeType = ref('')
const excludeName = ref('')
const includeType = ref('')
const includeName = ref('')

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

const dirExamples = ['DP_DIR', 'DATA_PUMP_DIR', 'BACKUP_DIR', 'OGG_DIR']
const dumpExamples = ['backup_%U.dmp', 'full_exp_%U.dmp', 'schema_exp_%U.dmp', 'ogg_dir_%U.dmp']
const logExamples = ['export.log', 'expdp_full.log', 'expdp_schema.log']

const queryExamples = [
  { label: '按时间过滤', sql: "WHERE created_at > TO_TIMESTAMP('2026-01-01','YYYY-MM-DD')" },
  { label: '限制行数', sql: 'WHERE rownum <= 10000' },
  { label: '多条件组合', sql: "WHERE status = 'ACTIVE' AND dept_id = 10" },
  { label: 'IN 条件', sql: "WHERE object_type IN ('TABLE','INDEX')" },
  { label: '近30天数据', sql: 'WHERE created_at >= SYSDATE - 30' },
  { label: '模糊匹配', sql: "WHERE owner = 'SCOTT' AND table_name LIKE 'TMP_%'" },
]

const excludeExamples = [
  { label: '排除日志表', val: 'TABLE:"=LOG"' },
  { label: '排除索引', val: 'INDEX' },
  { label: '排除权限', val: 'GRANT' },
]

const includeExamples = [
  { label: '仅表', val: 'TABLE' },
  { label: '指定表', val: 'TABLE:"IN (EMP,DEPT)"' },
]

const flashbackTimeExamples = [
  { label: '指定时间', val: "TO_TIMESTAMP('2026-01-01 00:00:00','YYYY-MM-DD HH24:MI:SS')" },
  { label: '1天前', val: 'SYSDATE-1' },
]
</script>

<style scoped>
.param-hint { font-size: 11px; color: var(--text-tertiary); margin-top: 4px; line-height: 1.4; }
.param-examples {
  display: flex; flex-wrap: wrap; align-items: center; gap: 6px;
  margin-top: 6px;
}
.example-title { font-size: 11px; color: var(--text-tertiary); }
.example-tag {
  cursor: pointer; font-size: 11px;
  background: var(--bg-tertiary); border-color: var(--border-color); color: var(--text-secondary);
  transition: all var(--transition);
}
.example-tag:hover { background: var(--accent-light); border-color: var(--accent); color: var(--accent); }
.exclude-row { display: flex; gap: 8px; align-items: center; }
.params-form :deep(.el-form-item) { margin-bottom: 16px; }
</style>
