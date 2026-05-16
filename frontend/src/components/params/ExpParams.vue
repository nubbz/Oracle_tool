<template>
  <div class="params-form">
    <CollapsibleSection title="基础参数" :optional="false">
      <el-row :gutter="16">
        <el-col :span="12">
          <el-form-item label="File" required>
            <el-input v-model="form.file" placeholder="/backup/expdat.dmp" />
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item label="Log">
            <el-input v-model="form.logfile" placeholder="export.log" />
          </el-form-item>
        </el-col>
      </el-row>
    </CollapsibleSection>

    <CollapsibleSection title="导出范围">
      <el-form-item label="Owner">
        <TagInput v-model="form.owner" placeholder="输入用户名" />
      </el-form-item>
      <el-form-item label="Tables">
        <TagInput v-model="form.tables" placeholder="输入 表名 或 Schema.表名" />
      </el-form-item>
      <el-form-item label="Query">
        <el-input v-model="form.query" type="textarea" :rows="2" placeholder="WHERE 条件" />
      </el-form-item>
    </CollapsibleSection>

    <CollapsibleSection title="性能选项" :optional="true">
      <el-row :gutter="16">
        <el-col :span="8">
          <el-form-item label="Buffer">
            <el-input v-model="form.buffer" placeholder="10485760" />
            <div class="param-hint">缓冲区大小（字节）</div>
          </el-form-item>
        </el-col>
        <el-col :span="8">
          <el-form-item label="Record Length">
            <el-input-number v-model="form.recordlength" :min="0" :max="65535" style="width: 100%" controls-position="right" />
          </el-form-item>
        </el-col>
        <el-col :span="8">
          <el-form-item label="File Size">
            <el-input v-model="form.fileSize" placeholder="2G" />
          </el-form-item>
        </el-col>
      </el-row>
      <el-form-item label="Statistics">
        <el-select v-model="form.statistics" style="width: 200px">
          <el-option label="ESTIMATE" value="ESTIMATE" />
          <el-option label="COMPUTE" value="COMPUTE" />
          <el-option label="NONE" value="NONE" />
        </el-select>
      </el-form-item>
    </CollapsibleSection>

    <CollapsibleSection title="开关选项" :optional="true">
      <el-row :gutter="16">
        <el-col :span="6">
          <el-form-item><el-checkbox v-model="form.direct">DIRECT</el-checkbox></el-form-item>
        </el-col>
        <el-col :span="6">
          <el-form-item><el-checkbox v-model="form.compress">COMPRESS</el-checkbox></el-form-item>
        </el-col>
        <el-col :span="6">
          <el-form-item><el-checkbox v-model="form.consistent">CONSISTENT</el-checkbox></el-form-item>
        </el-col>
        <el-col :span="6">
          <el-form-item><el-checkbox v-model="form.compression">COMPRESSION</el-checkbox></el-form-item>
        </el-col>
      </el-row>
      <el-row :gutter="16">
        <el-col :span="6">
          <el-form-item><el-checkbox v-model="form.rows">ROWS</el-checkbox></el-form-item>
        </el-col>
        <el-col :span="6">
          <el-form-item><el-checkbox v-model="form.indexes">INDEXES</el-checkbox></el-form-item>
        </el-col>
        <el-col :span="6">
          <el-form-item><el-checkbox v-model="form.constraints">CONSTRAINTS</el-checkbox></el-form-item>
        </el-col>
        <el-col :span="6">
          <el-form-item><el-checkbox v-model="form.grants">GRANTS</el-checkbox></el-form-item>
        </el-col>
      </el-row>
      <el-row :gutter="16">
        <el-col :span="6">
          <el-form-item><el-checkbox v-model="form.triggers">TRIGGERS</el-checkbox></el-form-item>
        </el-col>
        <el-col :span="6">
          <el-form-item><el-checkbox v-model="form.objectConsistent">OBJECT_CONSISTENT</el-checkbox></el-form-item>
        </el-col>
      </el-row>
      <el-row :gutter="16">
        <el-col :span="8">
          <el-form-item label="Feedback">
            <el-input-number v-model="form.feedback" :min="0" style="width: 100%" controls-position="right" />
          </el-form-item>
        </el-col>
      </el-row>
    </CollapsibleSection>

    <CollapsibleSection title="可恢复" :optional="true">
      <el-form-item>
        <el-checkbox v-model="form.resumable">RESUMABLE</el-checkbox>
      </el-form-item>
      <el-row :gutter="16">
        <el-col :span="12">
          <el-form-item label="Resumable Name">
            <el-input v-model="form.resumableName" />
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item label="Resumable Timeout (秒)">
            <el-input-number v-model="form.resumableTimeout" :min="0" style="width: 100%" controls-position="right" />
          </el-form-item>
        </el-col>
      </el-row>
    </CollapsibleSection>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import CollapsibleSection from '@/components/common/CollapsibleSection.vue'
import TagInput from '@/components/common/TagInput.vue'
import { useGeneratorStore } from '@/stores/generatorStore'

const store = useGeneratorStore()
const form = computed(() => store.expParams)
</script>

<style scoped>
.param-hint { font-size: 11px; color: var(--text-tertiary); margin-top: 4px; line-height: 1.4; }
.params-form :deep(.el-form-item) { margin-bottom: 16px; }
</style>
