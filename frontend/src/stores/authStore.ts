import { defineStore } from 'pinia'
import { ref } from 'vue'
import { login as loginApi, register as registerApi, getMe as getMeApi } from '@/api/auth'
import type { UserResponse, TokenResponse } from '@/types/api'

export const useAuthStore = defineStore('auth', () => {
  const token = ref(localStorage.getItem('token') || '')
  const user = ref<{ id: number; username: string; display_name: string; is_active: boolean } | null>(null)

  async function login(username: string, password: string) {
    const { data } = await loginApi(username, password)
    const res: TokenResponse = data
    token.value = res.access_token
    user.value = res.user
    localStorage.setItem('token', res.access_token)
  }

  async function register(username: string, password: string, displayName = '') {
    const { data } = await registerApi(username, password, displayName)
    const res: TokenResponse = data
    token.value = res.access_token
    user.value = res.user
    localStorage.setItem('token', res.access_token)
  }

  async function fetchUser() {
    if (!token.value) return
    try {
      const { data } = await getMeApi()
      user.value = data
    } catch {
      logout()
    }
  }

  function logout() {
    token.value = ''
    user.value = null
    localStorage.removeItem('token')
  }

  return { token, user, login, register, fetchUser, logout }
})
