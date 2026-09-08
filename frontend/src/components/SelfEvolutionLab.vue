<script setup lang="ts">
import AppCard from './ui/AppCard.vue'
import PublishedMemoryPanel from './PublishedMemoryPanel.vue'
import EvolutionReviewPanel from './EvolutionReviewPanel.vue'
import { useDashboardStore } from '../stores/dashboard'
import { Sparkles } from 'lucide-vue-next'
const store = useDashboardStore()
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
    <PublishedMemoryPanel :publication="store.data?.memory_publication" />
  </div>
</template>
