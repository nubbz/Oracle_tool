import { ElMessage } from 'element-plus'

export function useClipboard() {
  async function copy(text: string, label = '内容') {
    try {
      await navigator.clipboard.writeText(text)
      ElMessage.success(`${label}已复制到剪贴板`)
    } catch {
      ElMessage.error('复制失败，请手动复制')
    }
  }

  return { copy }
}
