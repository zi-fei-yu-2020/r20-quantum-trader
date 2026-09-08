<script setup lang="ts">
import AppDialog from '../components/ui/AppDialog.vue'
import { useClipboard } from '../composables/useClipboard'
const { copyText: copyToClipboard } = useClipboard()
import { ref, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { useTheme } from '../composables/useTheme'
import {
  ShieldCheck,
  Cpu,
  FileText,
  ArrowLeft,
  Copy,
  Terminal,
  Users,
  Brain,
  TrendingUp,
  Layers,
  Lock,
  ShieldAlert,
  ChevronRight,
  Menu,
  X,
  Sun,
  Moon,
  Server,
} from 'lucide-vue-next'

const router = useRouter()
const { theme, toggleTheme } = useTheme()

const activeSection = ref('overview')
const mobileMenuOpen = ref(false)
const copiedTag = ref('')
const zoomImage = ref<string | null>(null)

const sections = [
  { id: 'overview', title: '1. 系统架构与量化哲学', icon: TrendingUp },
  { id: 'dashboard', title: '2. 双翼工作台与资产控制舱', icon: Terminal },
  { id: 'council', title: '3. 可选多模型决策委员会 (Council Pro)', icon: Users },
  { id: 'prompt_studio', title: '4. 提示词策略与语义变量插槽', icon: FileText },
  { id: 'interceptors', title: '5. Python 物理拦截插件 (Fail-Closed)', icon: ShieldCheck },
  { id: 'llm_hub', title: '6. 模型连接与 API 协议支持', icon: Cpu },
  { id: 'self_evolution', title: '7. 自进化认知与长期记忆闭环', icon: Brain },
  { id: 'deployment', title: '8. 生产部署与多通道通知', icon: Server },
  { id: 'faq', title: '9. 常见问题解答与风控底线 (FAQ)', icon: ShieldAlert },
]

async function copyText(text: string, tag: string) {
  if (!(await copyToClipboard(text))) return
  copiedTag.value = tag
  setTimeout(() => {
    copiedTag.value = ''
  }, 2000)
}

function scrollToSection(id: string) {
  activeSection.value = id
  mobileMenuOpen.value = false
  const el = document.getElementById(id)
  if (el) {
    el.scrollIntoView({ behavior: 'smooth', block: 'start' })
  }
}

// Scroll spy
function onScroll() {
  const scrollPos = window.scrollY + 120
  for (let i = sections.length - 1; i >= 0; i--) {
    const el = document.getElementById(sections[i].id)
    if (el && el.offsetTop <= scrollPos) {
      activeSection.value = sections[i].id
      break
    }
  }
}

onMounted(() => {
  window.addEventListener('scroll', onScroll, { passive: true })
})

onUnmounted(() => {
  window.removeEventListener('scroll', onScroll)
})
</script>

<template>
  <div
    class="min-h-screen font-sans transition-colors selection:bg-blue-500/30"
    style="background-color: var(--bg-app); color: var(--text-main)"
  >
    <!-- Top Header Navigation (Slim & Clean) -->
    <header
      class="sticky top-0 z-40 backdrop-blur-md border-b px-3 sm:px-6 h-[48px] flex items-center justify-between transition-colors"
      style="background-color: var(--bg-header); border-color: var(--border-subtle)"
    >
      <div class="flex items-center space-x-2 sm:space-x-3 min-w-0">
        <button
          @click="router.push('/')"
          class="flex items-center space-x-1 px-2 py-1 rounded-lg border text-xs font-mono transition-colors cursor-pointer shadow-xs shrink-0"
          style="
            background-color: var(--bg-card);
            border-color: var(--border-subtle);
            color: var(--text-muted);
          "
          title="返回交易终端"
        >
          <ArrowLeft class="w-3.5 h-3.5" />
          <span class="hidden sm:inline">返回终端</span>
        </button>
        <div
          class="h-4 w-px hidden sm:block shrink-0"
          style="background-color: var(--border-subtle)"
        ></div>
        <div class="flex items-center space-x-1.5 sm:space-x-2 min-w-0">
          <span class="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse shrink-0"></span>
          <span
            class="font-mono font-black text-xs sm:text-sm tracking-wide shrink-0 whitespace-nowrap"
            style="color: var(--text-main)"
          >
            R20 QUANTUM
          </span>
          <span
            class="px-1.5 sm:px-2 py-0.2 rounded text-[10px] font-mono border font-bold shrink-0 whitespace-nowrap"
            style="
              background-color: var(--color-brand-bg);
              color: var(--color-brand);
              border-color: var(--color-brand-border);
            "
          >
            <span class="hidden md:inline">v7.3.0 官方开发与使用指南</span>
            <span class="hidden sm:inline md:hidden">v7.3.0 指南</span>
            <span class="sm:hidden">DOCS</span>
          </span>
        </div>
      </div>

      <div class="flex items-center space-x-1.5 sm:space-x-2 shrink-0">
        <!-- Mobile TOC Drawer Button -->
        <button
          @click="mobileMenuOpen = !mobileMenuOpen"
          class="sm:hidden flex items-center justify-center w-7.5 h-7.5 rounded-lg border transition-all cursor-pointer shadow-xs"
          style="
            background-color: var(--bg-card);
            border-color: var(--border-subtle);
            color: var(--text-main);
          "
          title="目录索引 (TOC)"
        >
          <Menu v-if="!mobileMenuOpen" class="w-3.5 h-3.5" />
          <X v-else class="w-3.5 h-3.5" />
        </button>

        <!-- Theme Toggle -->
        <button
          @click="toggleTheme"
          class="flex items-center justify-center w-7.5 h-7.5 rounded-lg border transition-all cursor-pointer shadow-xs"
          style="
            background-color: var(--bg-card);
            border-color: var(--border-subtle);
            color: var(--text-main);
          "
          :title="theme === 'dark' ? '切换为亮色模式' : '切换为暗色模式'"
        >
          <Sun
            v-if="theme === 'dark'"
            class="w-3.5 h-3.5 text-amber-400 hover:rotate-45 transition-transform"
          />
          <Moon v-else class="w-3.5 h-3.5 text-slate-700 hover:-rotate-12 transition-transform" />
        </button>

        <!-- Admin Portal (Desktop only) -->
        <button
          @click="router.push('/admin')"
          class="hidden sm:flex items-center space-x-1 px-2.5 py-1 rounded-lg border text-xs font-mono cursor-pointer transition-colors shadow-xs"
          style="
            background-color: var(--bg-card);
            border-color: var(--border-subtle);
            color: var(--text-muted);
          "
        >
          <Lock class="w-3.5 h-3.5" />
          <span>控制台</span>
        </button>
      </div>
    </header>

    <!-- Mobile TOC Backdrop Overlay -->
    <div
      v-if="mobileMenuOpen"
      class="fixed inset-0 bg-black/60 backdrop-blur-xs z-40 sm:hidden transition-opacity"
      @click="mobileMenuOpen = false"
    ></div>

    <!-- Main Container -->
    <div class="max-w-7xl mx-auto px-4 sm:px-6 py-6 sm:py-8 flex gap-8">
      <!-- Left Sticky Sidebar (TOC) -->
      <aside
        class="w-64 shrink-0 fixed inset-y-12 left-0 z-50 sm:z-30 sm:bg-transparent p-4 sm:p-0 border-r sm:border-r-0 transition-transform duration-200 sm:translate-x-0 sm:sticky sm:top-16 sm:h-[calc(100vh-5rem)] overflow-y-auto"
        :class="
          mobileMenuOpen
            ? 'translate-x-0 bg-[var(--bg-card)] shadow-2xl'
            : '-translate-x-full sm:translate-x-0'
        "
        style="border-color: var(--border-subtle)"
      >
        <div class="flex items-center justify-between mb-3 px-2">
          <div
            class="text-[11px] font-mono font-bold uppercase tracking-wider"
            style="color: var(--text-faint)"
          >
            目录索引 (TOC)
          </div>
          <button
            @click="mobileMenuOpen = false"
            class="sm:hidden p-1 rounded-lg border text-xs cursor-pointer transition-colors"
            style="
              background-color: var(--bg-card-subtle);
              border-color: var(--border-subtle);
              color: var(--text-muted);
            "
            title="关闭目录"
          >
            <X class="w-3.5 h-3.5" />
          </button>
        </div>
        <nav class="space-y-1">
          <button
            v-for="s in sections"
            :key="s.id"
            @click="scrollToSection(s.id)"
            class="w-full text-left px-3 py-2 rounded-xl text-xs font-medium transition-all flex items-center justify-between group cursor-pointer border"
            :style="
              activeSection === s.id
                ? {
                    backgroundColor: 'var(--color-brand-bg)',
                    color: 'var(--color-brand)',
                    borderColor: 'var(--color-brand-border)',
                    fontWeight: 'bold',
                  }
                : {
                    backgroundColor: 'transparent',
                    borderColor: 'transparent',
                    color: 'var(--text-muted)',
                  }
            "
          >
            <div class="flex items-center space-x-2.5 truncate">
              <component :is="s.icon" class="w-3.5 h-3.5 shrink-0" />
              <span class="truncate">{{ s.title }}</span>
            </div>
            <ChevronRight
              class="w-3 h-3 opacity-0 group-hover:opacity-100 transition-opacity"
              :class="activeSection === s.id ? 'opacity-100' : ''"
            />
          </button>
        </nav>
      </aside>

      <!-- Right Content Area -->
      <main class="min-w-0 flex-1 space-y-14 pb-24">
        <!-- 1. 系统概览与量化哲学 -->
        <section id="overview" class="space-y-4 pt-2">
          <div class="flex items-center space-x-2">
            <span
              class="px-2.5 py-0.5 rounded text-[11px] font-mono font-bold border"
              style="
                background-color: var(--color-brand-bg);
                color: var(--color-brand);
                border-color: var(--color-brand-border);
              "
              >CHAPTER 01</span
            >
            <h2
              class="text-xl sm:text-2xl font-black tracking-wide"
              style="color: var(--text-main)"
            >
              系统架构与量化哲学
            </h2>
          </div>

          <p class="text-xs sm:text-sm leading-relaxed font-sans" style="color: var(--text-muted)">
            <strong>R20 Quantum Trader</strong>
            是一套专为高波动加密货币（Crypto）打造的<strong>机构级全自动波段量化决策与执行系统</strong>。系统依托
            OKX 交易所官方 REST/WebSocket V5 生产 API 与 @okx_ai
            官方交易底座，运行在严格的北京时间（UTC+8）自然日财务基准之上，聚焦 1H~4H
            大级别顺势波段，以<strong>“证据优先、宁缺毋滥、Fail-Closed”</strong
            >为风控目标。系统不保证盈利或零 bug；demo 验证不等于 live 安全，实盘仍需独立核验执行与保护闭环。
          </p>

          <!-- 4 Core Pillars Grid -->
          <div class="grid grid-cols-1 sm:grid-cols-2 gap-3.5 pt-2">
            <div
              class="p-4 rounded-xl border space-y-2 shadow-xs"
              style="background-color: var(--bg-card); border-color: var(--border-subtle)"
            >
              <div
                class="flex items-center space-x-2 text-xs font-mono font-bold"
                style="color: var(--color-up)"
              >
                <ShieldCheck class="w-4 h-4" />
                <span>Fail-Closed 物理硬拦截</span>
              </div>
              <p class="text-xs leading-relaxed" style="color: var(--text-muted)">
                风控不只依赖 LLM 提示词。Python 插件默认检查 4H 顺势、评分合法性、1H ADX 与价格盈亏比；
                最终执行层还会独立复核报价时效、扣除手续费与滑点后的净 RR 及风险预算，高评分不能绕过这些 gate。
              </p>
            </div>

            <div
              class="p-4 rounded-xl border space-y-2 shadow-xs"
              style="background-color: var(--bg-card); border-color: var(--border-subtle)"
            >
              <div
                class="flex items-center space-x-2 text-xs font-mono font-bold"
                style="color: var(--color-brand)"
              >
                <Users class="w-4 h-4" />
                <span>多模型决策委员会 (Council Pro)</span>
              </div>
              <p class="text-xs leading-relaxed" style="color: var(--text-muted)">
                默认单脑决策，Council 为可选模式。启用后，各交易员并发提交方案，由 CIO 模型终审；不是数值加权投票，也不提供额外交易授权。
              </p>
            </div>

            <div
              class="p-4 rounded-xl border space-y-2 shadow-xs"
              style="background-color: var(--bg-card); border-color: var(--border-subtle)"
            >
              <div
                class="flex items-center space-x-2 text-xs font-mono font-bold"
                style="color: var(--text-main)"
              >
                <Layers class="w-4 h-4" />
                <span>语义数据插槽提示词系统</span>
              </div>
              <p class="text-xs leading-relaxed" style="color: var(--text-muted)">
                全网快讯、自进化心法、多标的数理矩阵等动态数据抽象为标准语义变量插槽（如
                <code>&#123;&#123;news_intelligence&#125;&#125;</code
                >），支持模块自由解耦与策略方案一键导入导出。
              </p>
            </div>

            <div
              class="p-4 rounded-xl border space-y-2 shadow-xs"
              style="background-color: var(--bg-card); border-color: var(--border-subtle)"
            >
              <div
                class="flex items-center space-x-2 text-xs font-mono font-bold"
                style="color: var(--color-warn)"
              >
                <Brain class="w-4 h-4" />
                <span>自进化认知复盘闭环</span>
              </div>
              <p class="text-xs leading-relaxed" style="color: var(--text-muted)">
                自进化按配置时间调度，默认每日北京时间 20:00，基于当前账户已平仓台账生成 review-only 复盘与候选。
                候选不自动推广，也不覆盖现有运行记忆；纳管后统一读取 <code>data/memory_registry.db</code> 的已发布版本，不自动修改权重或风险参数。
              </p>
            </div>
          </div>
        </section>

        <!-- 2. 双翼工作台与资产控制舱 -->
        <section
          id="dashboard"
          class="space-y-4 pt-6 border-t"
          style="border-color: var(--border-subtle)"
        >
          <div class="flex items-center space-x-2">
            <span
              class="px-2.5 py-0.5 rounded text-[11px] font-mono font-bold border"
              style="
                background-color: var(--color-brand-bg);
                color: var(--color-brand);
                border-color: var(--color-brand-border);
              "
              >CHAPTER 02</span
            >
            <h2
              class="text-xl sm:text-2xl font-black tracking-wide"
              style="color: var(--text-main)"
            >
              双翼量化工作台与资产控制舱
            </h2>
          </div>

          <p class="text-xs sm:text-sm leading-relaxed font-sans" style="color: var(--text-muted)">
            前台终端采用机构级**「双翼量化工作台（Dual-Wing Workstation）」**架构，支持在宽屏下的
            62% : 38% 双翼并行视角与全景纵向视角间一键切换：
          </p>

          <div class="grid grid-cols-1 md:grid-cols-2 gap-3.5 pt-1 text-xs font-mono">
            <div
              class="p-3.5 rounded-xl border space-y-1.5"
              style="background-color: var(--bg-card); border-color: var(--border-subtle)"
            >
              <div class="font-bold text-sm" style="color: var(--text-main)">
                左翼：主控与操盘中心 (62%)
              </div>
              <p style="color: var(--text-muted)">
                •
                <strong>4 单元独立 Bento 资产控制舱</strong
                >：官方总权益、基准净盈亏水线、今日已结、持仓净盈亏分离解耦。<br />
                •
                <strong>高密度交互式操盘台 (Tactical Desk)</strong
                >：分段查看当前 demo/live 环境的持仓与限价挂单池，支持币种快速筛选与云端 OCO 止损覆盖状态核验；展示不等于保护必然生效。
              </p>
            </div>
            <div
              class="p-3.5 rounded-xl border space-y-1.5"
              style="background-color: var(--bg-card); border-color: var(--border-subtle)"
            >
              <div class="font-bold text-sm" style="color: var(--text-main)">
                右翼：六币因果动力学与微结构雷达 (38%)
              </div>
              <p style="color: var(--text-muted)">
                • <strong>微积分物理动能指标</strong>：实时计算一阶速度 $v$、二阶加速度
                $a$、三阶冲击 $j$ 与 ADX 趋势动量。<br />
                •
                <strong>聪明钱微结构</strong
                >：追踪大户多空比与净流入流出，点击卡片即刻呼出深度数学推演与当轮实发 Prompt 抽屉。
              </p>
            </div>
          </div>

          <p class="text-xs leading-relaxed" style="color: var(--text-muted)">
            <strong>账户切换：</strong>在后台「账户连接」分别管理 demo、live 与资讯绑定；保存候选连接不会切换当前交易账户，绑定与激活环境是独立操作。
            交易绑定需核验目标身份与读取能力；OAuth 读取成功不等于交易授权，当前不能绑定自动交易。
            更换交易账户或切换环境需显式确认，受交易锁约束，并核验相关账户无持仓、挂单或保护单、无未确认交易意图；核验失败则拒绝切换，不会自动平仓或撤单。
            demo 验证不等于 live 安全；后台手动平仓开关也不关闭独立止损与持仓风控。
          </p>

          <!-- Screenshot Card -->
          <div
            class="rounded-2xl border p-2 sm:p-3 overflow-hidden shadow-xl group"
            style="background-color: var(--bg-card); border-color: var(--border-subtle)"
          >
            <div
              class="text-[11px] font-mono px-2 py-1 flex items-center justify-between border-b mb-2"
              style="border-color: var(--border-subtle); color: var(--text-muted)"
            >
              <span
                >实机截图 · 双翼量化工作台 (左翼操盘台 + 右翼六币微积分雷达 + 亮暗双模切换)</span
              >
              <span class="font-bold" style="color: var(--color-brand)">点击图片放大</span>
            </div>
            <img
              src="/images/dashboard_trading.png"
              alt="双翼量化工作台全景"
              class="w-full rounded-xl cursor-zoom-in group-hover:opacity-95 transition-opacity"
              @click="zoomImage = '/images/dashboard_trading.png'"
            />
          </div>
        </section>

        <!-- 3. 多模型决策委员会 -->
        <section
          id="council"
          class="space-y-4 pt-6 border-t"
          style="border-color: var(--border-subtle)"
        >
          <div class="flex items-center space-x-2">
            <span
              class="px-2.5 py-0.5 rounded text-[11px] font-mono font-bold border"
              style="
                background-color: var(--color-brand-bg);
                color: var(--color-brand);
                border-color: var(--color-brand-border);
              "
              >CHAPTER 03</span
            >
            <h2
              class="text-xl sm:text-2xl font-black tracking-wide"
              style="color: var(--text-main)"
            >
              多模型决策委员会 (Council Pro)
            </h2>
          </div>

          <p class="text-xs sm:text-sm leading-relaxed font-sans" style="color: var(--text-muted)">
            系统默认单脑，Council 默认关闭、可按需启用。启用后采用<strong>多交易员提案与 CIO 模型终审</strong>，
            各席位审查同一份统一证据；多模型意见不是真实证据或胜率证明，也不能保证消除幻觉。
          </p>

          <div
            class="rounded-xl border p-4 text-xs font-mono space-y-2.5 shadow-xs"
            style="background-color: var(--bg-card); border-color: var(--border-subtle)"
          >
            <div class="font-bold text-xs" style="color: var(--text-main)">
              委员会实际决策流程（非确定性投票）：
            </div>
            <div class="grid grid-cols-1 md:grid-cols-3 gap-2.5 pt-1">
              <div
                class="p-2.5 rounded-lg border"
                style="background-color: var(--bg-card-subtle); border-color: var(--border-subtle)"
              >
                <div class="font-bold" style="color: var(--color-down)">
                  1. 并发交易提案
                </div>
                <div class="text-[11px] mt-1" style="color: var(--text-muted)">
                  已启用的交易员基于统一输入提交支持证据、反证与失效条件，意见仅供终审参考。
                </div>
              </div>
              <div
                class="p-2.5 rounded-lg border"
                style="background-color: var(--bg-card-subtle); border-color: var(--border-subtle)"
              >
                <div class="font-bold" style="color: var(--color-brand)">
                  2. CIO 模型终审
                </div>
                <div class="text-[11px] mt-1" style="color: var(--text-muted)">
                  CIO 汇总审查提案，可全部 WAIT；席位权重不构成数值加权投票，strict / weighted / aggressive 配置名不是确定性表决机制。
                </div>
              </div>
              <div
                class="p-2.5 rounded-lg border"
                style="background-color: var(--bg-card-subtle); border-color: var(--border-subtle)"
              >
                <div class="font-bold" style="color: var(--color-up)">
                  3. 统一契约与执行 gate
                </div>
                <div class="text-[11px] mt-1" style="color: var(--text-muted)">
                  终审输出仍须通过统一证据契约、最终报价与净 RR gate，任何席位均无绕过独立风控的权限。
                </div>
              </div>
            </div>
          </div>

          <!-- Screenshot Card -->
          <div
            class="rounded-2xl border p-2 sm:p-3 overflow-hidden shadow-xl group"
            style="background-color: var(--bg-card); border-color: var(--border-subtle)"
          >
            <div
              class="text-[11px] font-mono px-2 py-1 flex items-center justify-between border-b mb-2"
              style="border-color: var(--border-subtle); color: var(--text-muted)"
            >
              <span
                >实机截图 · 多模型决策委员会控制台 (席位动态启停、思考强度微调与现场辩论测试)</span
              >
              <span class="font-bold" style="color: var(--color-brand)">点击图片放大</span>
            </div>
            <img
              src="/images/admin_council.png"
              alt="多模型委员会控制台"
              class="w-full rounded-xl cursor-zoom-in group-hover:opacity-95 transition-opacity"
              @click="zoomImage = '/images/admin_council.png'"
            />
          </div>
        </section>

        <!-- 4. 提示词策略与变量插槽 -->
        <section
          id="prompt_studio"
          class="space-y-4 pt-6 border-t"
          style="border-color: var(--border-subtle)"
        >
          <div class="flex items-center space-x-2">
            <span
              class="px-2.5 py-0.5 rounded text-[11px] font-mono font-bold border"
              style="
                background-color: var(--color-brand-bg);
                color: var(--color-brand);
                border-color: var(--color-brand-border);
              "
              >CHAPTER 04</span
            >
            <h2
              class="text-xl sm:text-2xl font-black tracking-wide"
              style="color: var(--text-main)"
            >
              提示词策略与语义变量插槽
            </h2>
          </div>

          <p class="text-xs sm:text-sm leading-relaxed font-sans" style="color: var(--text-muted)">
            提示词策略工作室支持对四大核心管线（交易 System、交易
            User、自进化 System、自进化 User）进行可视化定制。引入<strong
              >语义变量插槽（Semantic Slots）</strong
            >引擎；自定义偏好不能覆盖统一证据契约与独立风控：
          </p>

          <p class="text-xs leading-relaxed" style="color: var(--text-muted)">
            单脑与 Council 使用统一证据契约 trading-evidence-v1：支持证据、反证与失效条件必须可核验。
            程序基于闭合（已收盘）的 15M/1H K线生成入场草案；模型可审查草案，也可提出符合契约的独立方案，草案不是下单授权。
            选用 candidate_id 后不得改写草案价格与失效点；最终报价时效、触发有效性、净 RR 与风险预算仍须通过执行 gate。
          </p>

          <!-- Variable Table -->
          <div
            class="rounded-xl border overflow-x-auto shadow-xs"
            style="background-color: var(--bg-card); border-color: var(--border-subtle)"
          >
            <table class="w-full text-left text-xs font-mono whitespace-nowrap">
              <thead>
                <tr
                  class="border-b"
                  style="
                    border-color: var(--border-subtle);
                    background-color: var(--bg-card-subtle);
                    color: var(--text-muted);
                  "
                >
                  <th class="p-3 font-bold">变量占位符</th>
                  <th class="p-3 font-bold">数据分类</th>
                  <th class="p-3 font-bold">注入内容与实战用途</th>
                </tr>
              </thead>
              <tbody class="divide-y" style="border-color: var(--border-subtle)">
                <tr class="hover:bg-[var(--bg-card-hover)] transition-colors">
                  <td class="p-3 font-bold" style="color: var(--color-brand)">
                    &#123;&#123;news_intelligence&#125;&#125;
                  </td>
                  <td class="p-3" style="color: var(--text-main)">全网快讯</td>
                  <td class="p-3" style="color: var(--text-muted)">
                    注入全网最新重大突发要闻、黑天鹅熔断状态与宏观情绪标签
                  </td>
                </tr>
                <tr class="hover:bg-[var(--bg-card-hover)] transition-colors">
                  <td class="p-3 font-bold" style="color: var(--color-up)">
                    &#123;&#123;trading_memory&#125;&#125;
                  </td>
                  <td class="p-3" style="color: var(--text-main)">自进化心法</td>
                  <td class="p-3" style="color: var(--text-muted)">
                    注入当前运行记忆；新复盘候选不会自动进入该插槽
                  </td>
                </tr>
                <tr class="hover:bg-[var(--bg-card-hover)] transition-colors">
                  <td class="p-3 font-bold" style="color: var(--text-main)">
                    &#123;&#123;market_matrix&#125;&#125;
                  </td>
                  <td class="p-3" style="color: var(--text-main)">微积分数理</td>
                  <td class="p-3" style="color: var(--text-muted)">
                    注入 6 币种最新价、微积分动力学 (v/a/j)、1H ADX 与聪明钱净流
                  </td>
                </tr>
                <tr class="hover:bg-[var(--bg-card-hover)] transition-colors">
                  <td class="p-3 font-bold" style="color: var(--color-warn)">
                    &#123;&#123;account_positions&#125;&#125;
                  </td>
                  <td class="p-3" style="color: var(--text-main)">账户敞口</td>
                  <td class="p-3" style="color: var(--text-muted)">
                    注入在途持仓方向、均价、标记价、未结浮盈 UPL 及云端止损防线
                  </td>
                </tr>
                <tr class="hover:bg-[var(--bg-card-hover)] transition-colors">
                  <td class="p-3 font-bold" style="color: var(--color-brand)">
                    &#123;&#123;pending_orders&#125;&#125;
                  </td>
                  <td class="p-3" style="color: var(--text-main)">挂单池</td>
                  <td class="p-3" style="color: var(--text-muted)">
                    注入在途 Maker 限价挂单价格、张数及被动成交状态
                  </td>
                </tr>
              </tbody>
            </table>
          </div>

          <!-- Screenshot Card -->
          <div
            class="rounded-2xl border p-2 sm:p-3 overflow-hidden shadow-xl group"
            style="background-color: var(--bg-card); border-color: var(--border-subtle)"
          >
            <div
              class="text-[11px] font-mono px-2 py-1 flex items-center justify-between border-b mb-2"
              style="border-color: var(--border-subtle); color: var(--text-muted)"
            >
              <span
                >实机截图 · 提示词策略工作室
                (语义插槽工具条、多方案打包导入导出与实发效果实时预览)</span
              >
              <span class="font-bold" style="color: var(--color-brand)">点击图片放大</span>
            </div>
            <img
              src="/images/admin_prompt_studio.png"
              alt="提示词策略工作室"
              class="w-full rounded-xl cursor-zoom-in group-hover:opacity-95 transition-opacity"
              @click="zoomImage = '/images/admin_prompt_studio.png'"
            />
          </div>
        </section>

        <!-- 5. Python 物理拦截插件 -->
        <section
          id="interceptors"
          class="space-y-4 pt-6 border-t"
          style="border-color: var(--border-subtle)"
        >
          <div class="flex items-center space-x-2">
            <span
              class="px-2.5 py-0.5 rounded text-[11px] font-mono font-bold border"
              style="
                background-color: var(--color-brand-bg);
                color: var(--color-brand);
                border-color: var(--color-brand-border);
              "
              >CHAPTER 05</span
            >
            <h2
              class="text-xl sm:text-2xl font-black tracking-wide"
              style="color: var(--text-main)"
            >
              Python 物理拦截插件中心 (Fail-Closed)
            </h2>
          </div>

          <p class="text-xs sm:text-sm leading-relaxed font-sans" style="color: var(--text-muted)">
            发单执行层遵循 <strong>Fail-Closed</strong>：校验异常或风控拒绝时不授权新开仓，候选可降级 WAIT；
            已发出的请求仍需确认与对账，不能把 WAIT 当作撤单或平仓成功。以下四个内置插件默认启用，另有默认关闭的自定义示例；最终执行 gate 独立复核。
          </p>

          <div class="grid grid-cols-1 sm:grid-cols-2 gap-3 pt-1">
            <div
              class="p-3.5 rounded-xl border space-y-1.5 shadow-xs"
              style="background-color: var(--bg-card); border-color: var(--border-subtle)"
            >
              <div class="docs-rule-heading flex items-center justify-between">
                <span class="font-bold text-xs font-mono" style="color: var(--text-main)"
                  >01_macro_trend_filter.py</span
                >
                <span
                  class="px-2 py-0.2 rounded text-[9px] font-bold border"
                  style="
                    background-color: var(--color-up-bg);
                    color: var(--color-up);
                    border-color: var(--color-up-border);
                  "
                  >顺势铁律</span
                >
              </div>
              <p class="text-[11px]" style="color: var(--text-muted)">
                4H 宏观多头通道严禁摸顶开空；4H 空头通道严禁接飞刀做多。
              </p>
            </div>

            <div
              class="p-3.5 rounded-xl border space-y-1.5 shadow-xs"
              style="background-color: var(--bg-card); border-color: var(--border-subtle)"
            >
              <div class="docs-rule-heading flex items-center justify-between">
                <span class="font-bold text-xs font-mono" style="color: var(--text-main)"
                  >02_confidence_gatekeeper.py</span
                >
                <span
                  class="px-2 py-0.2 rounded text-[9px] font-bold border"
                  style="
                    background-color: var(--color-up-bg);
                    color: var(--color-up);
                    border-color: var(--color-up-border);
                  "
                  >评分合法性</span
                >
              </div>
              <p class="text-[11px]" style="color: var(--text-muted)">
                入场 score / confidence 仅校验合法性：须为 0~100 的有限数值且非布尔值，是未校准研究评分而非胜率；无 75/80 硬门槛，也无 Meme 特殊分数线。
                AI 主动平仓（CLOSE_MARKET）的 85 门槛仍单独保留，不适用于入场，也不限制独立止损与保护退出。
              </p>
            </div>

            <div
              class="p-3.5 rounded-xl border space-y-1.5 shadow-xs"
              style="background-color: var(--bg-card); border-color: var(--border-subtle)"
            >
              <div class="docs-rule-heading flex items-center justify-between">
                <span class="font-bold text-xs font-mono" style="color: var(--text-main)"
                  >03_adx_volatility_filter.py</span
                >
                <span
                  class="px-2 py-0.2 rounded text-[9px] font-bold border"
                  style="
                    background-color: var(--color-up-bg);
                    color: var(--color-up);
                    border-color: var(--color-up-border);
                  "
                  >猴市过滤</span
                >
              </div>
              <p class="text-[11px]" style="color: var(--text-muted)">
                默认 ADX 插件对低于18的普通信号保持拦截；已通过证据契约、可重建的收盘触发程序计划可以继续接受最终风控。ADX不是胜率，也不是单独的下单授权。
              </p>
            </div>

            <div
              class="p-3.5 rounded-xl border space-y-1.5 shadow-xs"
              style="background-color: var(--bg-card); border-color: var(--border-subtle)"
            >
              <div class="docs-rule-heading flex items-center justify-between">
                <span class="font-bold text-xs font-mono" style="color: var(--text-main)"
                  >04_risk_reward_gatekeeper.py</span
                >
                <span
                  class="px-2 py-0.2 rounded text-[9px] font-bold border"
                  style="
                    background-color: var(--color-up-bg);
                    color: var(--color-up);
                    border-color: var(--color-up-border);
                  "
                  >价格几何 2.0R</span
                >
              </div>
              <p class="text-[11px]" style="color: var(--text-muted)">
                该插件检查入场、止盈与止损的价格几何 RR ≥ 2.0；最终执行层另按手续费、滑点和最终价格重算净 RR，默认至少 2.0，并检查风险预算。
              </p>
            </div>
          </div>

          <!-- Screenshot Card -->
          <div
            class="rounded-2xl border p-2 sm:p-3 overflow-hidden shadow-xl group"
            style="background-color: var(--bg-card); border-color: var(--border-subtle)"
          >
            <div
              class="text-[11px] font-mono px-2 py-1 flex items-center justify-between border-b mb-2"
              style="border-color: var(--border-subtle); color: var(--text-muted)"
            >
              <span
                >实机截图 · 物理拦截插件中心
                (4H顺势、评分合法性、ADX过滤与现场沙箱测试；历史截图阈值以当前文字说明为准)</span
              >
              <span class="font-bold" style="color: var(--color-brand)">点击图片放大</span>
            </div>
            <img
              src="/images/admin_interceptors.png"
              alt="物理拦截插件中心"
              class="w-full rounded-xl cursor-zoom-in group-hover:opacity-95 transition-opacity"
              @click="zoomImage = '/images/admin_interceptors.png'"
            />
          </div>
        </section>

        <!-- 6. 模型连接与协议格式 -->
        <section
          id="llm_hub"
          class="space-y-4 pt-6 border-t"
          style="border-color: var(--border-subtle)"
        >
          <div class="flex items-center space-x-2">
            <span
              class="px-2.5 py-0.5 rounded text-[11px] font-mono font-bold border"
              style="
                background-color: var(--color-brand-bg);
                color: var(--color-brand);
                border-color: var(--color-brand-border);
              "
              >CHAPTER 06</span
            >
            <h2
              class="text-xl sm:text-2xl font-black tracking-wide"
              style="color: var(--text-main)"
            >
              模型连接与 API 协议支持
            </h2>
          </div>

          <p class="text-xs sm:text-sm leading-relaxed font-sans" style="color: var(--text-muted)">
            后台「模型连接」模块实现了跨厂商无缝兼容，支持纳管市场上所有主流大模型及其代理网关：
          </p>

          <div
            class="rounded-xl border p-4 text-xs font-mono space-y-2 shadow-xs"
            style="background-color: var(--bg-card); border-color: var(--border-subtle)"
          >
            <div class="font-bold text-xs" style="color: var(--text-main)">
              支持的 API 协议标准：
            </div>
            <ul class="space-y-1.5 list-disc list-inside" style="color: var(--text-muted)">
              <li>
                <strong>OpenAI Chat</strong> (<code>/chat/completions</code>)：兼容 DeepSeek
                R1/V3、OpenAI GPT-4o、Qwen 2.5、GLM-4 等绝大部分供应商与 OneAPI/NewAPI 聚合网关。
              </li>
              <li>
                <strong>OpenAI Responses</strong> (<code>/responses</code>)：支持 OpenAI o3-mini、o1
                等新一代推理协议标准。
              </li>
              <li>
                <strong>Claude Messages</strong> (<code>/messages</code>)：原生适配 Anthropic Claude
                3.7 Sonnet / Haiku 及其 Thinking 协议。
              </li>
              <li>
                <strong>思考强度自适应 (Reasoning Effort)</strong>：支持在
                HIGH（长链推理）、MEDIUM、LOW 及 AUTO
                间自由微调，并由执行器自动转换或剥离非兼容参数。
              </li>
            </ul>
          </div>

          <!-- Screenshot Card -->
          <div
            class="rounded-2xl border p-2 sm:p-3 overflow-hidden shadow-xl group"
            style="background-color: var(--bg-card); border-color: var(--border-subtle)"
          >
            <div
              class="text-[11px] font-mono px-2 py-1 flex items-center justify-between border-b mb-2"
              style="border-color: var(--border-subtle); color: var(--text-muted)"
            >
              <span
                >实机截图 · 模型连接控制台
                (全局生效模型卡片、预设一键填入、连通性与思考链时延诊断)</span
              >
              <span class="font-bold" style="color: var(--color-brand)">点击图片放大</span>
            </div>
            <img
              src="/images/admin_llm.png"
              alt="模型连接控制台"
              class="w-full rounded-xl cursor-zoom-in group-hover:opacity-95 transition-opacity"
              @click="zoomImage = '/images/admin_llm.png'"
            />
          </div>
        </section>

        <!-- 7. 自进化认知与长期记忆闭环 -->
        <section
          id="self_evolution"
          class="space-y-4 pt-6 border-t"
          style="border-color: var(--border-subtle)"
        >
          <div class="flex items-center space-x-2">
            <span
              class="px-2.5 py-0.5 rounded text-[11px] font-mono font-bold border"
              style="
                background-color: var(--color-brand-bg);
                color: var(--color-brand);
                border-color: var(--color-brand-border);
              "
              >CHAPTER 07</span
            >
            <h2
              class="text-xl sm:text-2xl font-black tracking-wide"
              style="color: var(--text-main)"
            >
              自进化认知与长期记忆闭环 (review-only)
            </h2>
          </div>

          <p class="text-xs sm:text-sm leading-relaxed font-sans" style="color: var(--text-muted)">
            R20 的自进化是<strong>review-only 复盘与候选审核流程</strong>：按配置时间运行，
            默认每日北京时间 20:00，读取当前账户已平仓台账；demo 样本不等于 live 结果，复盘成功不代表策略已改善或已应用。
          </p>

          <div class="space-y-2 text-xs font-sans" style="color: var(--text-muted)">
            <div>
              • <strong style="color: var(--text-main)">可配置调度</strong>：按保存的复盘时间触发，也支持立即复盘；无新证据可返回 NO_CHANGE，不承诺每次产生新心法；
            </div>
            <div>
              •
              <strong style="color: var(--text-main)">版本化候选审核面板</strong
              >：超级管理员先提交新增、修订或停用候选，核验成交证据、说明理由并确认后发布。显式人工修改也必须走审核发布，不支持直接覆盖运行文件；
            </div>
            <div>
              • <strong style="color: var(--text-main)">报告、候选与运行记忆分离</strong>：复盘报告写入
              <code>self_improvement_review.md</code>，候选、发布历史与当前有效版本统一保存于 <code>data/memory_registry.db</code>。
              候选待证据审核或被拒绝，不自动推广，不自动覆盖现有运行记忆、权重或风险参数。旧 Markdown/JSON 仅作为兼容迁移来源，纳管后不再作为生效入口。
            </div>
            <div>
              • <strong style="color: var(--text-main)">自动证据反馈</strong>：剔除未结算、未知盈亏、账户不匹配或重复样本；只通过真实成交与原始决策精确关联开仓快照，按实际记忆、代码与执行预设追踪费用后结果。未关联不等于零值，分组盈亏不等于策略因果优势。进一步自动推广需要独立前向对照、灰度和回退验证，目前不自动启用。
            </div>
          </div>

          <!-- Screenshot Card -->
          <div
            class="rounded-2xl border p-2 sm:p-3 overflow-hidden shadow-xl group"
            style="background-color: var(--bg-card); border-color: var(--border-subtle)"
          >
            <div
              class="text-[11px] font-mono px-2 py-1 flex items-center justify-between border-b mb-2"
              style="border-color: var(--border-subtle); color: var(--text-muted)"
            >
              <span
                >实机截图 · 自进化认知配置与长期心法记忆库
                (复盘状态、实战心法CRUD管理与立即复盘；历史截图调度以当前配置为准)</span
              >
              <span class="font-bold" style="color: var(--color-brand)">点击图片放大</span>
            </div>
            <img
              src="/images/admin_evolution.png"
              alt="自进化配置与实战心法面板"
              class="w-full rounded-xl cursor-zoom-in group-hover:opacity-95 transition-opacity"
              @click="zoomImage = '/images/admin_evolution.png'"
            />
          </div>
        </section>

        <!-- 8. 生产部署与多通道通知 -->
        <section
          id="deployment"
          class="space-y-4 pt-6 border-t"
          style="border-color: var(--border-subtle)"
        >
          <div class="flex items-center space-x-2">
            <span
              class="px-2.5 py-0.5 rounded text-[11px] font-mono font-bold border"
              style="
                background-color: var(--color-brand-bg);
                color: var(--color-brand);
                border-color: var(--color-brand-border);
              "
              >CHAPTER 08</span
            >
            <h2
              class="text-xl sm:text-2xl font-black tracking-wide"
              style="color: var(--text-main)"
            >
              生产部署与多通道通知告警
            </h2>
          </div>

          <p class="text-xs sm:text-sm leading-relaxed font-sans" style="color: var(--text-muted)">
            系统支持在标准 Linux (Ubuntu/Debian) 云服务器上秒级开箱即用：
          </p>

          <div
            class="rounded-xl border p-4 text-xs font-mono space-y-2 shadow-xs"
            style="background-color: var(--bg-card); border-color: var(--border-subtle)"
          >
            <div class="flex items-center justify-between" style="color: var(--text-muted)">
              <span>极速启动命令序列:</span>
              <button
                @click="
                  copyText(
                    'git clone [your-repository-url].git\ncd r20-quantum-trader\npip install -r requirements.txt\n./scripts/start_standalone.sh',
                    'deploy_cmd',
                  )
                "
                class="flex items-center space-x-1 cursor-pointer hover:underline"
                style="color: var(--color-brand)"
              >
                <Copy class="w-3 h-3" />
                <span>{{ copiedTag === 'deploy_cmd' ? '已复制命令' : '复制命令' }}</span>
              </button>
            </div>
            <pre
              class="p-3 rounded-lg overflow-x-auto leading-relaxed border"
              style="
                background-color: var(--bg-card-subtle);
                border-color: var(--border-subtle);
                color: var(--color-up);
              "
            >
git clone [your-repository-url].git
cd r20-quantum-trader
pip install -r requirements.txt
./scripts/start_standalone.sh</pre
            >
          </div>

          <div class="text-xs space-y-1.5 font-sans" style="color: var(--text-muted)">
            <p><strong style="color: var(--text-main)">支持的告警通知渠道：</strong></p>
            <p>
              1.
              <strong>企业微信 Webhook</strong>：开仓、平仓、止盈止损移动、自进化报告实时推送到群；
            </p>
            <p>
              2. <strong>Telegram Bot</strong>：支持自定义 API Base 反向代理，国内海外无障碍推送；
            </p>
            <p>
              3. <strong>QQ 机器人频道</strong>：支持腾讯官方开放平台 AppID 与 ClientSecret
              私聊推送；
            </p>
            <p>
              4. <strong>通用 Webhook</strong>：支持飞书、钉钉、Discord 及私有运维告警服务无缝对接。
            </p>
          </div>
        </section>

        <!-- 9. 常见问题解答与风控底线 (FAQ) -->
        <section
          id="faq"
          class="space-y-4 pt-6 border-t"
          style="border-color: var(--border-subtle)"
        >
          <div class="flex items-center space-x-2">
            <span
              class="px-2.5 py-0.5 rounded text-[11px] font-mono font-bold border"
              style="
                background-color: var(--color-brand-bg);
                color: var(--color-brand);
                border-color: var(--color-brand-border);
              "
              >CHAPTER 09</span
            >
            <h2
              class="text-xl sm:text-2xl font-black tracking-wide"
              style="color: var(--text-main)"
            >
              常见问题解答与风控底线 (FAQ)
            </h2>
          </div>

          <div class="space-y-3">
            <div
              class="p-4 rounded-xl border space-y-2 shadow-xs"
              style="background-color: var(--bg-card); border-color: var(--border-subtle)"
            >
              <h3 class="text-sm font-bold" style="color: var(--text-main)">
                Q1: 为什么策略推演经常输出 WAIT？是系统出故障了吗？
              </h3>
              <p class="text-xs leading-relaxed" style="color: var(--text-muted)">
                不一定是故障。<strong>WAIT 表示本轮不授权该候选开仓</strong
                >。候选未成立、证据或数据不合格、默认趋势/ADX 插件拦截、最终报价或净 RR 不通过、风险预算不足均可能导致等待。
                应查看本轮审计原因；入场评分没有 75/80 硬门槛，WAIT 也不代表已有持仓或挂单已清空。
              </p>
            </div>

            <div
              class="p-4 rounded-xl border space-y-2 shadow-xs"
              style="background-color: var(--bg-card); border-color: var(--border-subtle)"
            >
              <h3 class="text-sm font-bold" style="color: var(--text-main)">
                Q2: 我的 OKX API Key 和大模型密钥会泄露吗？
              </h3>
              <p class="text-xs leading-relaxed" style="color: var(--text-muted)">
                不能保证绝不泄露。后台对凭据采用掩码展示（如 <code>sk-***abcd</code>），
                但掩码与 <code>.gitignore</code> 都不是完整安全边界；仍需限制主机与备份访问、使用最小权限并妥善保管凭据。
              </p>
            </div>

            <div
              class="p-4 rounded-xl border space-y-2 shadow-xs"
              style="background-color: var(--bg-card); border-color: var(--border-subtle)"
            >
              <h3 class="text-sm font-bold" style="color: var(--text-main)">
                Q3: 如何将策略分享给他人，或从策略广场导入？
              </h3>
              <p class="text-xs leading-relaxed" style="color: var(--text-muted)">
                在后台「提示词策略」页面点击「导出策略方案」即可下载标准
                <code>.json</code> 策略包；在另一台服务器上点击「导入策略」，系统将自动校验 JSON
                结构与变量合法性并即刻装载生效。
              </p>
            </div>
          </div>
        </section>
      </main>
    </div>

    <!-- Image Zoom Modal -->
    <AppDialog
      v-if="zoomImage"
      :open="!!zoomImage"
      title="界面预览"
      size="xl"
      @update:open="
        (open) => {
          if (!open) zoomImage = null
        }
      "
    >
      <img
        :src="zoomImage"
        alt="放大的界面截图"
        class="w-full max-h-[70dvh] object-contain rounded-lg cursor-zoom-out"
        @click="zoomImage = null"
      />
    </AppDialog>
  </div>
</template>
