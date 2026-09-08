import copy
from contextlib import ExitStack
import importlib.util
import json
from pathlib import Path
import tempfile
import time
from types import SimpleNamespace
import unittest
from unittest.mock import patch
from scripts import profit_protection,execution_profiles,capital_pool,risk_policy,prompt_library,strategy_evidence,entry_gateway
from test_entry_candidates import package,selection
from scripts import trading_prompt

class ProfitProtectionTests(unittest.TestCase):
    def test_cost_adjusted_floor_activates_before_old_large_atr_gate(self):
        # Old 1.2*max(ATR,price*1.2%) rejected +1% price profit.
        plan=profit_protection.floor_plan('long',100,101,101,99,2)
        self.assertTrue(plan['active']);self.assertGreater(plan['stop'],100.3)
        self.assertLess(plan['stop'],101)
        self.assertTrue(profit_protection.allow_ai_tightening('long',100,101,100.5,2))
    def test_symmetry_and_peak_giveback(self):
        long=profit_protection.floor_plan('long',100,103,104,99,2)
        short=profit_protection.floor_plan('short',100,97,96,101,2)
        self.assertAlmostEqual(100-long['stop'],short['stop']-100)
        drop=profit_protection.floor_plan('long',100,100.6,104,99,2)
        self.assertTrue(drop['crossed'])
    def test_small_noise_and_crossed_or_loss_side_ai_stops_are_rejected(self):
        self.assertFalse(profit_protection.floor_plan('long',100,100.1,100.1,99,2)['active'])
        for stop in (99,100.1,101,102):self.assertFalse(profit_protection.allow_ai_tightening('long',100,101,stop,2))

class ExecutionPresetTests(unittest.TestCase):
    def setUp(self):
        self.stack=ExitStack();self.addCleanup(self.stack.close)
        self.root=Path(self.stack.enter_context(tempfile.TemporaryDirectory()))
        self.stack.enter_context(patch.object(prompt_library,'LIBRARY_FILE',self.root/'profiles.json'))
        self.stack.enter_context(patch.object(strategy_evidence,'DB_PATH',self.root/'evidence.db'))
        self.env=SimpleNamespace(mode='demo',identity='demo-test')
    def test_named_preset_is_visible_and_activation_changes_real_policy(self):
        self.assertIn('small300',[p['id'] for p in prompt_library.all_profiles()])
        before=execution_profiles.runtime()
        prompt_library.activate_profile('small300')
        current=execution_profiles.runtime();policy=risk_policy.load_policy()
        self.assertNotEqual(before['signature'],current['signature'])
        self.assertEqual(policy.single_asset_margin_usdt,30)
        self.assertEqual(policy.max_leverage,3)
        self.assertEqual(policy.per_trade_equity_pct,.005)
        self.assertEqual(current['execution']['equity_cap_usdt'],300)
        prompt_library.activate_profile('stable')
        self.assertEqual(execution_profiles.runtime()['signature'],before['signature'])
        self.assertEqual(risk_policy.load_policy().single_asset_margin_usdt,600)
    def test_signature_change_rejects_before_exchange_reads(self):
        before=execution_profiles.runtime()
        d={'action':'BUY_LONG','contract_valid':True,'contract_version':trading_prompt.VERSION,'valid_until':time.time()+100}
        identity=strategy_evidence.append(self.env.identity,'decision',{'instrument':'TEST-USDT-SWAP','decision':d,'execution_profile_signature':before['signature']})
        prompt_library.activate_profile('small300')
        env=__import__('scripts.okx_runtime',fromlist=['OKXEnvironment']).OKXEnvironment('demo','fake','fake','fake',account_scope=self.env.identity)
        with patch.object(entry_gateway,'_request',side_effect=AssertionError('no exchange read')) as read:
            with self.assertRaisesRegex(risk_policy.RiskRejected,'preset changed'):
                entry_gateway.prepare(env,inst_id='TEST-USDT-SWAP',side='long',entry=100,stop=99,take_profit=104,requested_size=1,budget=15,decision_id=identity,decision_at=time.time())
            read.assert_not_called()
    def allocate(self,equity,at,positions=(),orders=(),flow=0):
        policy=risk_policy.Policy(single_asset_margin_usdt=30,max_leverage=3)
        budget=capital_pool.Budget(False,5000,5000,policy,{},'sig')
        balance={'details':[{'ccy':'USDT','eq':str(equity)}]}
        obs={'equity':equity,'at':at,'external_flow_total':flow,'external_flow_origin':1000}
        return execution_profiles.cap_allocation(budget,execution_profiles.SMALL_300,list(positions),list(orders),{},'BTC-USDT-SWAP',lambda *_:3,env=self.env,observation=obs,balance=balance)
    def test_300u_nav_losses_survive_switches_and_deposits(self):
        first=self.allocate(5000,1000)
        self.assertEqual(first.equity,300);self.assertEqual(first.available,90)
        down=self.allocate(4997,1001)
        self.assertEqual(down.equity,297)
        deposit=self.allocate(5097,1002,flow=100)
        self.assertEqual(deposit.equity,297)
        with self.assertRaisesRegex(risk_policy.RiskRejected,'drawdown'):
            self.allocate(5088,1003,flow=100)
    def test_oversize_existing_positions_block_not_resize(self):
        held=[{'instId':'SUI-USDT-SWAP','pos':'10','imr':'100'}];original=copy.deepcopy(held)
        with self.assertRaisesRegex(risk_policy.RiskRejected,'margin budget'):self.allocate(5000,1000,positions=held)
        self.assertEqual(held,original)
    def test_actual_final_gateway_applies_selected_300u_profile(self):
        from scripts.okx_runtime import OKXEnvironment
        prompt_library.activate_profile('small300');binding=execution_profiles.runtime()
        env=OKXEnvironment('demo','fake','fake','fake',account_scope=self.env.identity)
        now=time.time();meta={'instId':'TEST-USDT-SWAP','ctType':'linear','settleCcy':'USDT','state':'live','ctVal':'1','ctMult':'1','lotSz':'.01','minSz':'.01','tickSz':'.01'}
        d={'action':'BUY_LONG','contract_valid':True,'contract_version':trading_prompt.VERSION,'valid_until':now+120}
        identity=strategy_evidence.append(env.identity,'decision',{'instrument':meta['instId'],'decision':d,'execution_profile_signature':binding['signature']})
        def private(method,path,params,environment):
            self.assertEqual(method,'GET')
            if path.endswith('/balance'):return [{'totalEq':'5000','uTime':str(int(now*1000)),'details':[{'ccy':'USDT','eq':'5000','availEq':'5000'}]}]
            if path.endswith('/leverage-info'):return [{'posSide':'long','lever':'3'}]
            return []
        def public(url,**kwargs):return {'data':[meta]} if '/instruments?' in url else {'data':[{'last':'100','ts':str(int(now*1000))}]}
        with patch.object(entry_gateway,'_request',side_effect=private),patch.object(entry_gateway.public_market,'get_json',side_effect=public):
            plan,client=entry_gateway.prepare(env,inst_id=meta['instId'],side='long',entry=100,stop=98,take_profit=110,requested_size=1000,budget=15,decision_id=identity,decision_at=now)
        self.assertLessEqual(plan['risk_usdt'],1.5)
        self.assertLessEqual(plan['margin_usdt'],30)
        self.assertEqual(plan['execution_profile']['execution']['id'],'small300')
        self.assertEqual(strategy_evidence.unresolved(env.identity)[0][0],client)

    def test_small_account_sizing_caps_risk_margin_and_actual_leverage(self):
        prompt_library.activate_profile('small300');allocation=self.allocate(5000,1000)
        meta={'instId':'TEST-USDT-SWAP','ctType':'linear','settleCcy':'USDT','state':'live','ctVal':'1','lotSz':'.01','minSz':'.01','tickSz':'.01'}
        args=dict(metadata=meta,side='long',entry=100,stop=98,take_profit=110,requested_size=1000,budget_usdt=15,equity=allocation.equity,available=allocation.available,policy=risk_policy.load_policy())
        plan=risk_policy.order_plan(leverage=3,**args)
        self.assertLessEqual(plan['risk_usdt'],1.5)
        self.assertLessEqual(plan['margin_usdt'],30)
        with self.assertRaisesRegex(risk_policy.RiskRejected,'leverage'):risk_policy.order_plan(leverage=5,**args)

class ConditionalAdxTests(unittest.TestCase):
    def test_only_reconstructed_valid_closed_candle_plan_can_pass_low_adx(self):
        path=Path(__file__).resolve().parents[1]/'plugins/interceptors/03_adx_volatility_filter.py'
        spec=importlib.util.spec_from_file_location('adx_requested_test',path);plugin=importlib.util.module_from_spec(spec);spec.loader.exec_module(plugin)
        from scripts.entry_candidates import catalog
        p=package();p['adx_1h']=16;draft=catalog(p)['plans'][0]
        valid=trading_prompt.candidate(p,selection(draft),trading_prompt.facts_for(p))
        self.assertTrue(plugin.check_risk(p,valid,{})[0])
        for change in ({'candidate_id':None},{'candidate_id':'fake'},{'contract_valid':False}):
            self.assertFalse(plugin.check_risk(p,{**valid,**change},{})[0])

class SharedPositionSnapshotTests(unittest.TestCase):
    def test_holding_views_use_the_identical_margin_pnl_roi_and_timestamp(self):
        from dashboard.app import project_live_holding_rows
        row={'instId':'SUI-USDT-SWAP','side':'long','status':'holding','environment_id':'demo','margin':199.8,'pnl':1.09,'roi_pct':.6}
        p={'instId':'SUI-USDT-SWAP','posSide':'long','margin_usdt':199.72,'upl':.8,'roi_pct':.4,'markPx':.813,'avgPx':.8119,'pos_sz':737}
        out=project_live_holding_rows([row], [p], 'demo','snapshot-A')[0]
        self.assertEqual((out['margin'],out['pnl'],out['roi_pct']),(199.72,.8,.4))
        self.assertEqual(out['valuation_at'],'snapshot-A')
        self.assertEqual(row['pnl'],1.09)
        closed={**row,'status':'closed'}
        self.assertEqual(project_live_holding_rows([closed],[p],'demo','A')[0],closed)
