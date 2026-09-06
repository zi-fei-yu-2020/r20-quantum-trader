import io
import json
from pathlib import Path
import sqlite3
import tempfile
import threading
import time
import unittest
from unittest.mock import patch
from types import SimpleNamespace
from scripts import risk_policy as risk, strategy_evidence as evidence, trade_lock, entry_gateway
from scripts.okx_runtime import OKXEnvironment
import ai_factor_trader as trader

META={'instId':'TEST-USDT-SWAP','ctType':'linear','settleCcy':'USDT','state':'live','ctVal':'1','ctMult':'1','lotSz':'0.1','minSz':'0.1','tickSz':'0.01'}

class StrategyRiskTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup)
        for module,name,value in [(evidence,'DB_PATH',Path(self.temp.name)/'evidence.db'),(trade_lock,'PATH',Path(self.temp.name)/'writer.lock')]:
            p=patch.object(module,name,value);p.start();self.addCleanup(p.stop)
        self.env=OKXEnvironment('demo','fake','fake','fake')

    def plan(self,**extra):
        params=dict(metadata=META,side='long',entry=100,stop=94,take_profit=125,requested_size=16,budget_usdt=15,equity=10000,available=5000,leverage=3)
        params.update(extra);return risk.order_plan(**params)

    def test_final_stop_budget_never_rounds_up_to_original_16_contracts(self):
        p=self.plan();self.assertLessEqual(p['risk_usdt'],15);self.assertLess(p['size'],3)
        self.assertAlmostEqual(round(p['size']/.1)*.1,p['size'])

    def test_too_small_budget_is_rejected_not_forced_to_one_lot(self):
        with self.assertRaises(risk.RiskRejected):self.plan(budget_usdt=.01)

    def test_short_geometry_and_actual_leverage_are_checked(self):
        self.assertLessEqual(self.plan(side='short',stop=106,take_profit=75)['risk_usdt'],15)
        for changes in [{'leverage':20},{'stop':101},{'entry':100.001},{'metadata':{**META,'lotSz':''}},{'requested_size':float('nan')},{'take_profit':112}]:
            with self.subTest(changes=changes),self.assertRaises(risk.RiskRejected):self.plan(**changes)

    def test_portfolio_margin_and_group_budget_include_reserved_risk(self):
        p=self.plan(portfolio={'total':199,'long':199,'group':199})
        self.assertLessEqual(p['risk_usdt'],1)
        with self.assertRaises(risk.RiskRejected):self.plan(existing_margin=600)
        with self.assertRaises(risk.RiskRejected):self.plan(portfolio={'total':200,'long':200,'group':200})

    def test_stop_is_strictly_monotonic_both_directions(self):
        self.assertFalse(risk.monotonic_stop('long',110,105,120))
        self.assertFalse(risk.monotonic_stop('short',90,95,80))
        self.assertFalse(risk.monotonic_stop('long',110,110,120))
        self.assertTrue(risk.monotonic_stop('long',110,112,120))
        self.assertTrue(risk.monotonic_stop('short',90,88,80))

    def test_stop_function_refuses_loosen_and_does_not_advance_on_unknown(self):
        position={'TEST-USDT-SWAP':{'posSide':'long','markPx':120,'avgPx':100}}
        old={'algoId':'a','instId':'TEST-USDT-SWAP','posSide':'long','state':'live','slTriggerPx':'110'}
        for proposed,last,expected_calls,expected_stop in [(105,old,0,110),(112,{**old,'slTriggerPx':'112'},1,112),(112,RuntimeError('unknown'),1,110)]:
            tracker={'TEST-USDT-SWAP_long':{'trailingStopPx':110}}
            payload={'timestamp':int(time.time()),'instructions':[{'instId':'TEST-USDT-SWAP','action':'UPDATE_SL','suggested_sl_price':proposed}]}
            with patch.object(trader.os.path,'exists',return_value=True),patch('builtins.open',return_value=io.StringIO(json.dumps(payload))),patch.object(trader.algo_reader,'read_algo_orders',side_effect=[[old],last if isinstance(last,Exception) else [last]]),patch.object(trader.market,'_selected',return_value=self.env),patch.object(trader,'okx_private_command',side_effect=lambda c:c),patch.object(trader,'run_cmd_result',return_value={'ok':False}) as write,patch.object(trader.strategy_evidence,'best_effort'):
                trader.execute_ai_position_management(position,tracker,'test',[])
            self.assertEqual(write.call_count,expected_calls);self.assertEqual(tracker['TEST-USDT-SWAP_long']['trailingStopPx'],expected_stop)

    def test_drawdown_uses_marked_equity_and_adjusts_external_flow(self):
        first=risk.update_equity_state(None,equity=1000,at=100000,cash_flow=0,complete=True)
        deposit=risk.update_equity_state(first,equity=1500,at=100001,cash_flow=500,complete=True)
        self.assertEqual(deposit['peak_drawdown'],0)
        loss=risk.update_equity_state(deposit,equity=1400,at=100002,cash_flow=0,complete=True)
        self.assertTrue(loss['blocked'])
        with self.assertRaises(risk.RiskRejected):risk.update_equity_state(first,equity=1000,at=100002,cash_flow=0,complete=False)

    def test_unknown_existing_or_pending_stop_blocks_exposure(self):
        position={'instId':META['instId'],'pos':'1','posSide':'long','markPx':'100'}
        with self.assertRaises(risk.RiskRejected):risk.exposure([position],[],[],{META['instId']:META})
        algo={'instId':META['instId'],'side':'sell','posSide':'long','sz':'1','slTriggerPx':'90'}
        x=risk.exposure([position],[],[algo],{META['instId']:META});self.assertGreater(x['total'],10)
        with self.assertRaises(risk.RiskRejected):risk.exposure([],[{'instId':META['instId'],'posSide':'long','sz':'1','px':'100'}],[],{META['instId']:META})

    def test_durable_intent_prevents_duplicate_decision_and_redacts_secrets(self):
        identity=evidence.begin_intent('demo','decision','TEST',{'instId':'TEST','api_key':'NEVERSTORE','size':1})
        with self.assertRaises(sqlite3.IntegrityError):evidence.begin_intent('demo','decision','TEST',{})
        self.assertEqual(len(evidence.unresolved('demo')),1)
        self.assertNotIn('NEVERSTORE',str(evidence.unresolved('demo')))
        evidence.finish_intent(identity,'filled');self.assertEqual(evidence.unresolved('demo'),[])

    def test_evidence_is_idempotent_but_rejects_mutated_same_identity(self):
        evidence.append('demo','fill',{'fee':1},'fill1');evidence.append('demo','fill',{'fee':1},'fill1')
        self.assertEqual(len(evidence.export_events('demo')),1)
        with self.assertRaises(ValueError):evidence.append('demo','fill',{'fee':2},'fill1')

    def test_writer_reentrant_and_released_only_during_inference(self):
        entered=threading.Event()
        def other():
            with trade_lock.writer(timeout=2):entered.set()
        with trade_lock.writer():
            with trade_lock.writer():pass
            thread=threading.Thread(target=other);thread.start()
            self.assertFalse(entered.wait(.05))
            with trade_lock.inference_window():self.assertTrue(entered.wait(1))
        thread.join(2);self.assertFalse(thread.is_alive())

    def test_uncertain_entry_is_reconciled_read_only_not_resent(self):
        evidence.begin_intent(self.env.identity,'d','TEST',{'instId':'TEST'})
        with patch.object(entry_gateway,'_request',side_effect=RuntimeError('not found')) as get:
            with self.assertRaises(risk.RiskRejected):entry_gateway.reconcile_intents(self.env)
        get.assert_called_once();self.assertEqual(get.call_args.args[0],'GET')

if __name__=='__main__':unittest.main()
