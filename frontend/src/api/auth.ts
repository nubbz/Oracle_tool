import api from './index'

export function login(username: string, password: string) {
  return api.post('/auth/login', { username, password })
}

export function register(username: string, password: string, display_name = '') {
  return api.post('/auth/register', { username, password, display_name })
}

export function getMe() {
  return api.get('/auth/me')
}
