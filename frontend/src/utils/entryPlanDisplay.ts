import type { DecisionCycle } from './waitAudit.ts'
export type CycleItem = NonNullable<DecisionCycle['items']>[number]
export type PlanCheck = NonNullable<CycleItem['entry_plans']>['checks'][number]

export function checkLabel(reason: string): string {
  return ({ existing_macro_direction_veto: '大周期方向限制', quote_moved_beyond_closed_trigger: '报价已偏离收盘触发位置', no_observed_target: '缺少可观察的目标位', closed_candle_trigger_not_met: '收盘触发条件未满足', net_rr_below_policy: '成本后盈亏比未达要求', invalid_geometry: '价格结构无效', market_data_invalid: '行情不可用', environment_not_verified_for_entry: '交易环境尚未核验', entry_candle_provenance_missing: '缺少同一时点的收盘证据' } as Record<string,string>)[reason] || reason || '检查未就绪'
}
export function setupLabel(setup: string): string {
  return ({ all: '全部形态', pullback_reclaim: '回踩回收', closed_range_breakout: '区间突破' } as Record<string,string>)[setup] || setup || '未知形态'
}
export function sideLabel(side: string): string { return side === 'long' ? '做多' : side === 'short' ? '做空' : '方向未明' }
export function decisionLabel(item: CycleItem): string {
  if (item.status === 'incomplete') return '审计未通过'
  if (item.status === 'audited_wait') return '等待 · 审计通过'
  if (item.status === 'execution_rejected') return '执行未通过'
  if (item.status === 'entry_candidate') return '开仓候选 · 待执行核验'
  return item.action === 'WAIT' ? '等待 · 尚未审计' : item.action || '状态待核验'
}
export function incompleteReason(item: CycleItem, fallback?: string | null): string {
  if (item.status !== 'incomplete') return ''
  return (item.reason || fallback || '本轮未提供完整的可核验审计说明').replace(/^WAIT审计不完整[:：]\s*/, '')
}
export function groupedPlanChecks(checks: PlanCheck[] = []) {
  const groups = new Map<string, { key: string; side: string; reason: string; setups: string[]; ratios: number[]; checks: PlanCheck[] }>()
  for (const check of checks) {
    const key = JSON.stringify([check.side, check.reason])
    const group = groups.get(key) || { key, side: check.side, reason: check.reason, setups: [], ratios: [], checks: [] }
    if (!group.setups.includes(check.setup)) group.setups.push(check.setup)
    if (Number.isFinite(check.net_rr) && !group.ratios.includes(check.net_rr!)) group.ratios.push(check.net_rr!)
    group.checks.push(check); groups.set(key, group)
  }
  return [...groups.values()]
}
