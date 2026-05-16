import api from './index'

export interface TemplateItem {
  id: number
  name: string
  description: string
  tool: string
  oracle_version: string
  params: Record<string, any>
  is_builtin: boolean
  created_at: string
  updated_at: string
}

export function getTemplates(tool?: string) {
  return api.get('/templates', { params: { tool } })
}

export function getTemplate(id: number) {
  return api.get(`/templates/${id}`)
}

export function createTemplate(data: { name: string; description?: string; tool: string; oracle_version?: string; params: any }) {
  return api.post('/templates', data)
}

export function updateTemplate(id: number, data: any) {
  return api.put(`/templates/${id}`, data)
}

export function deleteTemplate(id: number) {
  return api.delete(`/templates/${id}`)
}

export function seedBuiltinTemplates() {
  return api.post('/templates/seed')
}
