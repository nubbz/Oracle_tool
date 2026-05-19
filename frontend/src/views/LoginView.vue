<template>
  <div class="login-page">
    <div class="login-card">
      <div class="login-header">
        <el-icon :size="36" color="var(--accent)"><Coin /></el-icon>
        <h1>Oracle工具箱</h1>
      </div>

      <el-tabs v-model="mode" class="login-tabs">
        <el-tab-pane label="登录" name="login">
          <el-form :model="loginForm" :rules="loginRules" ref="loginFormRef" @submit.prevent="handleLogin" label-position="top">
            <el-form-item label="用户名" prop="username">
              <el-input v-model="loginForm.username" placeholder="请输入用户名" prefix-icon="User" size="large" />
            </el-form-item>
            <el-form-item label="密码" prop="password">
              <el-input v-model="loginForm.password" type="password" placeholder="请输入密码" prefix-icon="Lock" size="large" show-password @keyup.enter="handleLogin" />
            </el-form-item>
            <el-button type="primary" size="large" :loading="loading" style="width: 100%" @click="handleLogin">登 录</el-button>
          </el-form>
        </el-tab-pane>
        <el-tab-pane label="注册" name="register">
          <el-form :model="regForm" :rules="regRules" ref="regFormRef" @submit.prevent="handleRegister" label-position="top">
            <el-form-item label="用户名" prop="username">
              <el-input v-model="regForm.username" placeholder="请输入用户名" prefix-icon="User" size="large" />
            </el-form-item>
            <el-form-item label="密码" prop="password">
              <el-input v-model="regForm.password" type="password" placeholder="请输入密码（至少6位）" prefix-icon="Lock" size="large" show-password />
            </el-form-item>
            <el-form-item label="确认密码" prop="confirmPassword">
              <el-input v-model="regForm.confirmPassword" type="password" placeholder="请再次输入密码" prefix-icon="Lock" size="large" show-password @keyup.enter="handleRegister" />
            </el-form-item>
            <el-button type="primary" size="large" :loading="loading" style="width: 100%" @click="handleRegister">注 册</el-button>
          </el-form>
        </el-tab-pane>
      </el-tabs>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/authStore'
import { ElMessage } from 'element-plus'
import type { FormInstance, FormRules } from 'element-plus'

const router = useRouter()
const authStore = useAuthStore()
const mode = ref('login')
const loading = ref(false)
const loginFormRef = ref<FormInstance>()
const regFormRef = ref<FormInstance>()
const loginForm = reactive({ username: '', password: '' })
const regForm = reactive({ username: '', password: '', confirmPassword: '' })

const loginRules: FormRules = {
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  password: [{ required: true, message: '请输入密码', trigger: 'blur' }],
}

const regRules: FormRules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    { min: 3, max: 30, message: '用户名长度 3-30 位', trigger: 'blur' },
    { pattern: /^[a-zA-Z0-9_]+$/, message: '用户名只允许字母、数字和下划线', trigger: 'blur' },
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, max: 64, message: '密码长度 6-64 位', trigger: 'blur' },
  ],
  confirmPassword: [
    { required: true, message: '请确认密码', trigger: 'blur' },
    {
      validator: (_rule, value, callback) => {
        if (value !== regForm.password) callback(new Error('两次密码不一致'))
        else callback()
      },
      trigger: 'blur',
    },
  ],
}

async function handleLogin() {
  if (!loginFormRef.value) return
  await loginFormRef.value.validate()
  loading.value = true
  try {
    await authStore.login(loginForm.username, loginForm.password)
    ElMessage.success('登录成功')
    router.push('/')
  } catch { /* error handled by interceptor */ }
  finally { loading.value = false }
}

async function handleRegister() {
  if (!regFormRef.value) return
  await regFormRef.value.validate()
  loading.value = true
  try {
    await authStore.register(regForm.username, regForm.password, regForm.username)
    ElMessage.success('注册成功')
    router.push('/')
  } catch { /* error handled by interceptor */ }
  finally { loading.value = false }
}
</script>

<style scoped>
.login-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--bg-primary);
  padding: 20px;
}
.login-card {
  width: 420px;
  background: var(--bg-secondary);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-lg);
  padding: 40px;
  box-shadow: var(--shadow-lg);
}
.login-header {
  text-align: center;
  margin-bottom: 32px;
}
.login-header h1 {
  font-size: 22px;
  margin-top: 12px;
  color: var(--text-primary);
  font-weight: 600;
}
.subtitle {
  margin-top: 8px;
  color: var(--text-tertiary);
  font-size: 13px;
}
.login-tabs :deep(.el-tabs__nav-wrap::after) {
  background: var(--border-color);
}
</style>
