"""Deterministic, symmetric profit protection; never widens an existing stop.

Engineering thresholds, not a calibrated return forecast. Costs are estimated;
exchange gaps/slippage can exceed them. Cloud confirmation remains separate.
"""
import math

def finite(value, default=0.):
    try: number=float(value)
    except (ValueError,TypeError):return default
    return number if math.isfinite(number) else default

def floor_plan(side, entry, current, peak, initial_stop, atr, *, taker_fee=.0005, slippage=.001):
    entry,current,peak,initial_stop,atr=[finite(v) for v in (entry,current,peak,initial_stop,atr)]
    if side not in ('long','short') or min(entry,current,peak)<=0:return {'active':False,'reason':'invalid_price'}
    sign=1 if side=='long' else -1
    gain=sign*(peak-entry)
    risk=sign*(entry-initial_stop) if initial_stop>0 else 0
    # A missing initial risk cannot invent a tiny R; use the configured movement floor.
    initial_risk=risk if risk>0 else max(atr,entry*.01)
    costs=entry*(2*taker_fee+2*slippage)
    activation=max(costs*1.5,min(initial_risk*.8,max(atr*1.5,entry*.006)))
    if gain<activation:return {'active':False,'reason':'profit_below_cost_adjusted_activation','activation':activation}
    distance=max(costs,gain*.45)
    if gain>=initial_risk:distance=max(distance,gain*.55)
    desired=entry+sign*distance
    buffer=max(entry*.001, min(atr*.25,entry*.003))
    # A violated floor requests local exit; never submit a stop through the market.
    crossed=sign*(current-desired)<=0
    if not crossed and sign*(current-desired)<buffer:
        desired=current-sign*buffer
    if sign*(desired-entry)<costs:return {'active':False,'reason':'insufficient_cost_buffer','activation':activation}
    return {'active':True,'stop':desired,'crossed':crossed,'activation':activation,
            'cost_buffer':costs,'market_buffer':buffer,'peak_gain':gain,'retained_gain':sign*(desired-entry)}

def allow_ai_tightening(side,entry,current,new_stop,atr,*,taker_fee=.0005,slippage=.001):
    entry,current,new_stop,atr=[finite(v) for v in (entry,current,new_stop,atr)]
    if side not in ('long','short') or min(entry,current,new_stop)<=0:return False
    sign=1 if side=='long' else -1
    costs=entry*(2*taker_fee+2*slippage)
    buffer=max(entry*.001,min(max(atr,0)*.25,entry*.003))
    return sign*(current-entry)>=costs*1.5 and sign*(new_stop-entry)>=costs and sign*(current-new_stop)>=buffer
