import api from './index'

export function getEnvironments() {
  return api.get('/environments')
}

export function getEnvironment(id: number) {
  return api.get(`/environments/${id}`)
}

export function createEnvironment(data: any) {
  return api.post('/environments', data)
}

export function updateEnvironment(id: number, data: any) {
  return api.put(`/environments/${id}`, data)
}

export function deleteEnvironment(id: number) {
  return api.delete(`/environments/${id}`)
}

export function testSshConnection(id: number) {
  return api.post(`/environments/${id}/test-ssh`)
}

export function testOracleConnection(id: number, username: string, password: string) {
  return api.post(`/environments/${id}/test-oracle`, { username, password })
}
