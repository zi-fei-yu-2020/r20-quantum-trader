<script setup lang="ts">
import AppCard from './ui/AppCard.vue'
import EvolutionReviewPanel from './EvolutionReviewPanel.vue'
import { computed } from 'vue'
import { useDashboardStore } from '../stores/dashboard'
import { Sparkles, Brain } from 'lucide-vue-next'
const store = useDashboardStore()
const memoryMd = computed(() => store.data?.ai_trading_memory_md || '')
</script>
<template>
  <div class="space-y-3.5 min-w-0">
    <AppCard class="p-4 sm:p-5 flex flex-wrap gap-3 items-center justify-between">
      <div class="min-w-0">
        <h2 class="flex items-center gap-2 text-sm font-semibold" style="color:var(--text-main)"><Sparkles class="size-5 shrink-0" />AI 策略自进化与认知提炼中心</h2>
        <p class="text-xs mt-2 leading-relaxed" style="color:var(--text-muted)">复盘、候选审核与运行记忆分别记录；显示真实任务结果，不自动改动交易规则。</p>
      </div>
      <span class="flex flex-wrap min-w-0 max-w-full items-center gap-2 text-xs break-all" style="color:var(--text-muted)">自进化主脑：{{ store.llmRuntime.model }}</span>
    </AppCard>
    <EvolutionReviewPanel :review="store.data?.evolution_review" />
    <AppCard class="p-4 sm:p-5 min-w-0 space-y-3">
      <header class="flex flex-wrap items-center justify-between gap-2">
        <h3 class="flex items-center gap-2 text-sm font-semibold" style="color:var(--text-main)"><Brain class="size-4" />运行记忆库 (Trading Memory)</h3>
        <span class="text-xs" style="color:var(--text-muted)">与最新复盘报告分别保存</span>
      </header>
      <p class="text-xs leading-relaxed" style="color:var(--text-muted)">这里保留当前运行记忆原文。原文中的历史时间、模型判断不等于本轮任务状态，也不代表已验证收益；最新复盘请看上方。</p>
      <pre class="p-3 rounded-lg border text-xs leading-relaxed max-h-96 overflow-y-auto whitespace-pre-wrap" style="background:var(--bg-card-subtle);border-color:var(--border-subtle);color:var(--text-main);overflow-wrap:anywhere">{{ memoryMd || '暂无运行记忆内容。' }}</pre>
    </AppCard>
  </div>
</template>
