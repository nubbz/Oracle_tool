import api from './index'
import type { GenerateRequest, GenerateResponse } from '@/types'

export function generateCommand(data: GenerateRequest) {
  return api.post<GenerateResponse>('/generate', data)
}

export function generateReverse(data: GenerateRequest) {
  return api.post<GenerateResponse>('/generate/reverse', data)
}
