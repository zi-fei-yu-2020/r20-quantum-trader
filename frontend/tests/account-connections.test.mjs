import test from 'node:test'
import assert from 'node:assert/strict'
import { readFileSync } from 'node:fs'
import { canBind, connectionStateLabel, newsConnectionLabel, friendlyConnectionError } from '../src/utils/accountConnections.ts'
import { newsIsFresh, newsStatusText, newsTime } from '../src/utils/newsStatus.ts'

const connection={id:'fixture',label:'fixture',auth_type:'oauth',mode:'demo',site:'global',status:'identity_verified',capabilities:{demo:{account_uid:'A',read_ready:true},live:{account_uid:'A',read_ready:true,news_ready:true}}}
test('OAuth read success allows news only, not automatic trading',()=>{
 assert.equal(canBind(connection,'demo'),false)
 assert.equal(canBind(connection,'live'),false)
 assert.equal(canBind(connection,'news'),true)
 assert.equal(canBind({...connection,status:'authorization_pending'},'news'),false)
})
test('Key binding cannot cross account environments',()=>{
 const key={...connection,auth_type:'api_key'}
 assert.equal(canBind(key,'demo'),true)
 assert.equal(canBind(key,'live'),false)
})
test('news freshness requires successful source time, not a recent attempt',()=>{
 assert.equal(newsIsFresh({schema:2,connection_status:'fresh',last_success_at:1000},1100),true)
 assert.equal(newsIsFresh({schema:2,connection_status:'fresh',last_success_at:1000,last_attempt_at:3000},3000),false)
 assert.equal(newsIsFresh({schema:2,connection_status:'fresh',last_success_at:4000},3000),false)
 assert.equal(newsIsFresh({updated_at:'just now'},3000),false)
 assert.equal(newsTime(undefined),'--')
})
test('source failure is distinct from no market news',()=>{
 assert.ok(newsStatusText({schema:2,connection_status:'unavailable'}).includes('不表示市场没有新闻'))
 assert.equal(newsConnectionLabel('unconfigured'),'资讯连接未绑定')
 assert.equal(connectionStateLabel('unverified'),'待核验')
 assert.ok(friendlyConnectionError('oauth_account_changed').includes('已阻止'))
})
test('account center uses accessible component dialogs rather than browser alerts',()=>{
 const source=readFileSync(new URL('../src/views/admin/AccountsPage.vue',import.meta.url),'utf8')
 for(const token of ['AppDialog','AppField','grid-cols-1','items-start','type="password"','autocomplete="new-password"','clearSecrets']) assert.ok(source.includes(token))
 for(const token of ['window.alert','window.confirm','v-html','localStorage.setItem']) assert.ok(!source.includes(token))
})
test('news view does not invent mention counts or claim monitoring healthy on stale input',()=>{
 const source=readFileSync(new URL('../src/components/NewsIntelligence.vue',import.meta.url),'utf8')
 assert.ok(source.includes('<NewsConnectionStatus'))
 assert.ok(source.includes('资讯监测待恢复'))
 assert.ok(source.includes("s.mentions == null ? '--'"))
})
