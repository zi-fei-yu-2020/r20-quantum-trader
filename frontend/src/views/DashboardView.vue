<script setup lang="ts">
import { computed, ref, onMounted, onUnmounted, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useDashboardStore } from '../stores/dashboard'
import HeaderBar from '../components/HeaderBar.vue'
import TopHudRibbon from '../components/TopHudRibbon.vue'
import TacticalDesk from '../components/TacticalDesk.vue'
import InstrumentMatrix from '../components/InstrumentMatrix.vue'
import LedgerLogs from '../components/LedgerLogs.vue'
import NewsIntelligence from '../components/NewsIntelligence.vue'
import SelfEvolutionLab from '../components/SelfEvolutionLab.vue'
import TradesLedger from '../components/TradesLedger.vue'
import AiBrainHistory from '../components/AiBrainHistory.vue'
import FloatingActions from '../components/FloatingActions.vue'
import AboutModal from '../components/AboutModal.vue'
import PageHeader from '../components/ui/PageHeader.vue'
import AppBadge from '../components/ui/AppBadge.vue'
import { Columns2, Rows2, RefreshCw, Info } from 'lucide-vue-next'
const router = useRouter()
const route = useRoute()
const store = useDashboardStore()
const layoutMode = ref<'dual' | 'stacked'>('stacked')
const descriptions = {
  trading: ['交易概览', '账户、持仓与市场信号，在一个视图中保持同步。'],
  factors: ['AI 决策', '回溯模型判断与投委会讨论，了解每一轮策略的依据。'],
  news: ['市场情报', '关注影响市场的新闻、情绪与资金动向。'],
  lab: ['策略复盘', '查看交易复盘与长期记忆，追踪策略的持续演进。'],
  history: ['交易记录', '查阅订单生命周期、历史成交与执行日志。'],
} as const
const heading = computed(() => descriptions[store.activeTab])
const hasAccount = computed(() => store.data?.account?.total_eq != null)
function syncTabFromRoute() {
  const tab = route.meta.tab
  if (typeof tab === 'string' && tab in descriptions)
    store.activeTab = tab as keyof typeof descriptions
  else if (route.path === '/') store.activeTab = 'trading'
}
watch(() => route.path, syncTabFromRoute)
watch(
  () => store.activeTab,
  (tab) => {
    const path = tab === 'trading' ? '/' : `/${tab}`
    if (route.path !== path && !route.path.startsWith('/admin') && !route.path.startsWith('/docs'))
      router.replace(path)
  },
)
onMounted(() => {
  syncTabFromRoute()
  store.startPolling(3000)
  try {
    if (localStorage.getItem('r20_dashboard_layout_v2') === 'dual') layoutMode.value = 'dual'
  } catch {
    /* optional preference */
  }
})
onUnmounted(() => store.stopPolling())
function setLayout(mode: 'dual' | 'stacked') {
  layoutMode.value = mode
  try {
    localStorage.setItem('r20_dashboard_layout_v2', mode)
  } catch {
    /* optional preference */
  }
}
</script>
<template>
  <div class="terminal-shell">
    <HeaderBar />
    <main class="terminal-main">
      <PageHeader :title="heading[0]" :description="heading[1]" eyebrow="工作空间 / 监控终端"
        ><template #actions>
          <AppBadge v-if="store.data?.okx_environment" :tone="store.data.okx_environment === 'demo' ? 'neutral' : 'warning'">
            {{ store.data.okx_environment === 'demo' ? 'OKX 模拟盘' : 'OKX 实盘' }}
          </AppBadge>
          <AppBadge
            :tone="store.error ? 'danger' : !hasAccount || store.isStale ? 'warning' : 'success'"
            dot
            >{{
              store.error
                ? '连接异常'
                : !hasAccount || store.isStale
                  ? '等待有效数据'
                  : '数据已更新'
            }}</AppBadge
          ><button
            class="ui-icon-button"
            :disabled="store.isRefreshing"
            aria-label="刷新监控数据"
            @click="store.fetchDashboard()"
          >
            <RefreshCw class="size-4" :class="{ 'animate-spin': store.isRefreshing }" />
          </button>
          <div
            v-if="store.activeTab === 'trading'"
            class="hidden lg:flex border rounded-lg p-0.5 bg-[var(--bg-card)]"
          >
            <button
              class="ui-icon-button"
              :style="{ color: layoutMode === 'stacked' ? 'var(--color-brand)' : undefined }"
              :aria-pressed="layoutMode === 'stacked'"
              aria-label="切换纵向布局"
              @click="setLayout('stacked')"
            >
              <Rows2 class="size-4" /></button
            ><button
              class="ui-icon-button"
              :style="{ color: layoutMode === 'dual' ? 'var(--color-brand)' : undefined }"
              :aria-pressed="layoutMode === 'dual'"
              aria-label="切换分栏布局"
              @click="setLayout('dual')"
            >
              <Columns2 class="size-4" />
            </button></div></template
      ></PageHeader>
      <div
        v-if="store.error || !hasAccount || store.isStale"
        class="connection-notice"
        role="status"
      >
        <Info class="size-5 shrink-0" />
        <div>
          <strong>{{
            store.error
              ? '暂时无法获取监控数据'
              : !hasAccount
                ? '账户数据尚未就绪'
                : '当前显示最近一次有效快照'
          }}</strong>
          <p class="mt-1">
            {{
              store.error ||
              '请在控制台核对账户连接与任务状态。未就绪的数据以“—”展示，不会用模拟收益代替。'
            }}
          </p>
        </div>
      </div>
      <div
        v-show="store.activeTab === 'trading'"
        class="terminal-overview"
        :class="{ 'terminal-overview--dual': layoutMode === 'dual' }"
      >
        <div class="terminal-overview__left"><TopHudRibbon /><TacticalDesk /></div>
        <InstrumentMatrix />
      </div>
      <div v-show="store.activeTab === 'factors'" class="terminal-grid"><AiBrainHistory /></div>
      <div v-show="store.activeTab === 'news'" class="terminal-grid"><NewsIntelligence /></div>
      <div v-show="store.activeTab === 'lab'" class="terminal-grid"><SelfEvolutionLab /></div>
      <div v-show="store.activeTab === 'history'" class="terminal-grid">
        <TradesLedger /><LedgerLogs />
      </div>
    </main>
    <footer class="terminal-footer">
      <button @click="store.showAboutModal = true">R20 Quantum Trader · v7.3.0</button
      ><span class="ml-4 hidden sm:inline">只读监控 · 交易有风险，决策需审慎</span>
    </footer>
    <FloatingActions /><AboutModal
      :visible="store.showAboutModal"
      @close="store.showAboutModal = false"
    />
  </div>
</template>
