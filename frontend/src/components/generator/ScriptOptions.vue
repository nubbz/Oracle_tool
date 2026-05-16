<template>
  <div class="script-options">
    <el-button-group>
      <el-button :type="activeTab === 'command' ? 'primary' : ''" @click="activeTab = 'command'">命令</el-button>
      <el-button :type="activeTab === 'parfile' ? 'primary' : ''" @click="activeTab = 'parfile'">参数文件</el-button>
      <el-button :type="activeTab === 'sh' ? 'primary' : ''" @click="activeTab = 'sh'">Shell脚本</el-button>
      <el-button :type="activeTab === 'bat' ? 'primary' : ''" @click="activeTab = 'bat'">Bat脚本</el-button>
      <el-button v-if="props.result?.directory_ddl" :type="activeTab === 'ddl' ? 'primary' : ''" @click="activeTab = 'ddl'">Directory DDL</el-button>
    </el-button-group>
    <div class="download-btns">
      <el-button size="small" @click="handleDownload('sh')">
        <el-icon><Download /></el-icon> .sh
      </el-button>
      <el-button size="small" @click="handleDownload('bat')">
        <el-icon><Download /></el-icon> .bat
      </el-button>
      <el-button size="small" @click="handleDownload('par')">
        <el-icon><Download /></el-icon> .par
      </el-button>
    </div>
  </div>
  <CodeBlock :code="currentCode" :label="tabLabels[activeTab]" />
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import CodeBlock from '@/components/common/CodeBlock.vue'
import { useClipboard } from '@/composables/useClipboard'
import { downloadFile, timestamp } from '@/utils/helpers'

const props = defineProps<{ result: any }>()
const activeTab = ref<'command' | 'parfile' | 'sh' | 'bat' | 'ddl'>('command')
const { copy } = useClipboard()

const tabLabels: Record<string, string> = {
  command: '命令',
  parfile: '参数文件',
  sh: 'Shell脚本',
  bat: 'Bat脚本',
  ddl: 'Directory DDL',
}

const currentCode = computed(() => {
  if (!props.result) return ''
  switch (activeTab.value) {
    case 'command': return props.result.command || ''
    case 'parfile': return props.result.parfile || ''
    case 'sh': return props.result.script || ''
    case 'bat': return props.result.script_bat || ''
    case 'ddl': return props.result.directory_ddl || ''
    default: return ''
  }
})

function handleDownload(type: string) {
  const ts = timestamp()
  let content = '', filename = ''
  if (type === 'sh') {
    content = props.result.script || ''
    filename = `oracle_backup_${ts}.sh`
  } else if (type === 'bat') {
    content = props.result.script_bat || props.result.script || ''
    filename = `oracle_backup_${ts}.bat`
  } else if (type === 'par') {
    content = props.result.parfile || ''
    filename = `oracle_backup_${ts}.par`
  }
  downloadFile(content, filename)
}
</script>

<style scoped>
.script-options {
  display: flex; justify-content: space-between; align-items: center;
  margin-bottom: 12px;
}
.download-btns { display: flex; gap: 6px; }
</style>
