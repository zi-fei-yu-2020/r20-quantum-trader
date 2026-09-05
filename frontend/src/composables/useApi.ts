import { ref } from 'vue'
import { useAuthStore } from '../stores/auth'
import { createSingleFlight } from '../utils/singleFlight'

const sharedReads = createSingleFlight<any>()
let readEpoch = 0

export function useApi() {
  const loading = ref(false)
  const error = ref<string | null>(null)
  let pending = 0

  async function api<T = any>(path: string, options: RequestInit = {}): Promise<T> {
    const auth = useAuthStore()
    const session = auth.token
    const isRead = (options.method || 'GET').toUpperCase() === 'GET'
    if (!isRead) readEpoch += 1
    pending += 1
    loading.value = true
    error.value = null
    try {
      const headers = new Headers({ 'Content-Type': 'application/json' })
      if (session) headers.set('X-R20-Session', session)
      new Headers(options.headers).forEach((value, key) => headers.set(key, value))
      const request = async () => {
        const resp = await fetch(path, { ...options, headers })
        let data: any = {}
        try { data = await resp.json() } catch { /* empty response */ }
        if (auth.token !== session) throw new Error('登录状态已变化，请重新加载页面')
        if (resp.status === 401 && session) {
          auth.logout(false)
          throw new Error('会话已过期，请重新登录')
        }
        if (!resp.ok) {
          const detail = Array.isArray(data.detail)
            ? data.detail.map((x: any) => `${(x.loc || []).slice(1).join('.') || '请求'}：${x.msg}`).join('；')
            : data.detail
          throw new Error(detail || `HTTP ${resp.status}`)
        }
        return data
      }
      const canShare = isRead && Object.keys(options).every(key => key === 'method' || key === 'headers')
      const key = JSON.stringify([session, readEpoch, path, [...headers.entries()]])
      return await (canShare ? sharedReads(key, request) : request()) as T
    } catch (e: any) {
      error.value = e.message || String(e)
      throw e
    } finally {
      // A post-save refresh must not join a read started before the mutation.
      if (!isRead) readEpoch += 1
      pending -= 1
      loading.value = pending > 0
    }
  }

  return { loading, error, api }
}
