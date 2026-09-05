// OKX raw numeric strings and locally aggregated numeric values coexist.
export type NumericValue = string | number
export type TradeAction = 'BUY_LONG' | 'SELL_SHORT' | 'WAIT'

export interface AccountSummary {
  total_eq: number
  avail_eq: number
  cash_bal?: number
  upl?: number
  pos_upl_total?: number
  margin_usage_pct?: number
  margin_ratio?: number
  risk_level?: string
  currency?: string
  initial_capital?: number | null
  baseline_configured?: boolean
  cum_net_pnl?: number | null
  cum_realized_pnl?: number
  cum_roi_pct?: number | null
  cum_total_fees?: number
}

export interface PositionItem {
  instId: string
  name: string
  side: 'long' | 'short'
  pos: NumericValue
  lever: NumericValue
  margin?: NumericValue
  margin_source?: string
  marginSource?: string
  markPx?: NumericValue
  margin_usdt?: number | null
  roi_pct?: number
  roi?: NumericValue // legacy persisted snapshots
  protectionStatus?: 'fully_protected' | 'partially_protected' | 'unprotected' | 'unknown_stale' | 'verification_stale'
  protectionCoveragePct?: number
  avgPx: NumericValue
  last?: NumericValue
  upl: NumericValue
  uplRatio: NumericValue
  displayStop?: number | null
  takeProfitPx?: number | null
  cloud_oco_verified?: boolean
}

export interface PendingOrderItem {
  inst?: string
  side_raw?: 'buy' | 'sell'
  time?: string
  ordId: string
  instId: string
  name: string
  side: 'buy' | 'sell'
  posSide: 'long' | 'short'
  px: string
  sz: string
  state: string
  cTime: string
  tpTriggerPx?: string
  slTriggerPx?: string
}

export interface InstrumentFactor {
  instId: string
  name: string
  type: string
  price: number
  chg24h: number
  high24h?: number
  low24h?: number
  vol24h?: number
  rsi: number
  macd_hist: number
  trend_direction?: string
  action?: TradeAction
  confidence?: number
  adx_1h?: NumericValue
  calculus?: {
    velocity_1h?: number
    accel_1h?: number
    jerk_1h?: number
    impulse_1h?: number
    energy_1h?: number
    action_area_1h?: number
    state_1h?: string
  }
  smart_money?: {
    weighted_long_pct?: number
    net_flow_usdt?: string
    top_win_rate?: string
  }
  decision?: {
    action: TradeAction
    confidence: number
    leverage: number
    margin_usdt: number
    entry_price: number
    take_profit_price: number
    stop_loss_price: number
    risk_reward_ratio: string
    summary_reason: string
  }
  thought_process?: {
    market_structure?: string
    calculus_dynamics?: string
    math_prob_rationale?: string
    volume_and_oi?: string
    risk_reward_evaluation?: string
  }
  position?: PositionItem | null
}

export interface LLMRuntime {
  model: string
  provider_name: string
  reasoning_effort: string
  api_format: string
}

export interface DashboardResponse {
  timestamp: string
  is_stale?: boolean
  okx_environment?: 'demo' | 'live'
  data_health?: { status?: 'LIVE' | 'STALE' | 'PARTIAL' | 'OFFLINE'; partial?: boolean; errors?: string[] }
  account: AccountSummary
  positions_summary: {
    total_count: number
    long_count: number
    short_count: number
    items: PositionItem[]
  }
  pending_orders: PendingOrderItem[]
  factors: InstrumentFactor[]
  macro_assessment?: string
  llm_runtime?: LLMRuntime
  logs: string[]
  trades: any[]
  ai_brain_history?: AiBrainHistoryItem[]
  ai_last_prompt?: string
  today_stats?: any
  performance?: any
  news_intelligence?: any[]
  review?: any
  ai_trading_memory_md?: string
  factor_library?: any
}

export interface CouncilMemberResult {
  role_id?: string
  role_name?: string
  model_used?: string
  status?: string
  content?: string
  duration_ms?: number
  weight?: number
}

export interface AiBrainHistoryItem {
  time: string
  macro_assessment?: string
  ai_last_prompt?: string
  council_transcript?: {
    council_mode?: boolean
    total_duration_ms?: number
    advisors?: Record<string, CouncilMemberResult>
    arbitrator?: CouncilMemberResult
  } | null
  position_management?: Array<{
    instId: string
    action: 'HOLD' | 'CLOSE_MARKET' | 'UPDATE_SL'
    reason?: string
    reasoning?: string
  }>
}
