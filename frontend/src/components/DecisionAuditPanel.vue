<script setup lang="ts">
import { computed } from 'vue'
import AppCard from './ui/AppCard.vue'
import AppBadge from './ui/AppBadge.vue'
import { checkLabel, setupLabel, sideLabel, decisionLabel, incompleteReason, groupedPlanChecks } from '../utils/entryPlanDisplay'
import { auditLabel, conditionText, reviewLabel } from '../utils/waitAudit'
import type { WaitAuditState, DecisionCycle } from '../utils/waitAudit'
const props = defineProps<{ audit?: WaitAuditState; cycle?: DecisionCycle }>()
const rows = computed(() => props.audit?.items || [])
const planRows = computed(() => (props.cycle?.items || []).filter(item => item.entry_plans).map(item => ({
  ...item, checks: groupedPlanChecks(item.entry_plans?.checks),
  diagnostic: incompleteReason(item, rows.value.find(row => row.instId === item.instId)?.error),
})))
const programPlanCount = computed(() => planRows.value.reduce((sum, row) => sum + (row.entry_plans?.plans?.length || 0), 0))
const timestamp = computed(() => props.audit?.updated_at
  ? new Date(props.audit.updated_at * 1000).toLocaleString('zh-CN', { timeZone: 'Asia/Shanghai', hour12: false })
  : '尚无审计记录')
</script>

<template>
  <AppCard class="min-w-0 max-w-full rounded-xl border p-3 sm:p-4 space-y-3"
    style="background: var(--bg-card); border-color: var(--border-subtle)">
    <header class="flex flex-wrap items-center justify-between gap-2 min-w-0">
      <h3 class="text-sm font-semibold" style="color: var(--text-main)">决策与等待审计</h3>
      <span class="text-xs break-words" style="color: var(--text-muted)">上次审计 · {{ timestamp }}</span>
    </header>
    <p v-if="cycle?.counts" class="text-xs leading-relaxed" style="color: var(--text-muted)">
      本轮审查 {{ cycle.evaluated_count }} 标的 · 候选 {{ cycle.counts.entry_candidate || 0 }} ·
      等待审计通过 {{ cycle.counts.audited_wait || 0 }} · 决策不完整 {{ cycle.counts.incomplete || 0 }} · 风控拒绝 {{ cycle.counts.execution_rejected || 0 }}
    </p>
    <p v-if="audit?.alert || audit?.status === 'error'" role="status" class="rounded-lg border p-2 text-xs leading-relaxed break-words"
      style="background: var(--color-brand-bg); border-color: var(--color-brand-border); color: var(--text-main)">
      {{ audit.message }}<span v-if="audit.alert">（连续 {{ audit.no_entry_candidate_streak }} 轮）</span>
    </p>
    <p v-if="!rows.length" class="text-xs" style="color: var(--text-muted)">
      {{ cycle?.unavailable_reason || '尚未取得结构化审计，不能将旧版 WAIT 视为已通过审查。' }}
    </p>
    <details v-if="planRows.length" class="action-disclosure min-w-0 text-xs" data-entry-plan-review>
      <summary class="cursor-pointer min-h-11 flex items-center" style="color:var(--text-main)"><span class="min-w-0 flex-1"><span class="block">开仓条件与模型审计</span><span class="block mt-1 font-normal leading-relaxed" style="color:var(--text-muted)">{{ programPlanCount ? `本轮 ${programPlanCount} 个程序草案` : '本轮未生成程序草案，展开查看原因' }} · 草案不等于订单</span></span></summary>
      <div class="grid grid-cols-1 xl:grid-cols-2 items-start gap-2 min-w-0 mt-2">
        <section v-for="item in planRows" :key="item.instId" class="min-w-0 border rounded-lg p-3 space-y-2" style="border-color:var(--border-subtle);overflow-wrap:anywhere">
          <header class="flex flex-wrap items-center justify-between gap-2"><strong class="text-sm" style="color:var(--text-main)">{{ item.instId.split('-')[0] }}</strong><AppBadge :tone="item.status === 'incomplete' || item.status === 'execution_rejected' ? 'warning' : 'neutral'">{{ decisionLabel(item) }}</AppBadge></header>
          <p v-if="item.diagnostic" class="rounded-md border p-2 leading-relaxed" data-decision-diagnostic style="border-color:var(--color-warn-border);background:var(--color-warn-bg);color:var(--text-main)">审计未通过：{{ item.diagnostic }}</p>
          <p v-if="item.entry_plans?.error">候选生成未就绪：{{ checkLabel(item.entry_plans.error) }}</p>
          <div v-for="plan in item.entry_plans?.plans || []" :key="plan.id" class="space-y-1">
            <p>{{ plan.action === 'BUY_LONG' ? '做多' : '做空' }} · {{ setupLabel(plan.setup) }} · {{ item.candidate_id === plan.id ? (item.status === 'execution_rejected' ? '模型已选择，但执行未通过' : '模型已选择，仍需执行核验') : '未选择' }}</p>
            <p>入场 {{ plan.entry_price }} · 止损 {{ plan.stop_loss_price }} · 目标 {{ plan.take_profit_price }} · 成本后 R:R {{ Number.isFinite(plan.net_rr) ? plan.net_rr.toFixed(2) : '--' }}</p>
            <p v-for="review in (item.candidate_reviews || []).filter(r => r.candidate_id === plan.id)" :key="review.candidate_id" style="color:var(--text-muted)">拒绝说明：{{ review.reason }}</p>
          </div>
          <div v-if="item.checks.length" class="space-y-2" data-plan-check-summary>
            <div v-for="group in item.checks" :key="group.key" class="flex items-start gap-2 leading-relaxed">
              <span class="shrink-0 rounded px-1.5 py-0.5 text-[10px] font-medium" style="background:var(--bg-card-subtle);color:var(--text-muted)">{{ sideLabel(group.side) }}</span>
              <div class="min-w-0"><p style="color:var(--text-main)">{{ checkLabel(group.reason) }}<span v-if="group.ratios.length">（净 R:R {{ group.ratios.map(value => value.toFixed(2)).join(' / ') }}）</span></p><p class="text-[11px]" style="color:var(--text-muted)">{{ group.setups.map(setupLabel).join('、') }}</p></div>
            </div>
          </div>
          <details v-if="item.entry_plans?.checks?.length" class="action-disclosure min-w-0 text-xs" data-plan-check-details>
            <summary>逐项检查（{{ item.entry_plans.checks.length }} 项）</summary>
            <ul class="mt-2 space-y-2 leading-relaxed" style="color:var(--text-muted)"><li v-for="(check,index) in item.entry_plans.checks" :key="index"><span class="font-medium">{{ sideLabel(check.side) }} · {{ setupLabel(check.setup) }}</span>：{{ checkLabel(check.reason) }}<span v-if="Number.isFinite(check.net_rr)">（净 R:R {{ check.net_rr!.toFixed(2) }}）</span></li></ul>
          </details>
        </section>
      </div>
    </details>
    <div class="grid min-w-0 grid-cols-1 items-start gap-2 xl:grid-cols-2">
      <details v-for="row in rows" :key="row.instId" :data-wait-audit-card="row.instId" class="action-disclosure min-w-0 self-start rounded-lg border p-2.5"
        style="border-color: var(--border-subtle); background: var(--bg-card-subtle)">
        <summary class="cursor-pointer text-xs leading-relaxed break-words" style="color: var(--text-main)">
          <strong>{{ row.instId.split('-')[0] }}</strong> · {{ auditLabel(row.status) }}
          <span v-if="reviewLabel(row)" class="ml-1">· {{ reviewLabel(row) }}</span>
        </summary>
        <div class="mt-2 space-y-2 text-xs leading-relaxed break-words min-w-0" style="color: var(--text-muted); overflow-wrap: anywhere">
          <p v-if="row.error" style="color: var(--text-main)">未通过：{{ row.error }}</p>
          <p>{{ row.reason }}</p>
          <template v-if="row.audit">
            <section v-for="side in (['long', 'short'] as const)" :key="side" class="space-y-1">
              <p class="font-semibold" style="color: var(--text-main)">{{ side === 'long' ? '做多阻碍' : '做空阻碍' }}：{{ row.audit[side].reason }}</p>
              <ul class="space-y-1 pl-3 list-disc">
                <li v-for="(e, index) in row.audit[side].evidence" :key="index">{{ e.ref }} = {{ e.value }} · {{ e.interpretation }}</li>
              </ul>
              <p v-if="row.audit[side].net_rr_check">该方案净盈亏比 {{ row.audit[side].net_rr_check!.net_rr.toFixed(2) }}，门槛 {{ row.audit[side].net_rr_check!.minimum }}；仅否定此方案。</p>
              <p>重审条件（全部满足）：{{ row.audit[side].reconsider.conditions.map(conditionText).join(' 且 ') }}</p>
              <p>{{ row.audit[side].reconsider.reason }}</p>
            </section>
            <p v-if="row.audit.previous_review">继续等待的复查解释：{{ row.audit.previous_review.reason }}</p>
          </template>
        </div>
      </details>
    </div>
    <details v-if="cycle?.executed_actions?.length" class="action-disclosure text-xs min-w-0">
      <summary class="cursor-pointer" style="color: var(--text-main)">本轮完整执行记录（{{ cycle.executed_actions.length }}）</summary>
      <ul class="mt-2 space-y-1 leading-relaxed break-words" style="color: var(--text-muted); overflow-wrap: anywhere">
        <li v-for="(action, index) in cycle.executed_actions" :key="index">{{ action }}</li>
      </ul>
    </details>
    <p v-if="cycle?.environment_notices?.length" class="text-xs leading-relaxed break-words" style="color: var(--text-muted)">
      环境限制（非交易动作）：{{ cycle.environment_notices.join('；') }}
    </p>
    <p class="text-[11px] leading-relaxed" style="color: var(--text-faint)">审计通过表示证据与条件可核验，不代表已证明没有交易优势。条件触发仅要求重新研究，不会强制开仓。</p>
  </AppCard>
</template>
