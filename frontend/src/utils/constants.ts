import type { ToolType, OracleVersion } from '@/types'

export const TOOL_OPTIONS: { value: ToolType; label: string; desc: string; icon: string }[] = [
  { value: 'expdp', label: 'expdp', desc: 'Oracle Data Pump 导出（推荐）', icon: 'Upload' },
  { value: 'exp', label: 'exp', desc: 'Oracle 传统导出工具', icon: 'TopRight' },
  { value: 'impdp', label: 'impdp', desc: 'Oracle Data Pump 导入（推荐）', icon: 'Download' },
  { value: 'imp', label: 'imp', desc: 'Oracle 传统导入工具', icon: 'BottomLeft' },
]

export const ORACLE_VERSIONS: { value: OracleVersion; label: string }[] = [
  { value: '10g', label: 'Oracle 10g' },
  { value: '11g', label: 'Oracle 11g' },
  { value: '12c', label: 'Oracle 12c' },
  { value: '19c', label: 'Oracle 19c' },
  { value: '21c', label: 'Oracle 21c' },
  { value: '23c', label: 'Oracle 23c' },
]

export const DEFAULT_CONNECTION = {
  username: '',
  password: '',
  authMethod: 'password' as const,
  connectType: 'service' as const,
  serviceName: '',
  sid: '',
  host: 'localhost',
  port: 1521,
  sshEnabled: false,
  sshHost: '',
  sshPort: 22,
  sshUsername: '',
  sshAuthMethod: 'password' as const,
  sshPassword: '',
  sshKeyPath: '',
  sshKeyPassphrase: '',
  containerMode: '' as const,
  pdbName: '',
}

export const ORACLE_PORT_PRESETS = [1521, 1522, 1526, 2483]

export const ORACLE_SERVICE_PRESETS = [
  { value: 'orcl', label: 'orcl' },
  { value: 'orclpdb', label: 'orclpdb' },
  { value: 'ORCLCDB', label: 'ORCLCDB' },
  { value: 'orcl.example.com', label: '生产模式' },
]

export const ORACLE_ENV_DEFAULTS: Record<string, { port: number; serviceName: string }> = {
  dev: { port: 1521, serviceName: 'orcl' },
  test: { port: 1521, serviceName: 'orcl' },
  uat: { port: 1521, serviceName: 'orcl' },
  production: { port: 1521, serviceName: 'orcl.example.com' },
}

export const DEFAULT_EXDP_PARAMS = {
  directory: '', dumpfile: '', schemas: [], tables: [], tablespaces: [],
  query: '', content: 'ALL' as const, exclude: [], include: [],
  filesize: '', reuseDumpfiles: false, version: '',
  flashbackScn: '', flashbackTime: '',
  encryption: '', encryptionPassword: '', encryptionMode: '', encryptionColumnsOnly: [],
  transportable: false, transportFullCheck: false,
  parallel: 1, logfile: '', compression: 'NONE',
  jobName: '', estimate: '',
}

export const DEFAULT_EXP_PARAMS = {
  file: '', owner: [], tables: [], query: '',
  direct: false, compress: false, consistent: false, statistics: 'ESTIMATE',
  buffer: '', rows: true, indexes: true, constraints: true, grants: true, triggers: true,
  feedback: 0, fileSize: '', resumable: false, resumableName: '', resumableTimeout: 0,
  recordlength: 0, objectConsistent: false, parallel: 1, logfile: '', compression: false,
}

export const DEFAULT_IMDP_PARAMS = {
  directory: '', dumpfile: '', schemas: [], tables: [],
  remapSchema: '', remapTablespace: '', remapDatafile: '', remapTable: '',
  tableExistsAction: '' as const,
  content: 'ALL' as const, exclude: [], include: [],
  transform: '', sqlfile: '', partitionOptions: '', dataOptions: '',
  disableArchiveLogging: false, encryptionPassword: '', version: '',
  flashbackScn: '', flashbackTime: '', networkLink: '',
  reuseDatafiles: false, reuseDumpfiles: false,
  parallel: 1, logfile: '', compression: 'NONE',
  jobName: '', logtime: '', metrics: false,
}

export const DEFAULT_IMP_PARAMS = {
  file: '', fromuser: [], touser: [], tables: [],
  commit: false, ignore: false, buffer: '', statistics: 'RECALCULATE',
  indexes: true, constraints: true, grants: true, triggers: true, rows: true,
  feedback: 0, recordlength: 0, resumable: false, resumableName: '', resumableTimeout: 0,
  show: false, destroy: false, compile: false, indexfile: '',
  skipUnusableIndexes: false, streamsize: '', toidNovalidate: [], filesize: '',
  parallel: 1, logfile: '', compression: false,
}
