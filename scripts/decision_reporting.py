"""Pure per-cycle reporting. Environment notices are not trade execution actions."""

def clean(value, limit=100):
    return ' '.join(str(value or '').split())[:limit]


def summarize(cache, notices=None, *, unavailable_reason='', circuit_breaker=False):
    rows=[]
    for inst,row in (cache or {}).items():
        decision=row.get('decision') or {}
        action=decision.get('action','WAIT')
        status=decision.get('decision_status') or ('entry_candidate' if action in ('BUY_LONG','SELL_SHORT') else 'incomplete')
        if not decision.get('contract_valid') and status!='execution_rejected':status='incomplete'
        audit=decision.get('wait_audit') or {}
        rows.append({'instId':inst,'name':row.get('name',inst.split('-')[0]),'action':action,'status':status,
                     'reason':clean(decision.get('validation_reason') or decision.get('summary_reason'),240),
                     'long_blocker':clean((audit.get('long') or {}).get('reason'),160),
                     'short_blocker':clean((audit.get('short') or {}).get('reason'),160),
                     'previous_check':decision.get('previous_wait_review',{})})
    counts={key:sum(r['status']==key for r in rows) for key in ('audited_wait','incomplete','entry_candidate','execution_rejected')}
    return {'status':'circuit_breaker' if circuit_breaker else 'unavailable' if not rows else 'incomplete' if counts['incomplete'] else 'reviewed',
            'counts':counts,'evaluated_count':len(rows),'items':rows,'environment_notices':notices or [],
            'unavailable_reason':clean(unavailable_reason,240)}


def format_summary(summary):
    if not summary['items']:
        text='本轮决策不可用：'+(summary.get('unavailable_reason') or ('熔断暂停推理' if summary['status']=='circuit_breaker' else '未取得模型输出'))
    else:
        n=summary['counts']
        text=f"审查{summary['evaluated_count']}标的，候选{n['entry_candidate']}，等待审计通过{n['audited_wait']}，决策不完整{n['incomplete']}，风控拒绝{n['execution_rejected']}"
        for row in summary['items']:
            if row['status']=='audited_wait':
                detail=f"多：{clean(row['long_blocker'],55)}；空：{clean(row['short_blocker'],55)}"
                if row.get('previous_check',{}).get('required'):detail+='；已触发前轮条件复查'
                label='WAIT审计通过'
            else:
                label='决策不完整' if row['status']=='incomplete' else '候选被风控拒绝' if row['status']=='execution_rejected' else row['action']
                detail=clean(row['reason'],100)
            text+=f"；[{row['name']}] {label}（{detail}）"
    if summary.get('wait_alert'):
        text+=f"；诊断告警：连续{summary.get('no_entry_candidate_streak',0)}轮无开仓候选，不触发强制交易"
    notices=summary.get('environment_notices') or []
    if notices:text+=' | 环境限制: '+', '.join(clean(n,100) for n in notices)
    return text
