import api from './index'

export function generateOptimizerCommand(data: any) {
  return api.post('/optimizer/generate', data)
}
