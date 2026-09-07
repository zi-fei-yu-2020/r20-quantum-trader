export interface AuditCondition { ref: string; op: string; value: number | string | boolean }
export interface DirectionAudit {
  code: string
  reason: string
  evidence: Array<{ ref: string; value: unknown; interpretation: string }>
  reconsider: { conditions: AuditCondition[]; reason: string }
  net_rr_check?: { net_rr: number; minimum: number; scope: string }
}
export interface WaitAuditRecord {
  instId: string
  status: string
  reason?: string
  error?: string | null
  updated_at?: number
  audit?: { long: DirectionAudit; short: DirectionAudit; previous_review?: { reason: string } } | null
  previous_check?: { required?: boolean; trigger_checks?: Record<string, string> }
}
export interface WaitAuditState {
  status: string
  updated_at?: number
  no_entry_candidate_streak?: number
  incomplete_count?: number
  alert?: boolean
  message?: string
  items: WaitAuditRecord[]
}
export interface DecisionCycle {
  timestamp?: string
  status?: string
  evaluated_count?: number
  counts?: Record<string, number>
  environment_notices?: string[]
  unavailable_reason?: string
}
export function auditLabel(status?: string): string {
  return ({ audited_wait: 'WAIT · 审计通过', incomplete: '决策不完整', execution_rejected: '候选被风控拒绝', entry_candidate: '开仓候选 · 待执行核验' } as Record<string, string>)[status || ''] || '待审计'
}
export function conditionText(c: AuditCondition): string {
  if (c.op === 'available') return `${c.ref} 恢复可用`
  const op = ({ gt: '>', gte: '≥', lt: '<', lte: '≤', eq: '=', ne: '≠' } as Record<string, string>)[c.op] || c.op
  return `${c.ref} ${op} ${String(c.value)}`
}
