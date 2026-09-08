import test from 'node:test'
import assert from 'node:assert/strict'
import {readFileSync} from 'node:fs'
import {adminPages,pageTitle,publicPages} from '../src/config/navigation.ts'
import {readableLog} from '../src/utils/logText.ts'
const read=p=>readFileSync(new URL('../src/'+p,import.meta.url),'utf8')
test('document title is exactly the visible navigation/page title',()=>{
 for(const item of adminPages)assert.equal(pageTitle('/admin/'+item.id),item.label)
 for(const [path,title] of Object.entries(publicPages))assert.equal(pageTitle(path),title)
 assert.ok(read('router/index.ts').includes('document.title = pageTitle(to.path)'))
})
test('old corrupted logs are identified instead of invented or silently erased',()=>{
 assert.equal(readableLog('DOGE'+'?'.repeat(10)),'DOGE〔历史日志编码缺失〕')
 assert.equal(readableLog('为什么?'),'为什么?')
 assert.ok(read('components/LedgerLogs.vue').includes('readableLog(log)'))
})
test('all research disclosures are styled as explicit actions',()=>{
 for(const f of ['components/DecisionAuditPanel.vue','components/EvolutionReviewPanel.vue'])assert.ok(read(f).includes('action-disclosure'))
 assert.ok(read('style.css').includes('.action-disclosure > summary::after'))
})
test('short refresh failures are quiet, prolonged faults remain visible',()=>{
 const source=read('stores/dashboard.ts')
 assert.ok(source.includes('90000'))
 assert.ok(read('views/DashboardView.vue').includes('store.showConnectionNotice'))
 assert.ok(source.includes('degradedSince.value = null'))
})

test('refresh request is bounded and cannot permanently stall single-flight polling',()=>{
 const source=read('stores/dashboard.ts')
 assert.ok(source.includes('controller.abort(), 8000'))
 assert.ok(source.includes('clearTimeout(timeout)'))
})
