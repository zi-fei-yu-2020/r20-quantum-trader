import test from 'node:test'
import assert from 'node:assert/strict'
import { readFileSync } from 'node:fs'
import * as Vue from 'vue'
import { renderToString } from 'vue/server-renderer'
import { parse, compileScript } from '@vue/compiler-sfc'
import ts from 'typescript'
import * as display from '../src/utils/entryPlanDisplay.ts'
import * as audit from '../src/utils/waitAudit.ts'

const checks=[
 {side:'long',setup:'pullback_reclaim',reason:'closed_candle_trigger_not_met'},
 {side:'long',setup:'closed_range_breakout',reason:'closed_candle_trigger_not_met'},
 {side:'short',setup:'closed_range_breakout',reason:'net_rr_below_policy',net_rr:.29},
]
const item={instId:'BTC-USDT-SWAP',action:'WAIT',status:'incomplete',reason:'WAIT审计不完整：声称盈亏比不足必须给出可计算方案',entry_plans:{plans:[],checks}}

test('duplicate reasons are grouped without deleting their individual checks or setups',()=>{
 const copy=structuredClone(checks),groups=display.groupedPlanChecks(checks)
 assert.equal(groups.length,2);assert.equal(groups[0].checks.length,2)
 assert.deepEqual(groups[0].setups,['pullback_reclaim','closed_range_breakout'])
 assert.deepEqual(groups[1].ratios,[.29]);assert.deepEqual(checks,copy)
})
test('different net RR observations remain available and missing is not converted to zero',()=>{
 const result=display.groupedPlanChecks([{...checks[2],net_rr:0},{...checks[2],net_rr:null},{...checks[2],net_rr:.29}])
 assert.deepEqual(result[0].ratios,[0,.29]);assert.equal(result[0].checks.length,3)
})
test('model audit failures are explicit and never presented as successful WAIT',()=>{
 assert.equal(display.decisionLabel(item),'审计未通过')
 assert.equal(display.incompleteReason(item),'声称盈亏比不足必须给出可计算方案')
 assert.equal(display.incompleteReason({...item,reason:undefined},'继续等待必须引用相对前轮变化的新证据'),'继续等待必须引用相对前轮变化的新证据')
 assert.equal(display.incompleteReason({...item,status:'audited_wait'}),'')
 assert.equal(display.decisionLabel({...item,status:'audited_wait'}),'等待 · 审计通过')
 assert.equal(display.decisionLabel({...item,status:'unknown'}),'等待 · 尚未审计')
})

const source=readFileSync(new URL('../src/components/DecisionAuditPanel.vue',import.meta.url),'utf8')
const {descriptor}=parse(source)
const script=compileScript(descriptor,{id:'entry-display',inlineTemplate:true})
const code=ts.transpileModule(script.content,{compilerOptions:{module:ts.ModuleKind.CommonJS,target:ts.ScriptTarget.ES2022}}).outputText
const exports={}
new Function('require','exports',code)(name=>{
 if(name==='vue')return Vue
 if(name.includes('entryPlanDisplay'))return display
 if(name.includes('waitAudit'))return audit
 if(name.endsWith('.vue'))return {__esModule:true,default:{setup:(_,{slots})=>()=>Vue.h('section',slots.default?.())}}
 throw Error(name)
},exports)

test('actual audit component separates validation reason from program trigger checks',async()=>{
 const html=await renderToString(Vue.createSSRApp(exports.default,{cycle:{items:[item],counts:{program_plans:0}},audit:{status:'ok',items:[]}}))
 assert.ok(html.includes('审计未通过：声称盈亏比不足必须给出可计算方案'))
 assert.ok(html.includes('本轮未生成程序草案'))
 assert.ok(html.includes('回踩回收、区间突破'))
 assert.ok(html.includes('净 R:R 0.29'))
 assert.ok(html.includes('逐项检查（3 项）'))
 assert.ok(!html.includes('最终 WAIT'))
 assert.ok(html.includes('data-plan-check-details'))
})
test('published memory disclosures have visible action styling and distinct content targets',()=>{
 const memory=readFileSync(new URL('../src/components/PublishedMemoryPanel.vue',import.meta.url),'utf8')
 assert.equal((memory.match(/class="action-disclosure text-xs min-w-0"/g)||[]).length,2)
 for(const value of ['data-memory-disclosure="legacy"','data-memory-disclosure="effective"','点击展开历史兼容内容','核对实际输入原文'])assert.ok(memory.includes(value))
 const css=readFileSync(new URL('../src/style.css',import.meta.url),'utf8')
 assert.ok(css.includes('.action-disclosure[open] > summary::after'))
 assert.ok(css.includes('.action-disclosure > summary:focus-visible'))
 assert.ok(!memory.includes('v-html'))
})
