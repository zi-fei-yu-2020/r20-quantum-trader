"""Evidence-based exit attribution. PnL sign/size is never a source classifier."""
import math
import re

def number(value):
    try:n=float(value);return n if math.isfinite(n) else 0.
    except (TypeError,ValueError):return 0.

def reason(history,orders):
    inst=history.get('instId');direction=history.get('direction') or history.get('posSide')
    side='sell' if direction=='long' else 'buy' if direction=='short' else ''
    end=number(history.get('uTime'));matches={}
    for order in orders:
        if (order.get('instId')!=inst or order.get('state')!='filled' or order.get('side')!=side
            or order.get('posSide') not in {direction,'net'}):continue
        if abs(number(order.get('fillTime') or order.get('uTime'))-end)>5000:continue
        if order.get('ordId'):matches[str(order['ordId'])]=order
    result={'exit_reason':'平仓来源待核验','exit_source':'unknown','exit_evidence':'insufficient_order_evidence','close_order_ids':list(matches),'attribution_status':'unknown'}
    if not matches:return result
    types=[]
    for order in matches.values():
        client=str(order.get('clOrdId') or '')
        if re.fullmatch(r'r20close\d{10,13}',client):types.append('manual_admin')
        elif order.get('category') in {'full_liquidation','partial_liquidation','adl'}:types.append('exchange_risk')
        elif order.get('algoId'):types.append('exchange_algo')
        else:types.append('unknown')
    size=number(history.get('closeTotalPos'))
    matched=sum(number(o.get('accFillSz') or o.get('sz')) for o in matches.values())
    full=size>0 and abs(matched-size)<=max(1e-8,size*.001)
    labels={'manual_admin':'手动平仓（后台操作）','exchange_risk':'交易所强制结算','exchange_algo':'云端条件单触发平仓','unknown':'外部平仓（来源待核验）'}
    kind=types[0] if len(set(types))==1 else 'mixed'
    if not full:
        result.update(exit_reason='平仓来源待核验（末笔：'+labels.get(types[-1],'未知')+'）',exit_source='partial',attribution_status='partial')
    elif kind=='mixed':result.update(exit_reason='多来源平仓',exit_source='mixed',attribution_status='mixed')
    else:result.update(exit_reason=labels[kind],exit_source=kind,attribution_status='verified' if kind!='unknown' else 'unknown')
    result['exit_evidence']='matched_filled_orders'
    return result
