<script setup lang="ts">
import { computed } from 'vue'
import AppCard from './ui/AppCard.vue'
import AppBadge from './ui/AppBadge.vue'
import { useDashboardStore } from '../stores/dashboard'

const store = useDashboardStore()
const stats = computed(() => store.data?.horizon_stats || {})
const profile = computed(() => store.data?.execution_profile)
const wait = computed(() => store.data?.decision_cycle)
const waitState = computed(() => store.data?.wait_state)
const stat = (key: string) => stats.value[key] || {}
const pct = (v: unknown) => v == null ? '--' : `${(Number(v) * 100).toFixed(1)}%`
const money = (v: unknown) => v == null ? '--' : `${Number(v).toFixed(2)} U`
const waitLabel = computed(() => {
  if (waitState.value?.detail) return waitState.value.detail
  if (wait.value?.unavailable_reason) return wait.value.unavailable_reason
  const counts = wait.value?.counts || {}
  if (Number(counts.entry_candidate || 0) > 0) return 'Executable candidates are being reviewed'
  if (Number(counts.incomplete || 0) > 0) return 'Some decisions need completion'
  return 'No executable candidate in the latest closed-candle frame'
})
</script>

<template>
  <div class="grid gap-3 md:grid-cols-2" data-strategy-telemetry>
    <AppCard class="p-4 min-w-0">
      <div class="flex items-center justify-between gap-3 mb-3">
        <div><p class="text-xs uppercase tracking-wider" style="color:var(--text-faint)">Strategy telemetry</p><h3 class="font-semibold mt-1">SCALP / SWING</h3></div>
        <AppBadge tone="brand">{{ profile?.execution?.id || '--' }}</AppBadge>
      </div>
      <div class="grid grid-cols-2 gap-3">
        <div class="rounded-lg p-3" style="background:var(--bg-card-subtle)"><p class="text-xs" style="color:var(--text-muted)">SCALP net</p><p class="text-lg font-bold num-tabular" :style="{color:Number(stat('scalp').net_pnl || 0)>=0?'var(--color-up)':'var(--color-down)'}">{{ money(stat('scalp').net_pnl) }}</p><p class="text-xs" style="color:var(--text-faint)">{{ stat('scalp').closed || 0 }} trades - {{ stat('scalp').wins || 0 }} wins</p></div>
        <div class="rounded-lg p-3" style="background:var(--bg-card-subtle)"><p class="text-xs" style="color:var(--text-muted)">SWING net</p><p class="text-lg font-bold num-tabular" :style="{color:Number(stat('swing').net_pnl || 0)>=0?'var(--color-up)':'var(--color-down)'}">{{ money(stat('swing').net_pnl) }}</p><p class="text-xs" style="color:var(--text-faint)">{{ stat('swing').closed || 0 }} trades - {{ stat('swing').wins || 0 }} wins</p></div>
      </div>
    </AppCard>
    <AppCard class="p-4 min-w-0">
      <div class="flex items-center justify-between gap-3 mb-3"><div><p class="text-xs uppercase tracking-wider" style="color:var(--text-faint)">Decision state</p><h3 class="font-semibold mt-1">WAIT is diagnostic, not a lock</h3></div><AppBadge :tone="waitState?.code === 'AI_UNAVAILABLE' || waitState?.code === 'DATA_UNAVAILABLE' ? 'warning' : 'neutral'">{{ wait?.status || 'WAIT' }}</AppBadge></div>
      <p class="text-sm leading-6" style="color:var(--text-muted)">{{ waitLabel }}</p><p class="text-xs mt-2" style="color:var(--text-faint)">Next: {{ waitState?.next_trigger || 'Next closed-candle evaluation' }}</p>
      <div class="mt-3 text-xs grid grid-cols-2 gap-2" style="color:var(--text-faint)"><span>Evaluated {{ wait?.evaluated_count ?? '--' }}</span><span>Candidates {{ wait?.counts?.entry_candidate ?? 0 }}</span><span>Risk/trade {{ profile?.execution?.per_trade_equity_pct == null ? '--' : pct(profile.execution.per_trade_equity_pct) }}</span><span>Daily stop {{ profile?.execution?.daily_drawdown_pct == null ? '--' : pct(profile.execution.daily_drawdown_pct) }}</span></div>
    </AppCard>
  </div>
</template>
