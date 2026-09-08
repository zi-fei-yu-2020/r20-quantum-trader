const sourceLabels: Record<string, string> = {
  'ai_brain_decisions.json': 'AI 决策',
  'factor_library_snapshot.json': '因子快照',
  'news_sentiment.json': '新闻情绪',
  'trading_ledger.json': '交易账本',
}

/** Short labels retain the original filename in the table's title/accessible name. */
export function dataHealthSource(value: unknown): string {
  if (typeof value !== 'string' || !value.trim()) return '--'
  const basename = value.split(/[\\/]/).pop() || value
  return sourceLabels[basename] || basename
}
