'use strict';
(() => {
  let catalog=[], poll=null, requestId=null, signature='', connected=false;
  const selected=new Set();
  const el=id=>document.getElementById(id);
  const say=text=>{el('agentStatus').textContent=text;};
  function counts(){el('agentCount').textContent=selected.size+' / 100 tanlangan · '+(selected.size+(selected.size>1?1:0))+' ta AI so‘rovi';}
  function render(){
    const term=el('agentSearch').value.toLocaleLowerCase();
    el('agentCatalog').replaceChildren();
    for(const a of catalog.filter(a=>(a.name+' '+a.group).toLocaleLowerCase().includes(term))){
      const label=document.createElement('label');label.className='agentChoice';
      const input=document.createElement('input');input.type='checkbox';input.checked=selected.has(a.id);
      input.onchange=()=>{input.checked?selected.add(a.id):selected.delete(a.id);counts();};
      const name=document.createElement('span');name.textContent=a.name;
      const group=document.createElement('small');group.textContent=a.group;
      label.append(input,name,group);el('agentCatalog').append(label);
    }
    counts();
  }
  async function connect(){
    if(!token)return;
    try{const config=await api('/agents');if(!token)return;connected=true;catalog=config.agents;
      el('agentConfig').textContent=config.model+' · '+(config.configured&&config.enabled?'Ulangan, javob olishda API ruxsati tekshiriladi.':'Hali faollashtirilmagan.')+' Kunlik chegara: '+config.daily_call_limit+' ta so‘rov (UTC). Har javob: '+config.max_output_tokens+' tokengacha.';
      render();await refresh();
    }catch(e){say(e.message);}
  }
  async function refresh(){
    clearTimeout(poll);if(!token||!connected)return;
    try{const data=await api('/agent-runs');if(!token||!connected)return;
      el('agentRuns').replaceChildren();let active=false;
      for(const run of data.runs){
        const live=['QUEUED','RUNNING','CANCELLING'].includes(run.status);active=active||live;
        const card=document.createElement('article');card.className='job';
        const h=document.createElement('strong');h.textContent=run.status+' · '+run.results.length+'/'+run.agents.length+' mutaxassis';
        const task=document.createElement('p');task.textContent=run.prompt;
        const info=document.createElement('p');info.textContent=run.error||('Model: '+run.model+' · Kirish: '+run.usage.input_tokens+' / chiqish: '+run.usage.output_tokens+' token');
        card.append(h,task,info);
        if(run.answer){const answer=document.createElement('pre');answer.className='agentAnswer';answer.textContent=run.answer;card.append(answer);}
        for(const result of run.results){const details=document.createElement('details'),summary=document.createElement('summary'),body=document.createElement('pre');summary.textContent=result.name;body.className='agentAnswer';body.textContent=result.text;details.append(summary,body);card.append(details);}
        if(live){const cancel=document.createElement('button');cancel.type='button';cancel.textContent='Keyingi agentlarni to‘xtatish';cancel.disabled=run.status==='CANCELLING';cancel.onclick=async()=>{cancel.disabled=true;try{await api('/agent-runs/'+encodeURIComponent(run.id)+'/cancel',{});say('Boshlangan so‘rov tugaydi; keyingi agentlar ishga tushmaydi.');await refresh();}catch(e){say(e.message);cancel.disabled=false;}};card.append(cancel);}
        el('agentRuns').append(card);
      }
      if(active)poll=setTimeout(refresh,4000);
    }catch(e){say(e.message);}
  }
  el('agentSearch').oninput=render;
  el('agentClear').onclick=()=>{selected.clear();render();};
  el('agentRefresh').onclick=async()=>{await connect();};
  el('agentForm').onsubmit=async event=>{
    event.preventDefault();if(!token){say('Avval yuqorida studiyaga ulan.');return;}
    if(!selected.size){say('Kamida bitta agent tanla.');return;}
    const prompt=el('agentPrompt').value.trim();if(prompt.length<3){say('Vazifani yoz.');return;}
    const ids=Array.from(selected).sort();const sig=JSON.stringify({prompt,agents:ids});
    if(sig!==signature||!requestId){requestId=crypto.randomUUID();signature=sig;}
    const calls=ids.length+(ids.length>1?1:0);
    if(!confirm(calls+' ta pulli Astra so‘rovi. Vazifa OpenAI’ga yuboriladi. Boshlansinmi?'))return;
    el('agentStart').disabled=true;say('Vazifa yuborilmoqda…');
    try{const run=await api('/agent-runs',{id:requestId,prompt,agents:ids});say('Vazifa: '+run.status);await refresh();}
    catch(e){say(e.message+' Takror yuborish bir xil ish identifikatoridan foydalanadi.');}
    finally{el('agentStart').disabled=false;}
  };
  // Explicit new task releases the idempotency key; retries keep it.
  el('agentNew').onclick=()=>{requestId=null;signature='';el('agentPrompt').value='';say('Yangi vazifani yoz.');};
  window.addEventListener('begborim-connected',connect);
  window.addEventListener('begborim-disconnected',()=>{connected=false;clearTimeout(poll);el('agentRuns').replaceChildren();el('agentConfig').textContent='Studiyaga ulan.';say('Ulanish uzildi. Serverdagi ish o‘zi to‘xtamaydi.');});
})();
