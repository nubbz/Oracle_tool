import { defineStore } from 'pinia'
import { ref } from 'vue'
import type { OracleVersion } from '@/types'

export const useSettingsStore = defineStore('settings', () => {
  const theme = ref(localStorage.getItem('theme') || 'dark')
  const oracleVersion = ref<OracleVersion>((localStorage.getItem('oracleVersion') as OracleVersion) || '19c')

  function setTheme(t: string) {
    theme.value = t
    document.documentElement.setAttribute('data-theme', t)
    localStorage.setItem('theme', t)
  }

  function toggleTheme() {
    setTheme(theme.value === 'dark' ? 'light' : 'dark')
  }

  function setOracleVersion(v: OracleVersion) {
    oracleVersion.value = v
    localStorage.setItem('oracleVersion', v)
  }

  // init
  document.documentElement.setAttribute('data-theme', theme.value)

  return { theme, oracleVersion, setTheme, toggleTheme, setOracleVersion }
})
