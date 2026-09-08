<script setup lang="ts">
import AppCard from './ui/AppCard.vue'
import { computed } from 'vue'
export interface EvolutionReview {
  status?: string
  last_attempt_at?: string | null
  last_success_at?: string | null
  active_memory_updated_at?: string | null
  review_change_status?: string | null
  sample_size?: number | null
  win_rate?: number | null
  pending_candidates?: number
  rejected_candidates?: number
  insights?: string[]
  recommendations?: string[]
  review_markdown?: string
  message?: string
}
const props = defineProps<{ review?: EvolutionReview }>()
const label = computed(() => ({ success: '复盘已完成', no_new_evidence: '已检查，暂无新增平仓证据', failed: '最近复盘失败，保留上次成功报告', timeout: '最近复盘超时', running: '复盘运行中', not_run: '尚无复盘记录' }[props.review?.status || 'not_run'] || '复盘状态待核验'))
</script>
<template>
  <AppCard class="min-w-0 p-4 sm:p-5 space-y-4" data-evolution-review>
    <header class="flex flex-wrap items-center justify-between gap-2">
      <h3 class="font-semibold text-sm" style="color:var(--text-main)">最新策略复盘</h3>
      <span class="text-xs" role="status" style="color:var(--text-muted)">{{ label }}</span>
    </header>
    <dl class="grid grid-cols-1 sm:grid-cols-3 gap-3 text-xs min-w-0">
      <div><dt style="color:var(--text-muted)">最近尝试（北京时间）</dt><dd class="mt-1 break-words">{{ review?.last_attempt_at || '--' }}</dd></div>
      <div><dt style="color:var(--text-muted)">最近成功报告</dt><dd class="mt-1 break-words">{{ review?.last_success_at || '--' }}</dd></div>
      <div><dt style="color:var(--text-muted)">运行记忆更新</dt><dd class="mt-1 break-words">{{ review?.active_memory_updated_at || '--' }}</dd></div>
    </dl>
    <p class="text-xs leading-relaxed" style="color:var(--text-muted)">复盘报告不等于已应用的策略变更。NO_CHANGE 或建议尚未通过审核时，运行记忆日期不推进，风险参数不会自动修改。</p>
    <div class="flex flex-wrap gap-x-5 gap-y-2 text-xs" style="color:var(--text-main)">
      <span>复盘样本：{{ review?.sample_size ?? '--' }} 笔</span>
      <span>样本胜率：{{ review?.win_rate == null ? '--' : review.win_rate + '%' }}</span>
      <span>变更建议：{{ review?.review_change_status || '--' }}</span>
      <span>待审核建议：{{ review?.pending_candidates ?? '--' }}</span>
      <span>审核未通过：{{ review?.rejected_candidates ?? '--' }}</span>
    </div>
    <ul v-if="review?.insights?.length" class="space-y-2 text-sm leading-relaxed list-disc pl-5" style="overflow-wrap:anywhere">
      <li v-for="(insight,i) in review.insights" :key="i">{{ insight }}</li>
    </ul>
    <p v-else class="text-sm" style="color:var(--text-muted)">暂无可展示的复盘结论，不推断策略处于最优状态。</p>
    <p class="text-xs leading-relaxed" style="color:var(--text-muted)" data-evolution-authority>复盘会生成报告和改进候选，但不会自动改交易规则。增加开单次数不等于提升策略；候选需要费用后表现、前向样本和回退条件验证。</p>
    <details v-if="review?.recommendations?.length" class="action-disclosure min-w-0 text-sm">
      <summary class="cursor-pointer min-h-11 flex items-center">改进建议（未自动执行）</summary>
      <ul class="space-y-2 list-disc pl-5" style="overflow-wrap:anywhere"><li v-for="(item,i) in review.recommendations" :key="i">{{ item }}</li></ul>
    </details>
    <details v-if="review?.review_markdown" class="action-disclosure min-w-0 text-sm">
      <summary class="cursor-pointer min-h-11 flex items-center">原始复盘报告（模型文本，不是执行记录）</summary>
      <pre class="max-h-80 overflow-y-auto whitespace-pre-wrap text-xs leading-relaxed" style="overflow-wrap:anywhere">{{ review.review_markdown }}</pre>
    </details>
  </AppCard>
</template>
