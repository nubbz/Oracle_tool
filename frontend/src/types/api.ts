export interface UserResponse {
  id: number
  username: string
  display_name: string
  is_active: boolean
}

export interface TokenResponse {
  access_token: string
  token_type: string
  user: UserResponse
}
