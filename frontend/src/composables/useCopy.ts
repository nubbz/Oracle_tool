import { ElMessage } from 'element-plus'

export function useCopy() {
  return function copyText(text: string, label = '已复制') {
    navigator.clipboard.writeText(text).then(() => ElMessage.success(label))
  }
}
