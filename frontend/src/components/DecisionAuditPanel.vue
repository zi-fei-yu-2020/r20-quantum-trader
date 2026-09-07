<script setup lang="ts">
import { computed } from 'vue'
import AppCard from './ui/AppCard.vue'
import { auditLabel, conditionText } from '../utils/waitAudit'
import type { WaitAuditState, DecisionCycle } from '../utils/waitAudit'
const props = defineProps<{ audit?: WaitAuditState; cycle?: DecisionCycle }>()
const rows = computed(() => props.audit?.items || [])
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
    <div class="grid min-w-0 grid-cols-1 gap-2 xl:grid-cols-2">
      <details v-for="row in rows" :key="row.instId" class="min-w-0 rounded-lg border p-2.5"
        style="border-color: var(--border-subtle); background: var(--bg-card-subtle)">
        <summary class="cursor-pointer text-xs leading-relaxed break-words" style="color: var(--text-main)">
          <strong>{{ row.instId.split('-')[0] }}</strong> · {{ auditLabel(row.status) }}
          <span v-if="row.previous_check?.required" class="ml-1">· 前轮条件需复查</span>
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
    <p v-if="cycle?.environment_notices?.length" class="text-xs leading-relaxed break-words" style="color: var(--text-muted)">
      环境限制（非交易动作）：{{ cycle.environment_notices.join('；') }}
    </p>
    <p class="text-[11px] leading-relaxed" style="color: var(--text-faint)">审计通过表示证据与条件可核验，不代表已证明没有交易优势。条件触发仅要求重新研究，不会强制开仓。</p>
  </AppCard>
</template>
