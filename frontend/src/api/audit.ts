import api from './index'

export function getAuditLogs(action?: string, page?: number, pageSize?: number) {
  return api.get('/audit', { params: { action, page, page_size: pageSize } })
}
