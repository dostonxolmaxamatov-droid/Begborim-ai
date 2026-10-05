const {test}=require('node:test');
const assert=require('node:assert/strict');
const fs=require('node:fs');
const vm=require('node:vm');
const path=require('node:path');
const source=fs.readFileSync(path.join(__dirname,'../server/web.js'),'utf8');
const block=source.slice(source.indexOf('const DEFAULT_SHIRIN_SERVER='),source.indexOf('async function addRefs('));
const token='test-access-code-not-a-real-secret-1234567890';
function context({failure=false}={}){
 const local=new Map(),session=new Map(),native=[];
 const S={settings:{base:'https://old.example',token:'old-value',remember:false},form:{engine:'browser'},connectAttempt:0,connected:false};
 const c=vm.createContext({URL,Error,TypeError,S,AI_VIDEO_KINDS:[],window:{ShirinNative:{saveSettings:s=>native.push(JSON.parse(s))}},location:{hostname:'appassets.androidplatform.net'},
  $:id=>({serverBase:{value:'https://stale.example'},serverToken:{value:'stale-value'},rememberToken:{checked:false}}[id]),
  render:()=>{},toast:()=>{},chooseVideoEngine:()=> 'browser',
  localStorage:{setItem:(k,v)=>local.set(k,v)},sessionStorage:{setItem:(k,v)=>session.set(k,v)},
  api:async()=>{if(failure)throw Error('Ulanish kodi noto‘g‘ri.');return {name:'Shirin AI',release:'0.1.0',models:{video:[{id:'montage'}]},higgsfield:{configured:false}};}});
 vm.runInContext(block,c);return {c,S,local,session,native};
}
const file=(changes={})=>JSON.stringify({format:'shirin-connection',version:1,server_url:'https://studio.example/',connection_code:token,...changes});
test('valid file imports its complete URL and code, not stale form fields, then persists only after health succeeds',async()=>{
 const {c,S,local,native}=context();
 await c.importConnectionFile({size:400,text:async()=>file()});
 assert.equal(S.settings.base,'https://studio.example');assert.equal(S.settings.token,token);
 assert.equal(S.connected,true);assert.equal(S.health.higgsfield.configured,false);
 assert.equal(JSON.parse(local.get('shirin-studio-settings')).remember,true);assert.equal(native[0].token,token);
});
test('bad JSON, oversized file, invalid format/version or missing token cannot alter an existing connection',async()=>{
 for(const raw of ['{','null','[]',file({version:2}),file({format:'shirin-project'}),file({connection_code:''}),file({connection_code:'abc\n'+token}),file({connection_code:'short'}),' '.repeat(65537)]){
  const {c,S,local}=context();const before=JSON.stringify(S);
  await assert.rejects(c.importConnectionFile({size:raw.length,text:async()=>raw}));
  assert.equal(JSON.stringify(S),before);assert.equal(local.size,0);
 }
});
test('HTTP, URL credentials, paths, queries, fragments and whitespace are rejected before any request',()=>{
 const {c}=context();
 for(const url of ['http://studio.example','https://user:pass@studio.example','https://studio.example/path','https://studio.example/?token=abc','https://studio.example/#secret','https://stu dio.example','https://stu\ndio.example'])assert.throws(()=>c.parseConnectionFile(file({server_url:url})));
});
test('failed authentication reports failure and never persists the rejected credentials',async()=>{
 const {c,S,local,session,native}=context({failure:true});
 await assert.rejects(c.importConnectionFile({size:400,text:async()=>file()}),/noto‘g‘ri/);
 assert.equal(S.connected,false);assert.equal(S.connecting,false);assert.equal(local.size,0);assert.equal(session.size,0);assert.equal(native.length,0);
});
test('previous private deployment file and UTF-8 BOM are accepted',()=>{
 const {c}=context();const old=JSON.stringify({git_commit:'source-commit',connection:{server_url:'https://studio.example',connection_code:token}});
 assert.equal(c.parseConnectionFile(old).token,token);assert.equal(c.parseConnectionFile('\uFEFF'+file()).base,'https://studio.example');
});
test('import cannot interrupt an active render or connection check',async()=>{
 for(const flag of ['busy','connecting']){const {c,S}=context();S[flag]=true;await assert.rejects(c.importConnectionFile({size:400,text:async()=>file()}));assert.equal(S.settings.base,'https://old.example');}
});
