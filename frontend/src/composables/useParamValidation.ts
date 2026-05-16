import { ref, watchEffect, type Ref } from 'vue'
import type { ToolType } from '@/types'

interface ValidationError {
  field: string
  message: string
  level: 'error' | 'warning'
}

const VERSION_ORDER = ['10g', '11g', '12c', '19c', '21c', '23c']

const MIN_VERSION_PARAMS: Record<string, Record<string, string>> = {
  expdp: {
    encryption: '11g', encryptionPassword: '11g', encryptionMode: '11g',
    encryptionColumnsOnly: '11g', compression: '11g', reuseDumpfiles: '11g',
    transportable: '12c', transportFullCheck: '12c', version: '11g',
    flashbackScn: '10g', flashbackTime: '10g',
  },
  exp: {
    resumable: '9i', resumableName: '9i', resumableTimeout: '9i', objectConsistent: '10g',
  },
  impdp: {
    remapSchema: '10g', remapTablespace: '10g', remapDatafile: '10g',
    tableExistsAction: '10g', networkLink: '10g', encryptionPassword: '11g',
    version: '11g', flashbackScn: '10g', flashbackTime: '10g',
    transform: '11g', sqlfile: '10g', partitionOptions: '11g',
    disableArchiveLogging: '12c', reuseDatafiles: '10g', reuseDumpfiles: '11g',
    compression: '11g', transportable: '12c',
  },
  imp: {
    streamsize: '10g', resumable: '9i', resumableName: '9i',
    resumableTimeout: '9i', skipUnusableIndexes: '10g',
  },
}

function hasValue(v: any): boolean {
  if (v === null || v === undefined) return false
  if (typeof v === 'boolean') return v
  if (typeof v === 'string') return v !== ''
  if (typeof v === 'number') return v !== 0
  if (Array.isArray(v)) return v.length > 0
  return true
}

export function useParamValidation(tool: Ref<ToolType>, params: Ref<any>, oracleVersion?: Ref<string>) {
  const errors = ref<ValidationError[]>([])

  watchEffect(() => {
    const errs: ValidationError[] = []
    const p = params.value
    const t = tool.value
    const ver = oracleVersion?.value || '19c'
    const verIdx = VERSION_ORDER.indexOf(ver)

    // === 必填校验 ===
    if ((t === 'expdp' || t === 'impdp') && !p.directory) {
      errs.push({ field: 'directory', message: 'DIRECTORY 为必填参数', level: 'error' })
    }
    if ((t === 'exp' || t === 'imp') && !p.file) {
      errs.push({ field: 'file', message: 'FILE 为必填参数', level: 'error' })
    }

    // === 互斥校验 ===
    if (t === 'expdp') {
      if (p.schemas?.length > 0 && p.tables?.length > 0) {
        errs.push({ field: 'schemas', message: 'SCHEMAS 和 TABLES 不能同时指定', level: 'error' })
      }
      if (p.schemas?.length > 0 && p.tablespaces?.length > 0) {
        errs.push({ field: 'tablespaces', message: 'SCHEMAS 和 TABLESPACES 不能同时指定', level: 'error' })
      }
    }
    if (t === 'exp') {
      if (p.owner?.length > 0 && p.tables?.length > 0) {
        errs.push({ field: 'owner', message: 'OWNER 和 TABLES 不能同时指定', level: 'error' })
      }
    }
    if (t === 'impdp') {
      if (p.fromuser?.length > 0 && p.tables?.length > 0) {
        errs.push({ field: 'fromuser', message: 'FROMUSER 和 TABLES 不能同时指定', level: 'error' })
      }
    }

    // === Flashback 互斥 ===
    if ((t === 'expdp' || t === 'impdp') && p.flashbackScn && p.flashbackTime) {
      errs.push({ field: 'flashbackScn', message: 'FLASHBACK_SCN 和 FLASHBACK_TIME 不能同时指定', level: 'error' })
    }

    // === 格式校验 ===
    if (t === 'impdp') {
      if (p.remapSchema && !p.remapSchema.includes(':')) {
        errs.push({ field: 'remapSchema', message: 'REMAP_SCHEMA 格式应为 source:target', level: 'error' })
      }
      if (p.remapTable && !p.remapTable.includes(':')) {
        errs.push({ field: 'remapTable', message: 'REMAP_TABLE 格式应为 old_table:new_table', level: 'error' })
      }
      if (p.remapTablespace) {
        for (const mapping of p.remapTablespace.split(',')) {
          if (mapping.trim() && !mapping.trim().includes(':')) {
            errs.push({ field: 'remapTablespace', message: `REMAP_TABLESPACE "${mapping.trim()}" 格式应为 old:new`, level: 'error' })
            break
          }
        }
      }
    }

    // === PARALLEL + DUMPFILE %U ===
    if ((t === 'expdp' || t === 'impdp') && p.parallel > 1 && p.dumpfile && !p.dumpfile.includes('%U')) {
      errs.push({ field: 'dumpfile', message: 'PARALLEL > 1 时 DUMPFILE 应包含 %U 通配符', level: 'warning' })
    }

    // === PARALLEL + FILESIZE 建议 ===
    if (t === 'expdp' && p.parallel > 1 && !p.filesize) {
      errs.push({ field: 'filesize', message: '并行导出建议设置 FILESIZE', level: 'warning' })
    }

    // === 加密矛盾 ===
    if (t === 'expdp' && p.encryption && p.encryption !== 'NONE' && p.encryptionMode === 'NONE') {
      errs.push({ field: 'encryptionMode', message: 'ENCRYPTION_MODE=NONE 与加密参数矛盾', level: 'error' })
    }

    // === FILESIZE 格式 ===
    if ((t === 'expdp' || t === 'impdp') && p.filesize && !/^\d+[BKMGT]$/i.test(p.filesize)) {
      errs.push({ field: 'filesize', message: 'FILESIZE 格式应为 数字+单位（如 2G）', level: 'error' })
    }

    // === 版本兼容性 ===
    if (verIdx >= 0) {
      const minParams = MIN_VERSION_PARAMS[t] || {}
      for (const [param, minVer] of Object.entries(minParams)) {
        const camelKey = param.replace(/_([a-z])/g, (_, c) => c.toUpperCase())
        if (hasValue(p[camelKey]) || hasValue(p[param])) {
          const minIdx = VERSION_ORDER.indexOf(minVer)
          if (minIdx >= 0 && verIdx < minIdx) {
            const fieldName = hasValue(p[camelKey]) ? camelKey : param
            errs.push({ field: fieldName, message: `该参数需要 Oracle ${minVer} 及以上版本（当前 ${ver}）`, level: 'warning' })
          }
        }
      }
    }

    errors.value = errs
  })

  const hasErrors = ref(false)
  watchEffect(() => {
    hasErrors.value = errors.value.some(e => e.level === 'error')
  })

  function getFieldError(field: string): string {
    const err = errors.value.find(e => e.field === field && e.level === 'error')
    return err?.message || ''
  }

  return { errors, hasErrors, getFieldError }
}
