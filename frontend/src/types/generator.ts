export type ToolType = 'expdp' | 'exp' | 'impdp' | 'imp'
export type OracleVersion = '10g' | '11g' | '12c' | '19c' | '21c' | '23c'
export type AuthMethod = 'password' | 'wallet' | 'os'

export interface ConnectionParams {
  username: string
  password: string
  authMethod: AuthMethod
  connectType: 'service' | 'sid'
  serviceName: string
  sid: string
  host: string
  port: number
  sshEnabled: boolean
  sshHost: string
  sshPort: number
  sshUsername: string
  sshAuthMethod: 'password' | 'key'
  sshPassword: string
  sshKeyPath: string
  sshKeyPassphrase: string
  containerMode: '' | 'CDB' | 'PDB'
  pdbName: string
}

export interface ExpdpParams {
  directory: string
  dumpfile: string
  schemas: string[]
  tables: string[]
  tablespaces: string[]
  query: string
  content: 'ALL' | 'METADATA_ONLY' | 'DATA_ONLY'
  exclude: string[]
  include: string[]
  filesize: string
  reuseDumpfiles: boolean
  version: string
  flashbackScn: string
  flashbackTime: string
  encryption: string
  encryptionPassword: string
  encryptionMode: string
  encryptionColumnsOnly: string[]
  transportable: boolean
  transportFullCheck: boolean
  parallel: number
  logfile: string
  compression: string
  jobName: string
  estimate: string
}

export interface ExpParams {
  file: string
  owner: string[]
  tables: string[]
  query: string
  direct: boolean
  compress: boolean
  consistent: boolean
  statistics: string
  buffer: string
  rows: boolean
  indexes: boolean
  constraints: boolean
  grants: boolean
  triggers: boolean
  feedback: number
  fileSize: string
  resumable: boolean
  resumableName: string
  resumableTimeout: number
  recordlength: number
  objectConsistent: boolean
  parallel: number
  logfile: string
  compression: boolean
}

export interface ImpdpParams {
  directory: string
  dumpfile: string
  schemas: string[]
  tables: string[]
  remapSchema: string
  remapTablespace: string
  remapDatafile: string
  remapTable: string
  tableExistsAction: '' | 'SKIP' | 'APPEND' | 'TRUNCATE' | 'REPLACE'
  content: 'ALL' | 'METADATA_ONLY' | 'DATA_ONLY'
  exclude: string[]
  include: string[]
  transform: string
  sqlfile: string
  partitionOptions: string
  dataOptions: string
  disableArchiveLogging: boolean
  encryptionPassword: string
  version: string
  flashbackScn: string
  flashbackTime: string
  networkLink: string
  reuseDatafiles: boolean
  reuseDumpfiles: boolean
  parallel: number
  logfile: string
  compression: string
  jobName: string
  logtime: string
  metrics: boolean
}

export interface ImpParams {
  file: string
  fromuser: string[]
  touser: string[]
  tables: string[]
  commit: boolean
  ignore: boolean
  buffer: string
  statistics: string
  indexes: boolean
  constraints: boolean
  grants: boolean
  triggers: boolean
  rows: boolean
  feedback: number
  recordlength: number
  resumable: boolean
  resumableName: string
  resumableTimeout: number
  show: boolean
  destroy: boolean
  compile: boolean
  indexfile: string
  skipUnusableIndexes: boolean
  streamsize: string
  toidNovalidate: string[]
  filesize: string
  parallel: number
  logfile: string
  compression: boolean
}

export interface ValidationWarning {
  level: 'error' | 'warning' | 'info'
  field: string
  message: string
  suggestion?: string
}

export interface GenerateResponse {
  command: string
  parfile: string
  script: string
  script_bat: string
  warnings: ValidationWarning[]
  recommendations: string[]
  has_error: boolean
  directory_ddl: string
}

export interface GenerateRequest {
  tool: ToolType
  oracleVersion: OracleVersion
  connection: ConnectionParams
  params: Record<string, any>
}
