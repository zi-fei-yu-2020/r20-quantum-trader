<script setup lang="ts">
import AppCard from './ui/AppCard.vue'
import type { MemoryPublication } from '../utils/memory'
defineProps<{ publication?: MemoryPublication }>()
</script>
<template>
  <AppCard class="min-w-0 p-4 sm:p-5 space-y-3" data-published-memory>
    <header class="flex flex-wrap items-center justify-between gap-2">
      <h3 class="font-semibold text-sm" style="color:var(--text-main)">模型实际运行记忆</h3>
      <span class="text-xs" style="color:var(--text-muted)">{{ publication?.active_version ? `版本 v${publication.active_version}` : publication?.status === 'legacy_unmanaged' ? '兼容旧输入，尚未纳管' : '尚无已发布版本' }}</span>
    </header>
    <p v-if="publication?.status === 'unavailable'" role="alert" class="text-sm" style="color:var(--color-warn)">{{ publication.message || '运行记忆不可用，已阻止回退到其他来源。' }}</p>
    <template v-else>
      <dl class="grid grid-cols-1 sm:grid-cols-3 gap-3 text-xs">
        <div><dt style="color:var(--text-muted)">版本发布 / 纳管时间</dt><dd class="mt-1">{{ publication?.published_at || '--' }}</dd></div>
        <div><dt style="color:var(--text-muted)">有效内容变更时间</dt><dd class="mt-1">{{ publication?.effective_updated_at || '--' }}</dd></div>
        <div><dt style="color:var(--text-muted)">已审核启用规则</dt><dd class="mt-1">{{ (publication?.rules || []).filter(r => r.enabled).length }} 条</dd></div>
      </dl>
      <p v-if="publication?.format === 'legacy_snapshot'" class="text-xs leading-relaxed" style="color:var(--text-muted)">当前内容是旧模型输入的兼容快照，并不表示旧结构化心法已经审核或启用。纳管本身不改变模型实际读取的文字。</p>
      <ul class="space-y-2 text-sm leading-relaxed" style="overflow-wrap:anywhere">
        <li v-for="rule in (publication?.rules || []).filter(r => r.enabled)" :key="rule.id" class="border rounded-lg p-3" style="border-color:var(--border-subtle)">{{ rule.text }}<span class="block mt-1 text-xs font-mono" style="color:var(--text-muted)">{{ rule.id }}</span></li>
      </ul>
      <p v-if="!(publication?.rules || []).some(r => r.enabled)" class="text-sm" style="color:var(--text-muted)">暂无审核发布的启用规则；不会自动加载旧的“黄金基准”。基础策略和执行层风控不受此列表替代。</p>
      <details v-if="publication?.legacy_context" class="action-disclosure text-xs min-w-0" data-memory-disclosure="legacy">
        <summary><span class="min-w-0 flex-1"><span class="block leading-relaxed">当前保留的旧兼容上下文（不是新审批规则）</span><span class="block mt-1 font-normal leading-relaxed" style="color:var(--text-muted)">点击展开历史兼容内容；不会因此启用或修改任何规则。</span></span></summary>
        <pre class="mt-2 max-h-80 overflow-y-auto whitespace-pre-wrap leading-relaxed rounded-lg border p-3" style="overflow-wrap:anywhere;border-color:var(--border-subtle);background:var(--bg-card-subtle)">{{ publication.legacy_context }}</pre>
      </details>
      <details v-if="publication?.prompt_text" class="action-disclosure text-xs min-w-0" data-memory-disclosure="effective">
        <summary><span class="min-w-0 flex-1"><span class="block leading-relaxed">查看模型实际读取的完整记忆文本</span><span class="block mt-1 font-normal leading-relaxed" style="color:var(--text-muted)">核对实际输入原文，与当前版本和内容指纹对应。</span></span></summary>
        <pre class="mt-2 max-h-80 overflow-y-auto whitespace-pre-wrap leading-relaxed rounded-lg border p-3" style="overflow-wrap:anywhere;border-color:var(--border-subtle);background:var(--bg-card-subtle)">{{ publication.prompt_text }}</pre>
      </details>
      <p v-if="publication?.prompt_hash" class="text-[11px] break-all font-mono" style="color:var(--text-faint)">内容指纹 {{ publication.prompt_hash }}</p>
    </template>
  </AppCard>
</template>
