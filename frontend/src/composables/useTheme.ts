import { ref, watch } from 'vue'

const theme = ref(localStorage.getItem('theme') || 'dark')

export function useTheme() {
  function setTheme(t: string) {
    theme.value = t
    document.documentElement.setAttribute('data-theme', t)
    localStorage.setItem('theme', t)
  }

  function toggleTheme() {
    setTheme(theme.value === 'dark' ? 'light' : 'dark')
  }

  watch(theme, (val) => {
    document.documentElement.setAttribute('data-theme', val)
  }, { immediate: true })

  return { theme, setTheme, toggleTheme }
}
