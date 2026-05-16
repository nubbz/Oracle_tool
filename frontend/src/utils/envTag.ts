const envTypeMap: Record<string, { label: string; type: string }> = {
  production: { label: '生产', type: 'danger' },
  uat: { label: 'UAT', type: 'warning' },
  test: { label: '测试', type: 'info' },
  dev: { label: '开发', type: 'success' },
}

export function envTypeTag(envType: string) {
  return envTypeMap[envType] || { label: envType, type: 'info' }
}
