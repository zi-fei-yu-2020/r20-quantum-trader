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
const execution = computed(() => profile.value?.execution || {})
const stat = (key: string) => stats.value[key] || {}
const pct = (v: unknown) => v == null ? '--' : `${(Number(v) * 100).toFixed(1)}%`
const money = (v: unknown) => v == null ? '--' : `${Number(v).toFixed(2)} U`
const profileLabel = computed(() => execution.value.label || execution.value.id || '标准风控')
const waitLabel = computed(() => waitState.value?.detail || wait.value?.unavailable_reason || '等待新的短线或波段候选')
</script>
<template>
  <div class="grid gap-3 xl:grid-cols-3" data-strategy-telemetry>
    <AppCard class="p-4 min-w-0">
      <div class="flex items-center justify-between gap-3 mb-3"><div><p class="text-xs uppercase tracking-wider" style="color:var(--text-faint)">&#x6267;&#x884C;&#x6A21;&#x5F0F;</p><h3 class="font-semibold mt-1">{{ profileLabel }}</h3></div><AppBadge tone="brand">{{ execution.id || '--' }}</AppBadge></div>
      <div class="grid grid-cols-2 gap-2 text-xs" style="color:var(--text-muted)"><span>&#x5355;&#x7B14;&#x98CE;&#x9669; {{ pct(execution.per_trade_equity_pct) }}</span><span>&#x6700;&#x5927;&#x6760;&#x6746; {{ execution.max_leverage ?? '--' }}x</span><span>&#x6301;&#x4ED3;&#x4E0A;&#x9650; {{ execution.max_active_instruments ?? '--' }}</span><span>&#x4FDD;&#x8BC1;&#x91D1;&#x4E0A;&#x9650; {{ execution.total_margin_usdt ?? '--' }}U</span></div>
    </AppCard>
    <AppCard class="p-4 min-w-0">
      <div class="flex items-center justify-between gap-3 mb-3"><div><p class="text-xs uppercase tracking-wider" style="color:var(--text-faint)">&#x7B56;&#x7565;&#x7EDF;&#x8BA1;</p><h3 class="font-semibold mt-1">&#x77ED;&#x7EBF; / &#x6CE2;&#x6BB5;</h3></div><AppBadge tone="neutral">&#x65B0;&#x4EA4;&#x6613;&#x5B9E;&#x65F6;&#x66F4;&#x65B0;</AppBadge></div>
      <div class="grid grid-cols-2 gap-2"><div class="rounded-lg p-3" style="background:var(--bg-card-subtle)"><p class="text-xs" style="color:var(--text-muted)">&#x77ED;&#x7EBF;&#x51C0;&#x76C8;&#x4E8F;</p><p class="text-lg font-bold num-tabular" :style="{color:Number(stat('scalp').net_pnl || 0)>=0?'var(--color-up)':'var(--color-down)'}">{{ money(stat('scalp').net_pnl) }}</p><p class="text-xs" style="color:var(--text-faint)">{{ stat('scalp').closed || 0 }} &#x7B14; ? {{ stat('scalp').wins || 0 }} &#x80DC;</p></div><div class="rounded-lg p-3" style="background:var(--bg-card-subtle)"><p class="text-xs" style="color:var(--text-muted)">&#x6CE2;&#x6BB5;&#x51C0;&#x76C8;&#x4E8F;</p><p class="text-lg font-bold num-tabular" :style="{color:Number(stat('swing').net_pnl || 0)>=0?'var(--color-up)':'var(--color-down)'}">{{ money(stat('swing').net_pnl) }}</p><p class="text-xs" style="color:var(--text-faint)">{{ stat('swing').closed || 0 }} &#x7B14; ? {{ stat('swing').wins || 0 }} &#x80DC;</p></div></div>
    </AppCard>
    <AppCard class="p-4 min-w-0">
      <div class="flex items-center justify-between gap-3 mb-3"><div><p class="text-xs uppercase tracking-wider" style="color:var(--text-faint)">&#x51B3;&#x7B56;&#x72B6;&#x6001;</p><h3 class="font-semibold mt-1">WAIT &#x662F;&#x5F53;&#x524D;&#x72B6;&#x6001;</h3></div><AppBadge :tone="waitState?.code === 'AI_UNAVAILABLE' || waitState?.code === 'DATA_UNAVAILABLE' ? 'warning' : 'neutral'">{{ wait?.status || 'WAIT' }}</AppBadge></div>
      <p class="text-sm leading-6" style="color:var(--text-muted)">{{ waitLabel }}</p><p class="text-xs mt-2" style="color:var(--text-faint)">&#x4E0B;&#x4E00;&#x6B65;&#xFF1A;{{ waitState?.next_trigger || '&#x7B49;&#x5F85;&#x65B0;&#x7684;&#x5019;&#x9009;' }}</p>
      <div class="mt-3 text-xs grid grid-cols-2 gap-2" style="color:var(--text-faint)"><span>&#x5DF2;&#x5BA1;&#x67E5; {{ wait?.evaluated_count ?? '--' }}</span><span>&#x5019;&#x9009; {{ wait?.counts?.entry_candidate ?? 0 }}</span><span>&#x5355;&#x7B14;&#x98CE;&#x9669; {{ pct(execution.per_trade_equity_pct) }}</span><span>&#x65E5;&#x5185;&#x7194;&#x65AD; {{ pct(execution.daily_drawdown_pct) }}</span></div>
    </AppCard>
  </div>
</template>
