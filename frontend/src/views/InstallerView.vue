<template>
  <div class="installer-page">
    <div class="page-header">
      <h2>DB 安装工具</h2>
      <span class="page-desc">Oracle 数据库静默安装脚本命令生成器（支持 11g / 12c / 19c / 21c / 23c）</span>
    </div>

    <el-alert type="warning" :closable="false" show-icon style="margin-bottom: 20px">
      本脚本仅用于新服务器部署，<b>严禁</b>在已运行数据库的主机上执行。
    </el-alert>

    <el-form :model="form" label-width="auto">
    <!-- 基础配置 -->
    <el-card shadow="never" class="section-card">
      <template #header><span class="section-title">基础配置</span></template>
      <el-row :gutter="24">
        <el-col :span="8">
          <el-form-item label="安装模式">
            <el-select v-model="form.mode" style="width: 100%" @change="onModeChange">
              <el-option label="单机 (Single)" value="single" />
              <el-option label="单机 ASM (Standalone)" value="standalone" />
              <el-option label="RAC 集群" value="rac" />
            </el-select>
          </el-form-item>
        </el-col>
        <el-col :span="8">
          <el-form-item label="DB 版本 (-dbv)">
            <el-select v-model="form.db_version" style="width: 100%">
              <el-option v-for="v in DB_VERSIONS" :key="v" :label="v" :value="v" />
            </el-select>
          </el-form-item>
        </el-col>
        <el-col v-if="isASM" :span="8">
          <el-form-item label="Grid 版本 (-giv)">
            <el-select v-model="form.gi_version" style="width: 100%">
              <el-option v-for="v in DB_VERSIONS" :key="v" :label="v" :value="v" />
            </el-select>
          </el-form-item>
        </el-col>
      </el-row>
      <el-row :gutter="24">
        <el-col :span="8">
          <el-form-item label="主机名 (-n)">
            <el-input v-model="form.hostname" />
          </el-form-item>
        </el-col>
        <el-col :span="8">
          <el-form-item label="安装根目录 (-d)">
            <el-input v-model="form.env_base_dir" />
          </el-form-item>
        </el-col>
        <el-col :span="8">
          <el-form-item label="公网网卡 (-lf)">
            <el-input v-model="form.local_ifname" placeholder="如 eth0、ens192" />
          </el-form-item>
        </el-col>
      </el-row>

      <el-divider content-position="left">安装选项</el-divider>
      <div class="switch-row">
        <div class="switch-item">
          <el-switch v-model="form.local_repo" active-value="Y" inactive-value="N" />
          <span>本地软件源</span>
        </div>
        <div class="switch-item">
          <el-switch v-model="form.net_repo" active-value="Y" inactive-value="N" />
          <span>网络软件源</span>
        </div>
        <div class="switch-item">
          <el-switch v-model="form.isgui" active-value="Y" inactive-value="N" />
          <span>图形界面</span>
        </div>
        <div class="switch-item">
          <el-switch v-model="form.huge_flag" active-value="Y" inactive-value="N" />
          <span>大页内存</span>
        </div>
        <div class="switch-item">
          <el-switch v-model="form.only_conf_os" active-value="Y" inactive-value="N" />
          <span>仅配置 OS</span>
        </div>
        <div class="switch-item">
          <el-switch v-model="form.install_until_db" active-value="Y" inactive-value="N" />
          <span>安装到 DB 软件</span>
        </div>
        <div v-if="isASM" class="switch-item">
          <el-switch v-model="form.install_until_grid" active-value="Y" inactive-value="N" />
          <span>安装到 Grid</span>
        </div>
        <div class="switch-item">
          <el-switch v-model="form.optimize_db" active-value="Y" inactive-value="N" />
          <span>优化数据库</span>
        </div>
      </div>
    </el-card>

    <!-- 用户与密码 -->
    <el-card shadow="never" class="section-card">
      <template #header><span class="section-title">用户与密码</span></template>
      <el-row :gutter="24">
        <el-col :span="8">
          <el-form-item label="oracle 用户 (-ou)">
            <el-input v-model="form.oracle_user" />
          </el-form-item>
        </el-col>
        <el-col :span="8">
          <el-form-item label="oracle 密码 (-op)">
            <el-input v-model="form.oracle_passwd" type="password" show-password />
          </el-form-item>
        </el-col>
        <el-col :span="8">
          <el-form-item label="sys/system 密码 (-dp)">
            <el-input v-model="form.database_passwd" type="password" show-password />
          </el-form-item>
        </el-col>
      </el-row>
      <el-row v-if="isASM" :gutter="24">
        <el-col :span="8">
          <el-form-item label="grid 用户 (-gu)">
            <el-input v-model="form.grid_user" />
          </el-form-item>
        </el-col>
        <el-col :span="8">
          <el-form-item label="grid 密码 (-gp)">
            <el-input v-model="form.grid_passwd" type="password" show-password />
          </el-form-item>
        </el-col>
      </el-row>
      <el-row v-if="isRAC" :gutter="24">
        <el-col :span="8">
          <el-form-item label="root 密码 (-rp)">
            <el-input v-model="form.root_passwd" type="password" show-password />
          </el-form-item>
        </el-col>
      </el-row>
    </el-card>

    <!-- 数据库参数 -->
    <el-card shadow="never" class="section-card">
      <template #header>
        <div style="display: flex; justify-content: space-between; align-items: center; width: 100%">
          <span class="section-title">数据库参数</span>
          <el-tag v-if="versionHint" :type="versionHint.type" size="small">{{ versionHint.text }}</el-tag>
        </div>
      </template>
      <el-row :gutter="24">
        <el-col :span="8">
          <el-form-item label="数据库名称 (-o)">
            <el-input v-model="form.db_name" />
          </el-form-item>
        </el-col>
        <el-col :span="8">
          <el-form-item>
            <template #label>
              {{ isASM ? '数据 ASM 磁盘组 (-dn)' : '数据文件目录 (-ord)' }}
            </template>
            <el-input v-if="isASM" v-model="form.data_asm_group" />
            <el-input v-else v-model="form.oradata_dir" />
          </el-form-item>
        </el-col>
        <el-col :span="8">
          <el-form-item label="字符集 (-ds)">
            <el-select v-model="form.db_characterset" style="width: 100%" filterable>
              <el-option v-for="cs in charsetOptions" :key="cs" :label="cs" :value="cs" />
            </el-select>
          </el-form-item>
        </el-col>
      </el-row>
      <el-row :gutter="24">
        <el-col :span="8">
          <el-form-item label="国家字符集 (-ns)">
            <el-select v-model="form.nation_characterset" style="width: 100%">
              <el-option label="AL16UTF16" value="AL16UTF16" />
              <el-option label="UTF8" value="UTF8" />
            </el-select>
          </el-form-item>
        </el-col>
        <el-col :span="8">
          <el-form-item label="块大小 (-dbs)">
            <el-select v-model="form.db_block_size" style="width: 100%">
              <el-option v-for="bs in blockSizeOptions" :key="bs" :label="String(bs)" :value="bs" />
            </el-select>
          </el-form-item>
        </el-col>
        <el-col v-if="supportsCDB" :span="8">
          <el-form-item>
            <template #label>
              PDB 名称 (-pdb)
              <el-tag v-if="isCDBForced" size="small" type="warning" style="margin-left: 4px">CDB 强制</el-tag>
            </template>
            <el-input v-model="form.pdbname" :placeholder="pdbPlaceholder" />
          </el-form-item>
        </el-col>
      </el-row>
      <el-row :gutter="24">
        <el-col :span="8">
          <el-form-item label="Redo 大小 MB (-redo)">
            <el-input-number v-model="form.redosize" :min="128" :step="128" style="width: 100%" controls-position="right" />
            <div class="preset-tags">
              <el-tag v-for="s in redoPresets" :key="s" size="small" class="preset-tag" @click="form.redosize = s">{{ s }}</el-tag>
            </div>
          </el-form-item>
        </el-col>
        <el-col :span="8">
          <el-form-item label="启用归档 (-er)">
            <el-switch v-model="form.enable_arch" active-value="true" inactive-value="false" active-text="是" inactive-text="否" />
          </el-form-item>
        </el-col>
        <el-col v-if="!isASM" :span="8">
          <el-form-item label="归档目录 (-ard)">
            <el-input v-model="form.archive_dir" />
          </el-form-item>
        </el-col>
        <el-col v-if="isASM" :span="8">
          <el-form-item label="归档 ASM 磁盘组 (-an)">
            <el-input v-model="form.arch_asm_group" />
          </el-form-item>
        </el-col>
      </el-row>
    </el-card>

    <!-- 存储配置 (standalone + rac) -->
    <el-card v-if="isASM" shadow="never" class="section-card">
      <template #header><span class="section-title">存储配置</span></template>
      <div class="switch-row">
        <div class="switch-item">
          <el-switch v-model="form.asm_disk_conf" active-value="Y" inactive-value="N" />
          <span>脚本配置 ASM 磁盘</span>
        </div>
        <div class="switch-item">
          <el-switch v-model="form.multipath" active-value="Y" inactive-value="N" />
          <span>Multipath 多路径</span>
        </div>
        <div class="switch-item">
          <el-switch v-model="form.virtualbox" active-value="Y" inactive-value="N" />
          <span>VBOX 修复</span>
        </div>
      </div>

      <el-divider content-position="left">DATA 磁盘组</el-divider>
      <el-row :gutter="24">
        <el-col :span="8">
          <el-form-item label="磁盘列表 (-dd)">
            <el-input v-model="form.data_base_disk" placeholder="如 /dev/sdb" />
          </el-form-item>
        </el-col>
        <el-col :span="8">
          <el-form-item label="磁盘组名 (-dn)">
            <el-input v-model="form.data_asm_group" />
          </el-form-item>
        </el-col>
        <el-col :span="8">
          <el-form-item label="冗余度 (-dr)">
            <el-select v-model="form.data_redun" style="width: 100%">
              <el-option label="EXTERNAL" value="EXTERNAL" />
              <el-option label="NORMAL" value="NORMAL" />
              <el-option label="HIGH" value="HIGH" />
            </el-select>
          </el-form-item>
        </el-col>
      </el-row>

      <template v-if="isRAC">
        <el-divider content-position="left">OCR 磁盘组</el-divider>
        <el-row :gutter="24">
          <el-col :span="8">
            <el-form-item label="磁盘列表 (-od)">
              <el-input v-model="form.ocr_base_disk" placeholder="如 /dev/sdc" />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="磁盘组名 (-on)">
              <el-input v-model="form.ocr_asm_group" />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="冗余度 (-or)">
              <el-select v-model="form.ocr_redun" style="width: 100%">
                <el-option label="EXTERNAL" value="EXTERNAL" />
                <el-option label="NORMAL" value="NORMAL" />
                <el-option label="HIGH" value="HIGH" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>

        <el-divider content-position="left">ARCH 磁盘组</el-divider>
        <el-row :gutter="24">
          <el-col :span="8">
            <el-form-item label="磁盘列表 (-ad)">
              <el-input v-model="form.arch_base_disk" placeholder="如 /dev/sdd" />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="磁盘组名 (-an)">
              <el-input v-model="form.arch_asm_group" />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="冗余度 (-ar)">
              <el-select v-model="form.arch_redun" style="width: 100%">
                <el-option label="EXTERNAL" value="EXTERNAL" />
                <el-option label="NORMAL" value="NORMAL" />
                <el-option label="HIGH" value="HIGH" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
      </template>
    </el-card>

    <!-- 网络配置 (rac only) -->
    <el-card v-if="isRAC" shadow="never" class="section-card">
      <template #header><span class="section-title">网络配置 (RAC)</span></template>
      <el-row :gutter="24">
        <el-col :span="12">
          <el-form-item label="心跳网卡 (-pf)">
            <el-input v-model="form.rac_priv_ifname" placeholder="如 eth1,eth2" />
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item label="时间服务器 (-tsi)">
            <el-input v-model="form.timeserver_ip" />
          </el-form-item>
        </el-col>
      </el-row>
      <el-row :gutter="24">
        <el-col :span="8">
          <el-form-item label="集群名称 (-cn)">
            <el-input v-model="form.cluster_name" placeholder="默认取主机名前缀-cluster" />
          </el-form-item>
        </el-col>
        <el-col :span="8">
          <el-form-item label="SCAN 名称 (-sn)">
            <el-input v-model="form.scan_name" placeholder="默认取主机名前缀-scan" />
          </el-form-item>
        </el-col>
        <el-col :span="8">
          <el-form-item label="SCAN IP (-si)">
            <el-input v-model="form.rac_scan_ip" placeholder="如 10.0.0.100" />
          </el-form-item>
        </el-col>
      </el-row>

      <el-divider content-position="left">节点 IP</el-divider>
      <el-row :gutter="24">
        <el-col :span="8">
          <el-form-item label="主机名列表 (-hn)">
            <el-input v-model="form.rac_hostname" placeholder="如 orcl01,orcl02" />
          </el-form-item>
        </el-col>
        <el-col :span="8">
          <el-form-item label="公网 IP (-ri)">
            <el-input v-model="form.rac_public_ip" placeholder="如 10.0.0.1,10.0.0.2" />
          </el-form-item>
        </el-col>
        <el-col :span="8">
          <el-form-item label="VIP (-vi)">
            <el-input v-model="form.rac_virtual_ip" placeholder="如 10.0.0.11,10.0.0.12" />
          </el-form-item>
        </el-col>
      </el-row>

      <el-divider content-position="left">DNS</el-divider>
      <el-row :gutter="24">
        <el-col :span="8">
          <el-form-item label="配置 DNS (-dns)">
            <el-switch v-model="form.dns" active-value="Y" inactive-value="N" />
          </el-form-item>
        </el-col>
        <el-col v-if="form.dns === 'Y'" :span="8">
          <el-form-item label="DNS 名称 (-dnsn)">
            <el-input v-model="form.dns_name" />
          </el-form-item>
        </el-col>
        <el-col v-if="form.dns === 'Y'" :span="8">
          <el-form-item label="DNS IP (-dnsi)">
            <el-input v-model="form.dns_ip" />
          </el-form-item>
        </el-col>
      </el-row>
    </el-card>

    <!-- 补丁 -->
    <el-card shadow="never" class="section-card">
      <template #header><span class="section-title">补丁 (可选)</span></template>
      <el-row :gutter="24">
        <el-col v-if="isASM" :span="8">
          <el-form-item label="Grid PSU/RU (-gpa)">
            <el-input v-model="form.grid_patch" placeholder="补丁编号" />
          </el-form-item>
        </el-col>
        <el-col :span="8">
          <el-form-item label="Oracle PSU/RU (-opa)">
            <el-input v-model="form.oracle_patch" placeholder="补丁编号" />
          </el-form-item>
        </el-col>
        <el-col :span="8">
          <el-form-item label="OJVM PSU/RU (-jpa)">
            <el-input v-model="form.ojvm_patch" placeholder="补丁编号" />
          </el-form-item>
        </el-col>
      </el-row>
    </el-card>
    </el-form>

    <!-- 操作按钮 -->
    <div class="action-bar">
      <el-button type="primary" size="large" @click="drawerVisible = true">生成命令</el-button>
      <el-button size="large" @click="resetForm">重置</el-button>
    </div>

    <!-- 底部抽屉 -->
    <el-drawer v-model="drawerVisible" direction="rtl" size="50%" title="生成结果">
      <template v-if="generatedCommand">
        <CommandSteps v-if="generatedSteps.length" :steps="generatedSteps" />
        <el-divider v-if="generatedSteps.length" />
        <div class="script-options">
          <div class="tags-area">
            <el-tag v-for="tag in paramTags" :key="tag" size="small" type="info" style="margin: 2px">{{ tag }}</el-tag>
          </div>
          <div class="download-btns">
            <el-button size="small" @click="copyCommand">
              <el-icon><CopyDocument /></el-icon> 复制
            </el-button>
            <el-button size="small" @click="downloadScript">
              <el-icon><Download /></el-icon> .sh
            </el-button>
          </div>
        </div>
        <CodeBlock :code="generatedCommand" label="安装命令" />
      </template>
      <template #footer>
        <div class="drawer-footer">
          <el-button type="primary" :loading="saving" @click="handleSave">保存到历史</el-button>
        </div>
      </template>
    </el-drawer>
  </div>
</template>

<script setup lang="ts">
import { reactive, computed, ref, watch } from 'vue'
import { ElMessage } from 'element-plus'
import { Download, CopyDocument } from '@element-plus/icons-vue'
import { generateInstallCommand } from '@/api/installer'
import CommandSteps from '@/components/common/CommandSteps.vue'
import CodeBlock from '@/components/common/CodeBlock.vue'

const DB_VERSIONS = ['11', '12', '19', '21', '26']
const CHARSET_COMMON = ['AL32UTF8', 'ZHS16GBK', 'ZHT16MSWIN950', 'UTF8', 'WE8ISO8859P1', 'EE8ISO8859P2']

const DEFAULTS: Record<string, any> = {
  mode: 'single', gi_version: '', db_version: '',
  local_repo: 'Y', net_repo: 'N', local_ifname: '',
  hostname: 'orcl', oracle_user: 'oracle', oracle_passwd: 'oracle',
  database_passwd: 'oracle', env_base_dir: '/u01', oradata_dir: '/oradata',
  db_name: 'orcl', db_characterset: 'AL32UTF8', nation_characterset: 'AL16UTF16',
  db_block_size: 8192, enable_arch: 'true', pdbname: '', redosize: 1024,
  isgui: 'N', huge_flag: 'N', only_conf_os: 'N', install_until_db: 'N',
  optimize_db: 'N', oracle_patch: '', ojvm_patch: '',
  archive_dir: '/oradata/archivelog', grid_user: 'grid', grid_passwd: 'oracle',
  asm_disk_conf: 'Y', multipath: 'Y', data_base_disk: '',
  data_asm_group: 'DATA', data_redun: 'EXTERNAL', grid_patch: '', virtualbox: 'N',
  rac_priv_ifname: '', rac_hostname: '', rac_public_ip: '',
  rac_virtual_ip: '', rac_scan_ip: '', root_passwd: '',
  cluster_name: '', scan_name: '', ocr_base_disk: '', arch_base_disk: '',
  ocr_asm_group: 'OCR', arch_asm_group: 'ARCH', ocr_redun: 'EXTERNAL',
  arch_redun: 'EXTERNAL', timeserver_ip: '', dns: 'N', dns_name: '',
  dns_ip: '', install_until_grid: 'N',
}

const ASM_FIELDS = new Set([
  'grid_user', 'grid_passwd', 'asm_disk_conf', 'multipath',
  'data_base_disk', 'data_asm_group', 'data_redun', 'grid_patch',
  'virtualbox',
])
const RAC_FIELDS = new Set([
  'rac_priv_ifname', 'rac_hostname', 'rac_public_ip', 'rac_virtual_ip',
  'rac_scan_ip', 'root_passwd', 'cluster_name', 'scan_name',
  'ocr_base_disk', 'arch_base_disk', 'ocr_asm_group', 'arch_asm_group',
  'ocr_redun', 'arch_redun', 'timeserver_ip',
  'dns', 'dns_name', 'dns_ip', 'install_until_grid',
])

const FLAG_MAP: [string, string][] = [
  ['mode', '-install_mode'], ['gi_version', '-giv'], ['db_version', '-dbv'],
  ['local_repo', '-lrp'], ['net_repo', '-nrp'], ['local_ifname', '-lf'],
  ['hostname', '-n'], ['oracle_user', '-ou'], ['oracle_passwd', '-op'],
  ['database_passwd', '-dp'], ['env_base_dir', '-d'], ['oradata_dir', '-ord'],
  ['db_name', '-o'], ['db_characterset', '-ds'], ['nation_characterset', '-ns'],
  ['db_block_size', '-dbs'], ['enable_arch', '-er'], ['pdbname', '-pdb'],
  ['redosize', '-redo'], ['isgui', '-gui'], ['huge_flag', '-hf'],
  ['only_conf_os', '-m'], ['install_until_db', '-ud'], ['optimize_db', '-opd'],
  ['oracle_patch', '-opa'], ['ojvm_patch', '-jpa'],
  ['archive_dir', '-ard'], ['grid_user', '-gu'], ['grid_passwd', '-gp'],
  ['asm_disk_conf', '-adc'], ['multipath', '-mp'], ['data_base_disk', '-dd'],
  ['data_asm_group', '-dn'], ['data_redun', '-dr'], ['grid_patch', '-gpa'],
  ['virtualbox', '-vbox'],
  ['rac_priv_ifname', '-pf'], ['rac_hostname', '-hn'], ['rac_public_ip', '-ri'],
  ['rac_virtual_ip', '-vi'], ['rac_scan_ip', '-si'], ['root_passwd', '-rp'],
  ['cluster_name', '-cn'], ['scan_name', '-sn'], ['ocr_base_disk', '-od'],
  ['arch_base_disk', '-ad'], ['ocr_asm_group', '-on'], ['arch_asm_group', '-an'],
  ['ocr_redun', '-or'], ['arch_redun', '-ar'], ['timeserver_ip', '-tsi'],
  ['dns', '-dns'], ['dns_name', '-dnsn'], ['dns_ip', '-dnsi'],
  ['install_until_grid', '-ug'],
]

const form = reactive({ ...DEFAULTS })

const saving = ref(false)
const drawerVisible = ref(false)

const isASM = computed(() => form.mode === 'standalone' || form.mode === 'rac')
const isRAC = computed(() => form.mode === 'rac')

const supportsCDB = computed(() => form.db_version !== '11')
const isCDBForced = computed(() => form.db_version === '21' || form.db_version === '26')

const versionHint = computed(() => {
  const v = form.db_version
  if (!v) return null
  const labels: Record<string, string> = { '11': '11g R2', '12': '12c R2', '19': '19c', '21': '21c', '26': '23c' }
  const isForced = v === '21' || v === '26'
  return {
    text: isForced ? `${labels[v]} · CDB 强制模式` : `${labels[v]}`,
    type: isForced ? 'warning' : 'info',
  }
})

const charsetOptions = computed(() => CHARSET_COMMON)
const blockSizeOptions = computed(() => [2048, 4096, 8192, 16384, 32768])
const redoPresets = computed(() => [512, 1024, 2048, 4096])

const pdbPlaceholder = computed(() => {
  if (isCDBForced.value) return 'CDB 模式必填，如 pdb01'
  if (form.pdbname) return ''
  return '可选，填入则启用 CDB'
})

watch(() => form.db_version, (newV, oldV) => {
  if (newV === oldV) return
  if (newV === '11') form.pdbname = ''
  if (newV === '12' || newV === '19') form.pdbname = ''
})

watch(() => form.mode, (newM) => {
  if (newM === 'single') {
    form.data_base_disk = ''
    form.grid_patch = ''
    form.oradata_dir = '/oradata'
    form.archive_dir = '/oradata/archivelog'
  }
  if (newM === 'standalone' || newM === 'rac') {
    form.oradata_dir = '+DATA'
    form.archive_dir = '+ARCH'
    form.data_asm_group = 'DATA'
    form.arch_asm_group = 'ARCH'
  }
})

function onModeChange() {
  // keep form data, computed handles visibility
}

function resetForm() {
  Object.assign(form, DEFAULTS)
}

const { generatedCommand, paramTags } = (() => {
  const result = computed(() => {
    const parts = ['./OracleShellInstall']
    const tags: string[] = []
    const mode = form.mode

    for (const [field, flag] of FLAG_MAP) {
      if (field === 'mode') continue
      if (mode === 'single' && (ASM_FIELDS.has(field) || RAC_FIELDS.has(field))) continue
      if (mode === 'standalone' && RAC_FIELDS.has(field)) continue

      const val = (form as any)[field]
      const valStr = String(val ?? '')
      const defStr = String(DEFAULTS[field] ?? '')
      if (valStr && valStr !== defStr) {
        parts.push(`${flag} ${valStr}`)
        tags.push(`${flag} ${valStr}`)
      }
    }

    parts.push(`-install_mode ${mode}`)

    return { cmd: parts.join(' \\\n    '), tags }
  })

  return {
    generatedCommand: computed(() => result.value.cmd),
    paramTags: computed(() => result.value.tags),
  }
})()

const STEP_DESCRIPTIONS: Record<string, string> = {
  db_version: '安装 {value} 版本数据库',
  hostname: '目标主机名: {value}',
  oracle_user: '使用 {value} 作为 Oracle 软件所有者',
  env_base_dir: '安装根目录: {value}',
  db_name: '创建数据库名称: {value}',
  db_characterset: '数据库字符集: {value}',
  nation_characterset: '国家字符集: {value}',
  db_block_size: '数据库块大小: {value} bytes',
  pdbname: '创建 Pluggable Database: {value}',
  redosize: 'Redo 日志组大小: {value} MB',
  enable_arch: '启用归档日志模式',
  oradata_dir: '数据文件目录: {value}',
  archive_dir: '归档日志目录: {value}',
  data_asm_group: '数据 ASM 磁盘组: {value}',
  arch_asm_group: '归档 ASM 磁盘组: {value}',
  data_base_disk: 'ASM 数据磁盘: {value}',
  data_redun: '数据磁盘组冗余度: {value}',
  local_ifname: '公网网卡: {value}',
  grid_user: '使用 {value} 作为 Grid 软件所有者',
  local_repo: '使用本地软件源',
  huge_flag: '配置大页内存',
  only_conf_os: '仅配置操作系统，不安装数据库',
  install_until_db: '安装到 DB 软件完成',
  install_until_grid: '安装到 Grid 软件完成',
  optimize_db: '安装完成后执行数据库优化',
  oracle_patch: '应用 Oracle PSU/RU 补丁: {value}',
  ojvm_patch: '应用 OJVM PSU/RU 补丁: {value}',
  grid_patch: '应用 Grid PSU/RU 补丁: {value}',
  rac_priv_ifname: 'RAC 心跳网卡: {value}',
  cluster_name: '集群名称: {value}',
  scan_name: 'SCAN 名称: {value}',
  rac_scan_ip: 'SCAN IP: {value}',
  multipath: '启用 Multipath 多路径',
  asm_disk_conf: '脚本自动配置 ASM 磁盘',
  isgui: '安装图形界面',
  net_repo: '使用网络软件源',
  virtualbox: '启用 VirtualBox 修复',
  dns: '配置 DNS',
  timeserver_ip: '时间服务器: {value}',
}

const generatedSteps = computed(() => {
  const steps: string[] = []
  const mode = form.mode
  const modeLabel: Record<string, string> = { single: '单机', standalone: '单机 ASM (Standalone)', rac: 'RAC 集群' }
  steps.push(`安装模式: ${modeLabel[mode] || mode}`)

  for (const [field] of FLAG_MAP) {
    if (mode === 'single' && (ASM_FIELDS.has(field) || RAC_FIELDS.has(field))) continue
    if (mode === 'standalone' && RAC_FIELDS.has(field)) continue
    if (field === 'mode') continue

    const val = String((form as any)[field] ?? '')
    const def = String(DEFAULTS[field] ?? '')
    if (val && val !== def && STEP_DESCRIPTIONS[field]) {
      steps.push(STEP_DESCRIPTIONS[field].replace('{value}', val))
    }
  }

  return steps
})

async function copyCommand() {
  try {
    await navigator.clipboard.writeText(generatedCommand.value)
    ElMessage.success('已复制')
  } catch {
    ElMessage.error('复制失败')
  }
}

async function handleSave() {
  saving.value = true
  try {
    await generateInstallCommand({ ...form })
    ElMessage.success('已保存到历史记录')
  } catch {
    // handled by interceptor
  } finally {
    saving.value = false
  }
}

async function downloadScript() {
  try {
    const token = localStorage.getItem('token')
    const res = await fetch('/api/v1/installer/download-script', {
      headers: { Authorization: `Bearer ${token}` },
    })
    if (!res.ok) {
      const data = await res.json()
      ElMessage.error(data.detail || '下载失败')
      return
    }
    const blob = await res.blob()
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = 'OracleShellInstall.sh'
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    URL.revokeObjectURL(url)
  } catch {
    ElMessage.error('下载失败')
  }
}
</script>

<style scoped>
.installer-page { max-width: 1400px; margin: 0 auto; }
.page-header { margin-bottom: 20px; }
.page-header h2 { font-size: 18px; font-weight: 600; }
.page-desc { font-size: 13px; color: var(--el-text-color-secondary); }

.section-card { margin-bottom: 20px; }
.section-card :deep(.el-card__body) { padding: 20px 24px; }
.section-title { font-size: 14px; font-weight: 600; }

.switch-row {
  display: flex; flex-wrap: wrap; gap: 24px;
  padding: 4px 0;
}
.switch-item {
  display: flex; align-items: center; gap: 8px;
  font-size: 13px; color: var(--el-text-color-regular);
}

.preset-tags { display: flex; gap: 6px; margin-top: 4px; }
.preset-tag { cursor: pointer; }

.action-bar {
  display: flex; gap: 12px; padding: 20px 0;
  justify-content: center;
}

.script-options {
  display: flex; justify-content: space-between; align-items: center;
  margin-bottom: 12px;
}
.tags-area { display: flex; flex-wrap: wrap; gap: 4px; }
.download-btns { display: flex; gap: 6px; }
.drawer-footer { display: flex; gap: 8px; }
</style>
