import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { ToolType, OracleVersion, ConnectionParams, GenerateResponse, ValidationWarning } from '@/types'
import { DEFAULT_CONNECTION, DEFAULT_EXDP_PARAMS, DEFAULT_EXP_PARAMS, DEFAULT_IMDP_PARAMS, DEFAULT_IMP_PARAMS } from '@/utils/constants'

export const useGeneratorStore = defineStore('generator', () => {
  const tool = ref<ToolType>('expdp')
  const connection = ref<ConnectionParams>({ ...DEFAULT_CONNECTION })
  const expdpParams = ref({ ...DEFAULT_EXDP_PARAMS })
  const expParams = ref({ ...DEFAULT_EXP_PARAMS })
  const impdpParams = ref({ ...DEFAULT_IMDP_PARAMS })
  const impParams = ref({ ...DEFAULT_IMP_PARAMS })
  const result = ref<GenerateResponse | null>(null)
  const loading = ref(false)

  const currentParams = computed(() => {
    switch (tool.value) {
      case 'expdp': return expdpParams.value
      case 'exp': return expParams.value
      case 'impdp': return impdpParams.value
      case 'imp': return impParams.value
    }
  })

  function resetParams() {
    switch (tool.value) {
      case 'expdp': expdpParams.value = { ...DEFAULT_EXDP_PARAMS }; break
      case 'exp': expParams.value = { ...DEFAULT_EXP_PARAMS }; break
      case 'impdp': impdpParams.value = { ...DEFAULT_IMDP_PARAMS }; break
      case 'imp': impParams.value = { ...DEFAULT_IMP_PARAMS }; break
    }
    result.value = null
  }

  function resetAll() {
    connection.value = { ...DEFAULT_CONNECTION }
    result.value = null
    resetParams()
  }

  function loadTemplate(data: { connection: any; params: any; tool: ToolType }) {
    tool.value = data.tool
    connection.value = { ...DEFAULT_CONNECTION, ...data.connection }
    switch (data.tool) {
      case 'expdp': expdpParams.value = { ...DEFAULT_EXDP_PARAMS, ...data.params }; break
      case 'exp': expParams.value = { ...DEFAULT_EXP_PARAMS, ...data.params }; break
      case 'impdp': impdpParams.value = { ...DEFAULT_IMDP_PARAMS, ...data.params }; break
      case 'imp': impParams.value = { ...DEFAULT_IMP_PARAMS, ...data.params }; break
    }
    result.value = null
  }

  return {
    tool, connection, expdpParams, expParams, impdpParams, impParams,
    currentParams, result, loading, resetParams, resetAll, loadTemplate,
  }
})
