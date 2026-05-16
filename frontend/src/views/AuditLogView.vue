<template>
  <div class="audit-view">
    <div class="page-header">
      <h2>审计日志</h2>
      <el-select v-model="actionFilter" placeholder="操作类型" clearable style="width: 160px" @change="loadLogs">
        <el-option label="登录" value="login" />
        <el-option label="注册" value="register" />
        <el-option label="命令生成" value="generate" />
        <el-option label="删除" value="delete" />
      </el-select>
    </div>

    <el-table :data="logs" v-loading="loading" stripe>
      <el-table-column prop="created_at" label="时间" width="180" />
      <el-table-column prop="user_id" label="用户ID" width="80" />
      <el-table-column prop="action" label="操作" width="120">
        <template #default="{ row }">
          <el-tag size="small" :type="actionTagType(row.action)">{{ row.action }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="target" label="目标" min-width="150" />
      <el-table-column prop="detail" label="详情" min-width="260" />
      <el-table-column prop="ip_address" label="IP" width="140" />
    </el-table>

    <el-pagination v-if="total > pageSize" :total="total" :page-size="pageSize"
      v-model:current-page="page" layout="prev, pager, next" @current-change="loadLogs"
      style="margin-top: 16px; justify-content: center" />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { getAuditLogs } from '@/api/audit'

const loading = ref(false)
const logs = ref<any[]>([])
const total = ref(0)
const page = ref(1)
const pageSize = 50
const actionFilter = ref('')

onMounted(loadLogs)

async function loadLogs() {
  loading.value = true
  try {
    const { data } = await getAuditLogs(actionFilter.value || undefined, page.value, pageSize)
    logs.value = data.items
    total.value = data.total
  } catch { /* handled */ }
  finally { loading.value = false }
}

function actionTagType(action: string) {
  const map: Record<string, string> = { login: 'success', register: 'info', generate: '', delete: 'danger' }
  return map[action] || ''
}
</script>

<style scoped>
.page-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px; }
.page-header h2 { margin: 0; }
</style>
