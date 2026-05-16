import api from './index'

export interface RmanBackupParams {
  backup_type: string
  scope: string
  incremental_level?: number
  tablespace_name?: string
  datafile_path?: string
  format_tag?: string
  format_path?: string
  format_pattern?: string
  channel_count?: number
  channel_type?: string
  compression?: string
  encryption?: string
  encryption_algorithm?: string
  encryption_password?: string
  section_size?: string
  skip_offline?: boolean
  skip_readonly?: boolean
  skip_inaccessible?: boolean
  delete_input?: boolean
  retention_policy?: string
  tag?: string
  oracle_home?: string
  include_housekeeping?: boolean
  crosscheck?: boolean
  validate?: boolean
}

export interface RmanRestoreParams {
  restore_type: string
  tablespace_name?: string
  pitr_time?: string
  pitr_scn?: string
  until_sequence?: string
  until_thread?: string
  from_tag?: string
  preview?: boolean
  validate?: boolean
  oracle_home?: string
}

export interface RmanConfigParams {
  settings: Record<string, string>
  oracle_home?: string
}

export function generateRmanBackup(data: RmanBackupParams) {
  return api.post('/rman/backup', data)
}

export function generateRmanRestore(data: RmanRestoreParams) {
  return api.post('/rman/restore', data)
}

export function generateRmanConfig(data: RmanConfigParams) {
  return api.post('/rman/config', data)
}
