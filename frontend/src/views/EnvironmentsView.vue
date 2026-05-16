<template>
  <div class="env-page">
    <div class="page-header">
      <h2>环境管理</h2>
      <el-button type="primary" @click="openDialog()">
        <el-icon><Plus /></el-icon> 新增环境
      </el-button>
    </div>

    <el-table :data="environments" stripe style="width: 100%" v-loading="loading" empty-text="暂无环境">
      <el-table-column prop="name" label="名称" width="140" />
      <el-table-column prop="env_type" label="类型" width="90">
        <template #default="{ row }">
          <el-tag :type="envTypeTag(row.env_type)" size="small">{{ row.env_type }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="host" label="主机" width="150" />
      <el-table-column prop="port" label="端口" width="70" />
      <el-table-column prop="service_name" label="Service Name" width="140" show-overflow-tooltip />
      <el-table-column label="容器" width="70" align="center">
        <template #default="{ row }">
          <el-tag v-if="row.container_mode" :type="row.container_mode === 'CDB' ? 'warning' : 'info'" size="small">{{ row.container_mode }}</el-tag>
          <span v-else class="text-muted">-</span>
        </template>
      </el-table-column>
      <el-table-column label="SSH" width="65" align="center">
        <template #default="{ row }">
          <el-tag v-if="row.ssh_enabled" type="success" size="small">ON</el-tag>
          <span v-else class="text-muted">-</span>
        </template>
      </el-table-column>
      <el-table-column prop="description" label="描述" min-width="140" show-overflow-tooltip />
      <el-table-column label="操作" width="300" fixed="right">
        <template #default="{ row }">
          <el-button size="small" text type="warning" @click="openOracleTest(row)">测试连接</el-button>
          <el-button v-if="row.ssh_enabled" size="small" text type="success" @click="testSsh(row)">测试SSH</el-button>
          <el-button size="small" text type="primary" @click="applyEnv(row)">应用</el-button>
          <el-button size="small" text type="primary" @click="openDialog(row)">编辑</el-button>
          <el-button size="small" text type="danger" @click="handleDelete(row.id)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>

    <!-- 编辑/新增对话框 -->
    <el-dialog v-model="dialogVisible" :title="editId ? '编辑环境' : '新增环境'" width="560px" :close-on-click-modal="false">
      <el-form :model="form" label-position="top">
        <el-form-item label="名称" required>
          <el-input v-model="form.name" placeholder="如 生产库-上海" />
        </el-form-item>
        <el-form-item label="类型">
          <el-select v-model="form.env_type" style="width: 100%" @change="onEnvTypeChange">
            <el-option label="开发" value="dev" />
            <el-option label="测试" value="test" />
            <el-option label="UAT" value="uat" />
            <el-option label="生产" value="production" />
          </el-select>
        </el-form-item>
        <el-row :gutter="16">
          <el-col :span="16">
            <el-form-item label="主机">
              <el-input v-model="form.host" />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="端口">
              <el-input-number v-model="form.port" :min="1" :max="65535" style="width: 100%" controls-position="right" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="连接类型">
          <el-radio-group v-model="form.connect_type">
            <el-radio-button value="service">Service Name</el-radio-button>
            <el-radio-button value="sid">SID</el-radio-button>
          </el-radio-group>
        </el-form-item>
        <el-form-item :label="form.connect_type === 'service' ? 'Service Name' : 'SID'">
          <el-input :model-value="form.connect_type === 'service' ? form.service_name : form.sid" @update:model-value="updateIdent($event)" />
        </el-form-item>
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="容器模式">
              <el-radio-group v-model="form.container_mode">
                <el-radio-button value="">无</el-radio-button>
                <el-radio-button value="CDB">CDB</el-radio-button>
                <el-radio-button value="PDB">PDB</el-radio-button>
              </el-radio-group>
            </el-form-item>
          </el-col>
          <el-col v-if="form.container_mode === 'PDB'" :span="12">
            <el-form-item label="PDB 名称">
              <el-input v-model="form.pdb_name" placeholder="如 pdb1" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="描述">
          <el-input v-model="form.description" type="textarea" :rows="2" />
        </el-form-item>

        <el-divider content-position="left">
          <el-switch v-model="form.ssh_enabled" active-text="SSH 隧道" inactive-text="" />
        </el-divider>

        <template v-if="form.ssh_enabled">
          <el-row :gutter="16">
            <el-col :span="12">
              <el-form-item label="SSH 主机">
                <el-input v-model="form.ssh_host" placeholder="跳板机地址" />
              </el-form-item>
            </el-col>
            <el-col :span="6">
              <el-form-item label="SSH 端口">
                <el-input-number v-model="form.ssh_port" :min="1" :max="65535" style="width: 100%" controls-position="right" />
              </el-form-item>
            </el-col>
            <el-col :span="6">
              <el-form-item label="SSH 用户名">
                <el-input v-model="form.ssh_username" />
              </el-form-item>
            </el-col>
          </el-row>
          <el-form-item label="认证方式">
            <el-radio-group v-model="form.ssh_auth_method">
              <el-radio-button value="password">密码</el-radio-button>
              <el-radio-button value="key">密钥</el-radio-button>
            </el-radio-group>
          </el-form-item>
          <el-form-item v-if="form.ssh_auth_method === 'password'" label="SSH 密码">
            <el-input v-model="form.ssh_password" type="password" show-password placeholder="SSH 密码" />
          </el-form-item>
          <template v-else>
            <el-form-item label="密钥路径">
              <el-input v-model="form.ssh_key_path" placeholder="~/.ssh/id_rsa" />
            </el-form-item>
            <el-form-item label="密钥密码">
              <el-input v-model="form.ssh_key_passphrase" type="password" show-password placeholder="可选" />
            </el-form-item>
          </template>
        </template>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="saving" @click="handleSave">保存</el-button>
      </template>
    </el-dialog>

    <!-- Oracle 连接测试对话框 -->
    <el-dialog v-model="oracleTestVisible" title="测试 Oracle 连接" width="460px" :close-on-click-modal="false">
      <el-alert :title="'环境: ' + oracleTestForm.envName" type="info" :closable="false" style="margin-bottom: 16px" />
      <el-form label-position="top">
        <el-form-item label="数据库用户名" required>
          <el-input v-model="oracleTestForm.username" placeholder="system" />
        </el-form-item>
        <el-form-item label="数据库密码" required>
          <el-input v-model="oracleTestForm.password" type="password" show-password placeholder="请输入密码" />
        </el-form-item>
      </el-form>
      <div v-if="oracleTestResult" style="margin-top: 16px">
        <el-result v-if="oracleTestResult.success" icon="success" title="连接成功">
          <template #extra>
            <el-descriptions :column="1" border size="small">
              <el-descriptions-item label="实例名">{{ oracleTestResult.instance_name }}</el-descriptions-item>
              <el-descriptions-item label="状态">{{ oracleTestResult.status }}</el-descriptions-item>
              <el-descriptions-item label="版本">{{ oracleTestResult.version }}</el-descriptions-item>
              <el-descriptions-item label="响应时间">{{ oracleTestResult.response_time }}s</el-descriptions-item>
            </el-descriptions>
          </template>
        </el-result>
        <el-result v-else icon="error" title="连接失败" :sub-title="oracleTestResult.error" />
      </div>
      <template #footer>
        <el-button @click="oracleTestVisible = false">关闭</el-button>
        <el-button type="primary" :loading="oracleTestLoading" @click="handleOracleTest">测试</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { getEnvironments, createEnvironment, updateEnvironment, deleteEnvironment, testSshConnection, testOracleConnection } from '@/api/environment'
import { useGeneratorStore } from '@/stores/generatorStore'
import { ORACLE_ENV_DEFAULTS } from '@/utils/constants'

const router = useRouter()
const store = useGeneratorStore()
const environments = ref<any[]>([])
const loading = ref(false)
const saving = ref(false)
const dialogVisible = ref(false)
const editId = ref<number | null>(null)

const form = reactive({
  name: '', env_type: 'production', host: 'localhost', port: 1521,
  service_name: '', sid: '', connect_type: 'service', description: '',
  container_mode: '', pdb_name: '',
  ssh_enabled: false, ssh_host: '', ssh_port: 22, ssh_username: '',
  ssh_auth_method: 'password' as const, ssh_password: '',
  ssh_key_path: '', ssh_key_passphrase: '',
})

// Oracle test state
const oracleTestVisible = ref(false)
const oracleTestLoading = ref(false)
const oracleTestResult = ref<any>(null)
const oracleTestForm = reactive({ envId: 0, envName: '', username: '', password: '' })

function updateIdent(val: string) {
  if (form.connect_type === 'service') form.service_name = val
  else form.sid = val
}

function onEnvTypeChange(type: string) {
  const defaults = ORACLE_ENV_DEFAULTS[type]
  if (defaults && !editId.value) {
    form.port = defaults.port
    if (form.connect_type === 'service') form.service_name = defaults.serviceName
  }
}

function envTypeTag(type: string) {
  return { dev: 'info', test: '', uat: 'warning', production: 'danger' }[type] || ''
}

async function load() {
  loading.value = true
  try {
    const { data } = await getEnvironments()
    environments.value = data
  } catch { /* handled */ }
  finally { loading.value = false }
}

function openDialog(row?: any) {
  if (row) {
    editId.value = row.id
    Object.assign(form, {
      name: row.name, env_type: row.env_type, host: row.host, port: row.port,
      service_name: row.service_name, sid: row.sid, connect_type: row.connect_type,
      description: row.description,
      container_mode: row.container_mode || '', pdb_name: row.pdb_name || '',
      ssh_enabled: row.ssh_enabled || false,
      ssh_host: row.ssh_host || '', ssh_port: row.ssh_port || 22,
      ssh_username: row.ssh_username || '',
      ssh_auth_method: row.ssh_auth_method || 'password',
      ssh_password: '', ssh_key_path: row.ssh_key_path || '',
      ssh_key_passphrase: '',
    })
  } else {
    editId.value = null
    Object.assign(form, {
      name: '', env_type: 'production', host: 'localhost', port: 1521,
      service_name: '', sid: '', connect_type: 'service', description: '',
      container_mode: '', pdb_name: '',
      ssh_enabled: false, ssh_host: '', ssh_port: 22, ssh_username: '',
      ssh_auth_method: 'password', ssh_password: '',
      ssh_key_path: '', ssh_key_passphrase: '',
    })
  }
  dialogVisible.value = true
}

async function handleSave() {
  if (!form.name.trim()) { ElMessage.warning('请输入名称'); return }
  saving.value = true
  try {
    if (editId.value) {
      await updateEnvironment(editId.value, { ...form })
      ElMessage.success('已更新')
    } else {
      await createEnvironment({ ...form })
      ElMessage.success('已创建')
    }
    dialogVisible.value = false
    load()
  } catch { /* handled */ }
  finally { saving.value = false }
}

function applyEnv(row: any) {
  store.connection.host = row.host
  store.connection.port = row.port
  store.connection.connectType = row.connect_type
  store.connection.serviceName = row.service_name
  store.connection.sid = row.sid
  store.connection.containerMode = row.container_mode || ''
  store.connection.pdbName = row.pdb_name || ''
  store.connection.sshEnabled = row.ssh_enabled || false
  store.connection.sshHost = row.ssh_host || ''
  store.connection.sshPort = row.ssh_port || 22
  store.connection.sshUsername = row.ssh_username || ''
  store.connection.sshAuthMethod = row.ssh_auth_method || 'password'
  store.connection.sshKeyPath = row.ssh_key_path || ''
  ElMessage.success(`已应用环境「${row.name}」`)
  router.push('/')
}

async function testSsh(row: any) {
  try {
    ElMessage.info('正在测试 SSH 连接...')
    const { data } = await testSshConnection(row.id)
    if (data.success) {
      ElMessage.success(`SSH 连接成功 (${data.connection_time}s)`)
    } else {
      ElMessage.error(`SSH 连接失败: ${data.error}`)
    }
  } catch (e: any) {
    ElMessage.error(e.response?.data?.detail || 'SSH 测试请求失败')
  }
}

function openOracleTest(row: any) {
  oracleTestForm.envId = row.id
  oracleTestForm.envName = row.name
  oracleTestForm.username = ''
  oracleTestForm.password = ''
  oracleTestResult.value = null
  oracleTestVisible.value = true
}

async function handleOracleTest() {
  if (!oracleTestForm.username || !oracleTestForm.password) {
    ElMessage.warning('请输入用户名和密码')
    return
  }
  oracleTestLoading.value = true
  oracleTestResult.value = null
  try {
    const { data } = await testOracleConnection(
      oracleTestForm.envId,
      oracleTestForm.username,
      oracleTestForm.password,
    )
    oracleTestResult.value = data
  } catch (e: any) {
    ElMessage.error(e.response?.data?.detail || '连接测试请求失败')
  } finally {
    oracleTestLoading.value = false
  }
}

async function handleDelete(id: number) {
  try {
    await ElMessageBox.confirm('确定删除此环境？', '提示', { type: 'warning' })
    await deleteEnvironment(id)
    ElMessage.success('已删除')
    load()
  } catch { /* cancelled */ }
}

onMounted(load)
</script>

<style scoped>
.env-page { max-width: 1200px; margin: 0 auto; }
.page-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; }
.page-header h2 { font-size: 18px; font-weight: 600; }
.text-muted { color: #c0c4cc; }
</style>
