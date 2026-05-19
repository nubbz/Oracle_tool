<template>
  <div class="history-page">
    <div class="page-header">
      <h2>历史记录</h2>
      <div class="header-actions">
        <el-select v-model="filterTool" placeholder="筛选工具" clearable style="width: 140px" @change="loadHistory">
          <el-option v-for="t in TOOL_OPTIONS" :key="t.value" :label="t.label" :value="t.value" />
        </el-select>
        <el-popconfirm title="确定清空所有历史记录？" @confirm="handleClear">
          <template #reference>
            <el-button type="danger" size="small" plain>清空</el-button>
          </template>
        </el-popconfirm>
      </div>
    </div>

    <el-table :data="items" stripe style="width: 100%" v-loading="loading" empty-text="暂无记录">
      <el-table-column prop="tool" label="工具" width="100">
        <template #default="{ row }">
          <el-tag size="small">{{ row.tool }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="oracle_version" label="版本" width="100" />
      <el-table-column prop="connection.username" label="用户" width="120" />
      <el-table-column prop="connection.host" label="主机" width="140" />
      <el-table-column prop="command" label="命令" min-width="300" show-overflow-tooltip />
      <el-table-column prop="created_at" label="时间" width="170">
        <template #default="{ row }">{{ row.created_at?.slice(0, 19).replace('T', ' ') }}</template>
      </el-table-column>
      <el-table-column label="操作" width="200" fixed="right">
        <template #default="{ row }">
          <el-button size="small" text type="primary" @click="showDetail(row)">详情</el-button>
          <el-button size="small" text type="primary" @click="handleReload(row)">加载</el-button>
          <el-button size="small" text type="danger" @click="handleDelete(row.id)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>

    <div class="pagination" v-if="total > pageSize">
      <el-pagination
        background
        layout="total, prev, pager, next"
        :total="total"
        :page-size="pageSize"
        v-model:current-page="page"
        @current-change="loadHistory"
      />
    </div>

    <!-- 历史详情抽屉 -->
    <el-drawer v-model="detailVisible" title="命令详情" direction="rtl" size="50%">
      <template v-if="detailRow">
        <el-descriptions :column="2" border size="small" style="margin-bottom: 16px">
          <el-descriptions-item label="工具"><el-tag size="small">{{ detailRow.tool }}</el-tag></el-descriptions-item>
          <el-descriptions-item label="版本">{{ detailRow.oracle_version }}</el-descriptions-item>
          <el-descriptions-item label="用户">{{ detailRow.connection?.username }}</el-descriptions-item>
          <el-descriptions-item label="主机">{{ detailRow.connection?.host }}:{{ detailRow.connection?.port }}</el-descriptions-item>
          <el-descriptions-item label="时间" :span="2">{{ detailRow.created_at?.slice(0, 19).replace('T', ' ') }}</el-descriptions-item>
        </el-descriptions>
        <CodeBlock :code="detailRow.command" label="Command" />
      </template>
    </el-drawer>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { getHistory, deleteHistoryItem, clearHistory } from '@/api/history'
import { useGeneratorStore } from '@/stores/generatorStore'
import CodeBlock from '@/components/common/CodeBlock.vue'
import { TOOL_OPTIONS } from '@/utils/constants'
import { snakeToCamel } from '@/utils/helpers'

const router = useRouter()
const store = useGeneratorStore()
const items = ref<any[]>([])
const loading = ref(false)
const filterTool = ref('')
const page = ref(1)
const pageSize = 20
const total = ref(0)
const detailVisible = ref(false)
const detailRow = ref<any>(null)

function showDetail(row: any) {
  detailRow.value = row
  detailVisible.value = true
}

async function loadHistory() {
  loading.value = true
  try {
    const { data } = await getHistory({ tool: filterTool.value || undefined, page: page.value, page_size: pageSize })
    items.value = data.items
    total.value = data.total
  } catch { /* handled */ }
  finally { loading.value = false }
}

function handleCopy(cmd: string) { copy(cmd, '命令') }

function handleReload(row: any) {
  store.loadTemplate({
    tool: row.tool,
    connection: convertKeysCamel(row.connection),
    params: convertKeysCamel(row.params),
  })
  router.push('/')
}

async function handleDelete(id: number) {
  try {
    await ElMessageBox.confirm('确定删除此记录？', '提示', { type: 'warning' })
    await deleteHistoryItem(id)
    loadHistory()
  } catch { /* cancelled */ }
}

async function handleClear() {
  try {
    await clearHistory()
    ElMessage.success('历史记录已清空')
    items.value = []
    total.value = 0
  } catch { /* handled */ }
}

function convertKeysCamel(obj: any): any {
  const result: any = {}
  for (const [k, v] of Object.entries(obj)) {
    result[snakeToCamel(k)] = v
  }
  return result
}

onMounted(loadHistory)
</script>

<style scoped>
.history-page { max-width: 1200px; margin: 0 auto; }
.page-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; }
.page-header h2 { font-size: 18px; font-weight: 600; }
.header-actions { display: flex; gap: 10px; align-items: center; }
.pagination { margin-top: 16px; display: flex; justify-content: flex-end; }
</style>
