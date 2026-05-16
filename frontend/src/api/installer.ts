import api from './index'

export function generateInstallCommand(data: any) {
  return api.post('/installer/generate', data)
}
