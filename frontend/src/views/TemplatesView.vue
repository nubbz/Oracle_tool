<template>
  <div class="templates-view">
    <div class="page-header">
      <h2>命令模板</h2>
      <div>
        <el-button @click="handleSeed" :disabled="seeding">加载内置模板</el-button>
        <el-button type="primary" @click="showCreate = true">新建模板</el-button>
      </div>
    </div>

    <el-tabs v-model="activeTool" @tab-change="loadTemplates">
      <el-tab-pane v-for="t in toolTabs" :key="t.value" :label="t.label" :name="t.value" />
    </el-tabs>

    <el-table :data="templates" v-loading="loading" stripe>
      <el-table-column prop="name" label="名称" min-width="180" />
      <el-table-column prop="description" label="描述" min-width="260" />
      <el-table-column prop="tool" label="工具" width="100">
        <template #default="{ row }">
          <el-tag size="small">{{ row.tool.toUpperCase() }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="oracle_version" label="版本" width="80" />
      <el-table-column label="内置" width="70" align="center">
        <template #default="{ row }">
          <el-tag v-if="row.is_builtin" type="info" size="small">是</el-tag>
        </template>
      </el-table-column>
      <el-table-column label="操作" width="200" fixed="right">
        <template #default="{ row }">
          <el-button size="small" @click="handleUse(row)">使用</el-button>
          <el-button size="small" type="primary" @click="handleEdit(row)" :disabled="row.is_builtin">编辑</el-button>
          <el-button size="small" type="danger" @click="handleDelete(row)" :disabled="row.is_builtin">删除</el-button>
        </template>
      </el-table-column>
    </el-table>

    <!-- Create/Edit Dialog -->
    <el-dialog v-model="showCreate" :title="editingTemplate ? '编辑模板' : '新建模板'" width="500px">
      <el-form :model="form" label-width="80px">
        <el-form-item label="名称" required>
          <el-input v-model="form.name" placeholder="模板名称" />
        </el-form-item>
        <el-form-item label="工具" required>
          <el-select v-model="form.tool" style="width: 100%" :disabled="!!editingTemplate">
            <el-option v-for="t in toolTabs" :key="t.value" :label="t.label" :value="t.value" />
          </el-select>
        </el-form-item>
        <el-form-item label="Oracle 版本">
          <el-select v-model="form.oracle_version" style="width: 100%">
            <el-option v-for="v in ['10g','11g','12c','19c','21c','23c']" :key="v" :label="v" :value="v" />
          </el-select>
        </el-form-item>
        <el-form-item label="描述">
          <el-input v-model="form.description" type="textarea" :rows="2" />
        </el-form-item>
        <el-form-item label="参数 JSON">
          <el-input v-model="form.paramsJson" type="textarea" :rows="8" placeholder="{}" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showCreate = false">取消</el-button>
        <el-button type="primary" @click="handleSave" :loading="saving">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { getTemplates, createTemplate, updateTemplate, deleteTemplate, seedBuiltinTemplates } from '@/api/template'
import type { TemplateItem } from '@/api/template'

const router = useRouter()
const loading = ref(false)
const saving = ref(false)
const seeding = ref(false)
const templates = ref<TemplateItem[]>([])
const activeTool = ref('')
const showCreate = ref(false)
const editingTemplate = ref<TemplateItem | null>(null)

const toolTabs = [
  { value: '', label: '全部' },
  { value: 'expdp', label: 'EXPDP' },
  { value: 'exp', label: 'EXP' },
  { value: 'impdp', label: 'IMPDP' },
  { value: 'imp', label: 'IMP' },
  { value: 'rman', label: 'RMAN' },
  { value: 'optimizer', label: '优化' },
  { value: 'installer', label: '安装' },
]

const form = reactive({
  name: '',
  tool: 'expdp',
  oracle_version: '19c',
  description: '',
  paramsJson: '{}',
})

onMounted(loadTemplates)

async function loadTemplates() {
  loading.value = true
  try {
    const { data } = await getTemplates(activeTool.value || undefined)
    templates.value = data
  } catch { /* handled */ }
  finally { loading.value = false }
}

function handleEdit(row: TemplateItem) {
  editingTemplate.value = row
  form.name = row.name
  form.tool = row.tool
  form.oracle_version = row.oracle_version
  form.description = row.description
  form.paramsJson = JSON.stringify(row.params, null, 2)
  showCreate.value = true
}

function handleUse(row: TemplateItem) {
  const routeMap: Record<string, string> = {
    expdp: '/', exp: '/', impdp: '/', imp: '/',
    rman: '/rman', optimizer: '/optimizer', installer: '/installer',
  }
  const path = routeMap[row.tool] || '/'
  router.push({ path, query: { template: row.id.toString() } })
}

async function handleSave() {
  saving.value = true
  try {
    const params = JSON.parse(form.paramsJson || '{}')
    if (editingTemplate.value) {
      await updateTemplate(editingTemplate.value.id, {
        name: form.name, description: form.description, params,
      })
      ElMessage.success('模板已更新')
    } else {
      await createTemplate({
        name: form.name, tool: form.tool,
        oracle_version: form.oracle_version,
        description: form.description, params,
      })
      ElMessage.success('模板已创建')
    }
    showCreate.value = false
    editingTemplate.value = null
    loadTemplates()
  } catch (e: any) {
    if (e instanceof SyntaxError) {
      ElMessage.error('参数 JSON 格式错误')
    }
  } finally { saving.value = false }
}

async function handleDelete(row: TemplateItem) {
  await ElMessageBox.confirm(`确定删除模板 "${row.name}"？`, '确认删除', { type: 'warning' })
  try {
    await deleteTemplate(row.id)
    ElMessage.success('已删除')
    loadTemplates()
  } catch { /* handled */ }
}

async function handleSeed() {
  seeding.value = true
  try {
    const { data } = await seedBuiltinTemplates()
    ElMessage.success(data.message || '内置模板已加载')
    loadTemplates()
  } catch { /* handled */ }
  finally { seeding.value = false }
}
</script>

<style scoped>
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}
.page-header h2 { margin: 0; }
</style>
