<template>
  <el-form label-position="top" class="conn-form">
    <el-row :gutter="16">
      <el-col :span="12">
        <el-form-item label="认证方式">
          <el-radio-group :model-value="modelValue.authMethod" @change="update('authMethod', $event)">
            <el-radio-button value="password">密码</el-radio-button>
            <el-radio-button value="wallet">Wallet</el-radio-button>
            <el-radio-button value="os">OS认证</el-radio-button>
          </el-radio-group>
        </el-form-item>
      </el-col>
      <el-col :span="12">
        <el-form-item label="连接类型">
          <el-radio-group :model-value="modelValue.connectType" @change="update('connectType', $event)">
            <el-radio-button value="service">Service Name</el-radio-button>
            <el-radio-button value="sid">SID</el-radio-button>
          </el-radio-group>
        </el-form-item>
      </el-col>
    </el-row>
    <el-row :gutter="16">
      <el-col :span="8">
        <el-form-item label="用户名" required>
          <el-input :model-value="modelValue.username" placeholder="system" @update:model-value="update('username', $event)" />
        </el-form-item>
      </el-col>
      <el-col v-if="modelValue.authMethod === 'password'" :span="8">
        <el-form-item label="密码">
          <el-input :model-value="modelValue.password" type="password" show-password placeholder="请输入密码" @update:model-value="update('password', $event)" />
        </el-form-item>
      </el-col>
      <el-col :span="8">
        <el-form-item :label="modelValue.connectType === 'service' ? 'Service Name' : 'SID'" required>
          <el-input :model-value="modelValue.connectType === 'service' ? modelValue.serviceName : modelValue.sid" :placeholder="modelValue.connectType === 'service' ? 'orcl.example.com' : 'orcl'" @update:model-value="updateIdent($event)" />
        </el-form-item>
      </el-col>
    </el-row>
    <el-row :gutter="16">
      <el-col :span="12">
        <el-form-item label="主机地址" required>
          <el-input :model-value="modelValue.host" placeholder="192.168.1.100" @update:model-value="update('host', $event)" />
        </el-form-item>
      </el-col>
      <el-col :span="4">
        <el-form-item label="端口">
          <el-input-number :model-value="modelValue.port" :min="1" :max="65535" @update:model-value="update('port', $event)" controls-position="right" style="width: 100%" />
        </el-form-item>
      </el-col>
    </el-row>

    <el-row :gutter="16">
      <el-col :span="12">
        <el-form-item label="容器模式">
          <el-radio-group :model-value="modelValue.containerMode" @change="update('containerMode', $event)">
            <el-radio-button value="">无</el-radio-button>
            <el-radio-button value="CDB">CDB</el-radio-button>
            <el-radio-button value="PDB">PDB</el-radio-button>
          </el-radio-group>
          <div class="param-hint">CDB 模式自动添加 CONTAINER=ALL（需 12c+），PDB 模式需设置对应 Service Name</div>
        </el-form-item>
      </el-col>
      <el-col v-if="modelValue.containerMode === 'PDB'" :span="12">
        <el-form-item label="PDB 名称">
          <el-input :model-value="modelValue.pdbName" placeholder="pdb1" @update:model-value="update('pdbName', $event)" />
        </el-form-item>
      </el-col>
    </el-row>

    <el-divider content-position="left">
      <el-switch
        :model-value="modelValue.sshEnabled"
        @change="update('sshEnabled', $event)"
        active-text="SSH 隧道"
        inactive-text=""
      />
    </el-divider>

    <template v-if="modelValue.sshEnabled">
      <el-row :gutter="16">
        <el-col :span="12">
          <el-form-item label="SSH 主机">
            <el-input :model-value="modelValue.sshHost" placeholder="跳板机地址" @update:model-value="update('sshHost', $event)" />
          </el-form-item>
        </el-col>
        <el-col :span="6">
          <el-form-item label="SSH 端口">
            <el-input-number :model-value="modelValue.sshPort" :min="1" :max="65535" @update:model-value="update('sshPort', $event)" controls-position="right" style="width: 100%" />
          </el-form-item>
        </el-col>
        <el-col :span="6">
          <el-form-item label="SSH 用户名">
            <el-input :model-value="modelValue.sshUsername" @update:model-value="update('sshUsername', $event)" />
          </el-form-item>
        </el-col>
      </el-row>
      <el-form-item label="SSH 认证方式">
        <el-radio-group :model-value="modelValue.sshAuthMethod" @change="update('sshAuthMethod', $event)">
          <el-radio-button value="password">密码</el-radio-button>
          <el-radio-button value="key">密钥</el-radio-button>
        </el-radio-group>
      </el-form-item>
      <el-form-item v-if="modelValue.sshAuthMethod === 'password'" label="SSH 密码">
        <el-input :model-value="modelValue.sshPassword" type="password" show-password placeholder="SSH 密码" @update:model-value="update('sshPassword', $event)" />
      </el-form-item>
      <template v-else>
        <el-form-item label="密钥路径">
          <el-input :model-value="modelValue.sshKeyPath" placeholder="~/.ssh/id_rsa" @update:model-value="update('sshKeyPath', $event)" />
        </el-form-item>
        <el-form-item label="密钥密码">
          <el-input :model-value="modelValue.sshKeyPassphrase" type="password" show-password placeholder="可选" @update:model-value="update('sshKeyPassphrase', $event)" />
        </el-form-item>
      </template>
    </template>
  </el-form>
</template>

<script setup lang="ts">
import type { ConnectionParams } from '@/types'

const props = defineProps<{ modelValue: ConnectionParams }>()
const emit = defineEmits<{ 'update:modelValue': [val: ConnectionParams] }>()

function update(key: string, val: any) {
  emit('update:modelValue', { ...props.modelValue, [key]: val })
}
function updateIdent(val: string) {
  if (props.modelValue.connectType === 'service') {
    emit('update:modelValue', { ...props.modelValue, serviceName: val })
  } else {
    emit('update:modelValue', { ...props.modelValue, sid: val })
  }
}
</script>

<style scoped>
.conn-form :deep(.el-form-item) { margin-bottom: 16px; }
.param-hint { font-size: 12px; color: var(--el-text-color-secondary); margin-top: 4px; line-height: 1.4; }
</style>
