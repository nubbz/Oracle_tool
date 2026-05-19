import api from './index'

export interface SqlldrParams {
  table_name: string
  data_file: string
  load_method: string
  fields_terminated_by: string
  fields_optionally_enclosed_by: string
  lines_terminated_by: string
  skip_rows: number
  columns: string
  direct_path: boolean
  parallel: boolean
  bindsize: string
  rows: string
  errors: string
  discardmax: string
  log_file: string
  bad_file: string
  discard_file: string
  host: string
  port: number
  username: string
  password: string
  service_name: string
  sid: string
  connect_type: string
  oracle_home: string
}

export interface SqlldrResult {
  command: string
  control_file: string
  script: string
  warnings: { level: string; field: string; message: string; suggestion?: string }[]
  recommendations: string[]
}

export function generateSqlldr(data: SqlldrParams) {
  return api.post<SqlldrResult>('/sqlldr/generate', data)
}
