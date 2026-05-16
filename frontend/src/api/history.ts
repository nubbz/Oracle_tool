import api from './index'

export function getHistory(params?: { tool?: string; page?: number; page_size?: number }) {
  return api.get('/history', { params })
}

export function getHistoryItem(id: number) {
  return api.get(`/history/${id}`)
}

export function deleteHistoryItem(id: number) {
  return api.delete(`/history/${id}`)
}

export function clearHistory() {
  return api.delete('/history')
}
