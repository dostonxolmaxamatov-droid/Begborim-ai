'use strict';
const $=id=>document.getElementById(id), esc=v=>String(v??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const PATHS={home:'M3 10 12 3l9 7v11h-6v-7H9v7H3z',chat:'M4 4h16v12H9l-5 4z M8 8h8 M8 12h5',image:'M3 3h18v18H3z M3 17l6-7 5 5 3-3 4 5 M16 7h.01',video:'M3 5h13v14H3z M16 10l5-3v10l-5-3 M7 2l3 3 M12 2l3 3',voice:'M9 4a3 3 0 0 1 6 0v8a3 3 0 0 1-6 0z M5 10v2a7 7 0 0 0 14 0v-2 M12 19v3 M8 22h8',edit:'m14 5 5 5 M4 16l12-12 4 4L8 20H4z M13 21h8',gallery:'M3 7h14v14H3z M7 3h14v14 M6 17l3-4 3 2 2-2',templates:'M3 3h7v7H3z M14 3h7v7h-7z M3 14h7v7H3z M14 14h7v7h-7z',settings:'M12 3v3 M12 18v3 M3 12h3 M18 12h3 M6 6l2 2 M16 16l2 2 M6 18l2-2 M16 8l2-2 M16 12a4 4 0 1 1-8 0 4 4 0 0 1 8 0',upload:'M12 16V3 M7 8l5-5 5 5 M3 15v6h18v-6',arrow:'M4 12h16 M14 6l6 6-6 6',spark:'m12 2 3 7 7 3-7 3-3 7-3-7-7-3 7-3z'};
const icon=n=>`<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="${PATHS[n]||PATHS.spark}"/></svg>`;
const NAV=[['home','Bosh sahifa'],['chat','Chat'],['image','Rasm'],['video','Video'],['voice','Ovoz'],['edit','Tahrir'],['gallery','Galereya'],['templates','Shablonlar'],['settings','Sozlamalar']];
const TEMPLATES=[
 {name:'Mini Farm · Loydan qutqarish',emoji:'🚜',desc:'Do‘stlar yordami bilan yo‘l yana ochiladi.',prompt:'Exactly 15 seconds, vertical 9:16. Original child-friendly polished 3D animation. A blue grain truck is stuck in shallow mud. A cheerful red mini tractor and yellow tracked excavator help it out. A green combine waits nearby. A boy and puppy watch safely behind a fence. Vehicle eyes on windshield and mouth on front. Keep colors and designs consistent. Clear safe actions and a happy ending. No third-party logos or text.'},
 {name:'Intizor · Sehrli eshik',emoji:'🚪',desc:'Bog‘dagi kichik eshik ortida nima bor?',prompt:'Exactly 15 seconds, vertical 9:16. Intizor is the only main human character. Keep her reference face, hair, bow, outfit, jewelry, skin tone and proportions unchanged. In a sunny safe garden, a tiny glowing rainbow door appears in a wall. She follows a thin ribbon of light and gently opens the door to discover a miniature flower garden. Warm, playful 3D animation, no tattoos, no new main characters.'},
 {name:'Mini Farm · Qovoq savati',emoji:'🎃',desc:'Dumalagan qovoq yumshoq poxolga tushadi.',prompt:'15-second vertical 9:16 original 3D cartoon. A pumpkin rolls slowly across a mini farm path. A yellow tracked excavator places a soft straw cushion. A red mini tractor nudges a basket into position. The pumpkin lands safely. A green combine and blue grain truck smile. Boy and puppy remain behind a fence. Consistent character design, no dangerous actions, no logos.'},
 {name:'Intizor · Uchgan shlyapa',emoji:'👒',desc:'Yengil shamol kichik sarguzasht boshlaydi.',prompt:'Exactly 15 seconds, 9:16. Intizor alone as the main human character in a bright flower park. Preserve the uploaded character reference exactly. A gentle breeze lifts her straw hat off a bench, carries it above a fountain and drops it into low flowers. Intizor walks along the safe path, retrieves the hat and smiles. No change to face, outfit, hair or accessories; no tattoos.'},
 {name:'Muhammad & Umar · Bayram',emoji:'🎉',desc:'Uy, bog‘ va tantanali yakun.',prompt:'Exactly 15 seconds, 9:16. Original child-friendly 3D animation with Muhammad and Umar. Preserve their uploaded character references. Begin with a happy celebration at home, continue with safe outdoor garden fun, and end at an elegant festive table. They celebrate together with a warm joyful expression. Consistent faces, clothing and proportions. No third-party logos.'},
 {name:'Intizor · Pushti shar',emoji:'🎈',desc:'Gul yo‘lagida yo‘qolgan shar topiladi.',prompt:'Exactly 15 seconds, vertical 9:16. Intizor is the only main human character. Preserve all uploaded reference details without redesign. On a safe garden promenade, a pink balloon floats away. Its ribbon catches on a low decorative arch. Intizor follows the path, gently retrieves the ribbon and returns smiling. Soft wind and warm sunlight, no tattoos.'},
 {name:'Mini Farm · Olmalar',emoji:'🍎',desc:'Ranglar bo‘yicha saralash o‘yini.',prompt:'Exactly 15 seconds, vertical 9:16. Red mini tractor, green combine, blue grain truck and yellow tracked excavator with original friendly faces sort red, green and yellow apples into matching baskets on a sunny mini farm. Clear simple actions, consistent designs and colors. Boy and puppy stay safely behind a fence. Polished 3D cartoon, no logos.'},
 {name:'Sokin tabiat',emoji:'🌿',desc:'Yumshoq yorug‘lik va tinch kamera.',prompt:'Vertical 9:16 cinematic scene, 15 seconds. A peaceful green garden in warm morning light. A gentle breeze moves flower petals. Slow smooth camera movement, delicate natural detail, calm atmosphere, no text, no logos.'}
];
const STYLES=[['','Asl uslub'],['Colorful original 3D cartoon, soft lighting.','3D multfilm'],['Cinematic photorealistic lighting and natural materials.','Kinematik'],['Japanese anime-inspired illustration, expressive line art.','Anime'],['Soft watercolor illustration with pastel colors.','Akvarel'],['Detailed miniature diorama, macro photography look.','Miniatyura']];
const CAMERAS=[['','Avtomatik'],['Slow cinematic dolly in.','Yaqinlashish'],['Slow cinematic dolly out.','Uzoqlashish'],['Smooth lateral tracking shot.','Yonma-yon kuzatish'],['Slow camera orbit around the subject.','Atrofidan aylanish'],['Overhead camera view.','Yuqoridan'],['Locked-off static camera.','Harakatsiz']];
const EFFECTS=[['','Effektsiz'],['Subtle magical sparkling particles.','Sehrli uchqunlar'],['A few petals drift gently through the scene.','Gul yaproqlari'],['Soft volumetric sunlight rays.','Yorug‘lik nurlari']];
function composePrompt(text,video=true){return [text,video?S.form.camera:'',S.form.style,S.form.effect,S.form.consistent?'Preserve reference faces, outfits, colors and proportions. Do not add new characters.':''].filter(Boolean).join('\n');}
function promptControls(video=true){return `<div class="form-grid">${video?select('camera','Kamera rakursi',CAMERAS):''}${select('style','AI uslubi',STYLES)}${select('effect','Effekt tavsifi',EFFECTS)}</div><label class="check"><input type="checkbox" data-prop="consistent" ${S.form.consistent?'checked':''}> Reference qahramon ko‘rinishini saqlashni so‘rash</label>`;}
const S={page:'home',db:null,refs:[],audio:null,video:null,artifacts:[],chat:[],health:null,connected:false,connecting:false,connectionError:'',videoError:'',connectAttempt:0,settings:{base:'',token:'',remember:false},form:{prompt:'',imagePrompt:'',ratio:'9:16',quality:'720',duration:15,fps:30,motion:'zoom',caption:'',engine:'auto_ai',imageEngine:'editor',imageRatio:'1:1',imageQuality:'1024',imageFormat:'png',brightness:100,contrast:100,saturation:100,rotation:0,removeBackground:false,keyColor:'#ffffff',tolerance:35,voiceText:'',voiceLanguage:'uz-UZ',voiceRate:1,trimStart:0,filter:'none',chatModel:'auto',camera:'',style:'',effect:'',consistent:true,cropBottom:0,autoText:false,videoLanguage:'none',paid:false},busy:false,cancel:false,filter:'all',search:'',urls:[],chatBusy:false,recorder:null,mediaStream:null,recordChunks:[]};
let toastTimer;
function toast(text){$('toast').textContent=text;$('toast').classList.add('show');clearTimeout(toastTimer);toastTimer=setTimeout(()=>$('toast').classList.remove('show'),6000);}
function id(){return crypto.randomUUID?crypto.randomUUID():Array.from(crypto.getRandomValues(new Uint8Array(16)),n=>n.toString(16).padStart(2,'0')).join('');}
function openDB(){return new Promise((resolve,reject)=>{const req=indexedDB.open('shirin-studio',1);req.onupgradeneeded=()=>{req.result.createObjectStore('assets',{keyPath:'id'});req.result.createObjectStore('meta');};req.onsuccess=()=>resolve(req.result);req.onerror=()=>reject(req.error);});}
function dbPut(store,value,key){return new Promise((resolve,reject)=>{const tx=S.db.transaction(store,'readwrite');key===undefined?tx.objectStore(store).put(value):tx.objectStore(store).put(value,key);tx.oncomplete=resolve;tx.onerror=()=>reject(tx.error);});}
function dbGet(store,key){return new Promise((resolve,reject)=>{const r=S.db.transaction(store).objectStore(store).get(key);r.onsuccess=()=>resolve(r.result);r.onerror=()=>reject(r.error);});}
function dbAll(){return new Promise((resolve,reject)=>{const r=S.db.transaction('assets').objectStore('assets').getAll();r.onsuccess=()=>resolve(r.result.sort((a,b)=>b.created-a.created));r.onerror=()=>reject(r.error);});}
function dbDelete(key){return new Promise((resolve,reject)=>{const tx=S.db.transaction('assets','readwrite');tx.objectStore('assets').delete(key);tx.oncomplete=resolve;tx.onerror=()=>reject(tx.error);});}
function draft(){return dbPut('meta',{refs:S.refs,audio:S.audio,video:S.video,form:S.form},'draft').catch(()=>toast('Qoralama saqlanmadi: qurilma xotirasini tekshir.'));}
function fileData(blob){return new Promise((resolve,reject)=>{const r=new FileReader();r.onload=()=>resolve(r.result);r.onerror=()=>reject(r.error);r.readAsDataURL(blob);});}
function blobFromData(url){const [header,b]=url.split(',');const bytes=Uint8Array.from(atob(b),c=>c.charCodeAt(0));return new Blob([bytes],{type:header.slice(5).split(';')[0]});}
function blobURL(blob){const u=URL.createObjectURL(blob);S.urls.push(u);return u;}
function dimensions(ratio,quality){const [a,b]=ratio.split(':').map(Number),s=Number(quality)||720;return [Math.round(a*s/Math.min(a,b)/2)*2,Math.round(b*s/Math.min(a,b)/2)*2];}
function head(title,sub,tag=''){return `<div class="page-head"><div><h1>${title}</h1><p>${sub}</p></div>${tag?`<span class="tag green">${tag}</span>`:''}</div>`;}
function options(rows,value){return rows.map(r=>{const [v,l,disabled]=Array.isArray(r)?r:[r,r];return `<option value="${esc(v)}" ${String(v)===String(value)?'selected':''} ${disabled?'disabled':''}>${esc(l)}</option>`;}).join('');}
function select(prop,label,rows){return `<label>${label}<select data-prop="${prop}">${options(rows,S.form[prop])}</select></label>`;}
function num(prop,label,min,max,step=1){return `<label>${label}<input type="number" data-prop="${prop}" min="${min}" ${max?'max="'+max+'"':''} step="${step}" value="${esc(S.form[prop])}"></label>`;}
function textArea(prop,label,placeholder=''){return `<label for="f-${prop}">${label}</label><textarea id="f-${prop}" data-prop="${prop}" placeholder="${placeholder}">${esc(S.form[prop])}</textarea>`;}
function upload(type,label,description,multiple=false){return `<label class="upload-zone">${icon('upload')}<strong>${label}</strong><small>${description}</small><input type="file" data-upload="${type}" ${multiple?'multiple':''} accept="${type==='refs'?'image/jpeg,image/png,image/webp':type==='srt'?'.srt':type+'/*'}"></label>`;}
function refs(){return `<div class="previews">${S.refs.map((r,i)=>`<div class="reference"><img src="${esc(r.thumb)}" alt="Sahna ${i+1}"><b>${i+1}</b><div><button data-ref="${i}" data-dir="-1" aria-label="Oldinga">←</button><button data-ref="${i}" data-dir="1" aria-label="Keyinga">→</button><button data-ref="${i}" data-dir="0" aria-label="Rasmni olib tashlash">×</button></div></div>`).join('')}</div>${S.refs.length?`<div class="hint">${S.refs.length} ta rasm · tartib chapdan o‘ngga</div>`:''}`;}
function paidControl(){return `<label class="check"><input type="checkbox" data-prop="paid" ${S.form.paid?'checked':''}> Pullik AI so‘rovlariga ruxsat beraman — xizmat o‘z tarifi bo‘yicha hisoblaydi.</label>`;}
function preview(){const ai=!['browser','montage'].includes(S.form.engine)&&S.page!=='edit';return `<aside class="panel"><div class="section-head"><h3>Video uchun rasm</h3><span class="tag">${esc(S.form.ratio)}</span></div><div class="preview-stage">${S.refs[0]?`<canvas id="videoReferenceCanvas" aria-label="Video uchun kesilgan rasm"></canvas>`:`<div class="preview-empty">${icon('video')}Telefon galereyasidan<br>rasmlarni tanla.</div>`}</div><p class="hint">${Number(S.form.cropBottom)>0&&ai?'Pastdagi '+Number(S.form.cropBottom)+'% kesiladi. Qahramon to‘liq qolganini tekshir.':'Manba rasm oldindan ko‘rinishi.'}</p><div class="note">${ai?'AI tanlangan rasmdagi qahramon, yuz ifodasi va muhitni tavsif asosida jonlantiradi. Natija tanlangan modelga bog‘liq.':'Montaj rasmlarni ketma-ket joylaydi va kamera effekti qo‘shadi.'}</div><button class="secondary full" data-page="gallery">${icon('gallery')} Galereyani ochish</button></aside>`;}
function nav(){ $('navigation').innerHTML='<p class="nav-label">IJOD MAYDONI</p>'+NAV.map(([n,l])=>`<button class="nav-button ${S.page===n?'active':''}" data-page="${n}">${icon(n)}<span>${n==='home'?'Bosh':l}</span></button>`).join('')+`<button class="nav-button mobile-more" data-action="more-tools">${icon('templates')}<span>Yana</span></button>`+'<div class="sidebar-foot"><strong>O‘zing yarat. O‘zing saqla.</strong>Galereya · rasm · video<br>STUDIO / 0.1.0</div>'; }
function home(){return `${head('Salom, ijodkor ✦','Bugun qaysi g‘oyangga hayot beramiz?')}<section class="hero"><div class="hero-copy"><div class="eyebrow">SHIRIN AI / IJOD SEN BILAN BOSHLANADI</div><h1>G‘oyangni<br><em>harakatga keltir.</em></h1><p>Rasmlar, ovoz va hikoyalar. Ijod uchun kerakli vositalar — bitta studiyada.</p><button class="primary" data-page="video">Video yaratishni boshlash ${icon('arrow')}</button></div><div class="hero-art" aria-hidden="true"><div class="orbit"></div><div class="orbit two"></div><div class="orb">${icon('video')}</div><span class="spark">✦</span></div></section><div class="section-head"><h2>Nima yaratamiz?</h2><small>Sening ijod maydoning</small></div><section class="tool-grid">${[['chat','AI Chat','G‘oya va suhbat'],['image','Rasm','Yaratish va tahrir'],['video','Video','Rasmdan hikoyaga'],['voice','Ovoz','Matndan ovozga'],['edit','Tahrirlash','Musiqa va subtitr'],['gallery','Galereya','Barcha ishlaring']].map(([n,t,d])=>`<button class="tool-card" data-page="${n}"><span class="tool-icon">${icon(n)}</span><strong>${t}</strong><small>${d}</small></button>`).join('')}</section><div class="section-head"><h2>Studiyang tayyor</h2><button class="text-button" data-page="settings">Ulanishlarni ko‘rish ↗</button></div><div class="bottom-grid"><section class="panel">${[['video','Bepul video montaj','Rasmlar, kamera harakati, musiqa, subtitr'],['image','Mahalliy rasm tahriri','Nisbat, ranglar va bir rangli fon'],['gallery','Shaxsiy galereya','Ishlaring qurilmangda saqlanadi']].map(([n,t,d])=>`<div class="feature-row"><span class="tool-icon">${icon(n)}</span><div><strong>${t}</strong><p>${d}</p></div><span class="tag green">Tayyor</span></div>`).join('')}</section><section class="panel"><div class="section-head"><h3>G‘oyadan boshlang</h3><span class="tag purple">15 soniya</span></div><div class="template-mini"><span class="emoji">🚜</span><div><h3>Mini Farm sarguzashti</h3><p>Kichkina qahramonlar.<br>Katta do‘stlik.</p><button class="text-button" data-template="0">Shablonni ochish →</button></div></div></section></div><footer><span>SHIRIN AI · Sening shaxsiy studiyang</span><span>Mahalliy vositalar • obunasiz</span></footer>`;}
function aiVideoOptions(){if(S.form.engine!=='fal_video')return promptControls();return promptControls()+`<label class="check"><input type="checkbox" data-prop="autoText" ${S.form.autoText?'checked':''} ${S.health?.models?.vision?'':'disabled'}> Rasmdagi sahna matnini o‘qish${S.health?.models?.vision?'':' · Gemini ulanmagan'}</label>${select('videoLanguage','Hikoyachi ovozi',[['none','Ovozsiz'],['uz','O‘zbekcha',!S.health?.models?.narration||!S.health?.models?.vision],['en','English',!S.health?.models?.narration||!S.health?.models?.vision]])}<p class="hint">AI, matn o‘qish va ovoz xizmatlari alohida tariflanadi. Hikoyachi yoki yuklangan audiodan birini tanla.</p>`;}

function imageSources(){return `<div class="image-sources">${upload('refs','Telefon galereyasi','Bir yo‘la bir nechta rasm tanla',true)}<div class="actions"><button class="secondary" data-action="choose-saved-images">${icon('gallery')} Saqlangan rasmlar</button><label class="file-button">Fayllardan<input type="file" data-upload="refs" data-picker="files" accept="image/jpeg,image/png,image/webp" multiple></label></div></div>`;}
function sceneOptions(){return `<details class="scene-settings"><summary>Har bir sahna va storyboard yozuvlari</summary><label class="mt">Pastdagi matn panelini kesish<select data-prop="cropBottom">${options([[0,'Kesilmasin'],[15,'Pastki 15%'],[20,'Pastki 20%'],[25,'Pastki 25%'],[30,'Pastki 30%'],[35,'Pastki 35%'],[40,'Pastki 40%']],S.form.cropBottom)}</select></label><p class="hint">Kesilgan ko‘rinishni yonida tekshir. Asl rasm saqlanadi. Rasmdagi sahna matnini o‘qish yoqilsa, AI matnni asl nusxadan o‘qiydi.</p>${S.refs.map((r,i)=>`<label class="scene-prompt">Sahna ${i+1} · ${esc(r.name)}<textarea data-scene-id="${r.id}" placeholder="Bu rasmda nima harakat bo‘lsin? Bo‘sh qolsa umumiy tavsif ishlatiladi.">${esc(r.scenePrompt||'')}</textarea></label>`).join('')}</details>`;}
const AI_VIDEO_KINDS=['fal_video','comfy_video'];
const AI_JOB_KINDS=['hf_video',...AI_VIDEO_KINDS,'image_video','text_video'];
function chooseVideoEngine(){const rows=S.connected?(S.health?.models?.video||[]).filter(m=>AI_VIDEO_KINDS.includes(m.id)&&m.ready):[];return (rows.find(m=>!m.paid)||rows[0])?.id||'auto_ai';}
function videoConnectionState(){
 if(S.connecting)return {code:'checking',title:'AI ulanishi tekshirilmoqda…',message:'Server javobi kutilmoqda. Tekshiruv 15 soniyagacha davom etadi.'};
 if(!S.connected)return {code:'offline',title:'AI serveriga ulanish kerak',message:S.connectionError||'Sozlamalarda server manzili va ulanish kodini kirit. Rasmlaring va tavsifing qoralamada saqlanadi.'};
 const rows=S.health?.models?.video||[],ready=rows.filter(m=>AI_VIDEO_KINDS.includes(m.id)&&m.ready);
 if(ready.length)return {code:'configured',title:'AI ulanishi topildi',message:'Model konfiguratsiyasi mavjud. Hisob balansi va xizmat javobi video yaratilayotganda tekshiriladi.'};
 if(S.health?.video_provider==='openai'||rows.some(m=>/sora|openai/i.test(m.id)))return {code:'legacy',title:'Serverdagi video xizmatini yangilash kerak',message:'Serverda eski video ulanishi ishlayapti. Jonlantirish uchun server yangilanishi va ishlaydigan Kling yoki ComfyUI ulanishi kerak.'};
 return {code:'missing',title:'Jonlantiruvchi AI hali sozlanmagan',message:'Serverga ulanish bor. Endi Kling hisobi yoki mahalliy ComfyUI video modeli sozlanishi kerak.'};
}
function videoConnectionNotice(){const state=videoConnectionState();return `<section class="connection-note" data-connection-state="${state.code}"><strong>${state.title}</strong><p>${esc(state.message)}</p><div class="actions"><button class="secondary" data-action="connect" ${S.connecting?'disabled':''}>${S.connecting?'Tekshirilmoqda…':'Qayta tekshirish'}</button><button class="secondary" data-page="settings">Ulanish sozlamalari →</button></div></section>`;}
function videoActions(ai,ready,edit,model){
 const error=ai&&S.videoError?`<div class="connection-note" role="alert"><strong>Jonlantirish tugamadi</strong><p>${esc(S.videoError)}</p><p>Rasmlar va tavsif saqlandi.</p></div>`:'';
 if(ai&&!ready){
  const state=videoConnectionState();
  return `<section id="videoActions" class="video-actions" data-video-state="${state.code}"><div id="videoActionStatus" role="status" aria-live="polite"><strong>${esc(state.title)}</strong><p>${esc(state.message)}</p></div>${error}<button class="primary full mt" data-action="video-setup">${icon('settings')} AI ulanishini sozlash</button>${S.settings.base?`<button class="secondary full mt" data-action="connect" ${S.connecting?'disabled':''}>${S.connecting?'Tekshirilmoqda…':'Ulanishni qayta tekshirish'}</button>`:''}</section>`;
 }
 return `<section id="videoActions" class="video-actions" data-video-state="${ai?'configured':'montage'}">${error}${ai&&model?.paid?paidControl():''}<button class="primary full" data-action="render-video" data-edit="${edit}" ${S.busy?'disabled':''}>${icon('video')} ${ai?'AI bilan jonlantirish':'Montajni tayyorlash'}</button></section>`;
}
function videoSetupDetails(){
 const state=videoConnectionState(),missing=S.health?.video_status?.missing_by_provider;
 const lines=[['fal_video','Kling',['FAL_KEY']],['comfy_video','ComfyUI',['COMFYUI_URL','COMFYUI_VIDEO_WORKFLOW']]].map(([kind,name,keys])=>{
  const model=S.health?.models?.video?.find(m=>m.id===kind),absent=missing?.[kind]?.filter(k=>keys.includes(k))||keys;
  return `<p><strong>${name}:</strong> ${model?.ready?'Konfiguratsiya mavjud':absent.length?'Serverda '+absent.map(k=>`<code>${k}</code>`).join(', ')+' kerak.':'Konfiguratsiyani tekshir.'}</p>`;
 }).join('');
 return `<section class="note amber" data-connection-state="${state.code}"><strong>${state.title}</strong><p>${esc(state.message)}</p>${S.connected&&state.code!=='configured'?`<details><summary>Serverni sozlash ma’lumoti</summary>${lines}<p>Provayder kalitlari serverda saqlanadi. Ulanish kodi maydoniga API kalitini yozma.</p></details>`:''}</section>`;
}
function closeSheet(){const d=$('assetSheet');if(d){if(d.close)d.close();d.remove();}for(const u of S.sheetUrls||[])URL.revokeObjectURL(u);S.sheetUrls=[];}
function sheet(title,body){closeSheet();const d=document.createElement('dialog');d.id='assetSheet';d.className='asset-sheet';d.innerHTML=`<div class="section-head"><h2>${title}</h2><button data-action="close-sheet" aria-label="Yopish">×</button></div>${body}`;document.body.append(d);if(d.showModal)d.showModal();else d.setAttribute('open','');d.addEventListener('cancel',closeSheet);}
function showSavedImages(){const rows=S.artifacts.filter(a=>a.type.startsWith('image/'));const urls=[];const body=rows.length?`<div class="asset-picks">${rows.map(a=>{const u=URL.createObjectURL(a.blob);urls.push(u);return `<label><input type="checkbox" data-pick-asset="${a.id}"><img src="${u}" alt="${esc(a.name)}"><span>${esc(a.name)}</span></label>`;}).join('')}</div><button class="primary full mt" data-action="use-selected-images">Tanlangan rasmlarni qo‘shish</button>`:`<p class="muted">Hozircha galereyada saqlangan rasm yo‘q. Galereya bo‘limida telefondan rasm qo‘shishing mumkin.</p><button class="primary full mt" data-page="gallery">Galereyaga o‘tish</button>`;sheet('Saqlangan rasmlar',body);S.sheetUrls=urls;}
async function croppedReference(ref,percent){const crop=Number(percent)||0;if(crop<0||crop>40)throw Error('Kesish qiymati noto‘g‘ri.');if(!crop)return ref.blob;const bitmap=await createImageBitmap(ref.blob);try{const c=document.createElement('canvas');c.width=bitmap.width;c.height=Math.max(2,Math.round(bitmap.height*(1-crop/100)));c.getContext('2d').drawImage(bitmap,0,0);const blob=await new Promise(r=>c.toBlob(r,'image/png'));if(!blob)throw Error('Rasmni kesib bo‘lmadi.');return blob;}finally{bitmap.close();}}
async function drawVideoReference(){const c=$('videoReferenceCanvas');if(!c||!S.refs[0])return;const ai=!['browser','montage'].includes(S.form.engine)&&S.page!=='edit';const blob=await croppedReference(S.refs[0],ai?S.form.cropBottom:0),bitmap=await createImageBitmap(blob);if(!c.isConnected){bitmap.close();return;}c.width=bitmap.width;c.height=bitmap.height;c.getContext('2d').drawImage(bitmap,0,0);bitmap.close();}
function videoPage(edit=false){
 const ai=!edit&&!['browser','montage'].includes(S.form.engine),models=S.health?.models?.video||[],available=models.filter(m=>AI_VIDEO_KINDS.includes(m.id));
 const rows=ai?[['auto_ai','AI modelni tanla',available.some(m=>m.ready)],...available.map(m=>[m.id,m.name+(m.paid?' · pullik':' · mahalliy'),!m.ready])]:[['browser','Qurilmada · bepul'],['montage','Serverda MP4 · bepul',!models.some(m=>m.id==='montage'&&m.ready)]];
 const model=available.find(m=>m.id===S.form.engine),ready=!ai||(S.connected&&model?.ready);
 return `${head(edit?'Video tahrirlash':ai?'Rasmdan video':'Rasmlardan montaj',edit?'Videoni kes, ovoz va subtitr qo‘sh.':ai?'Rasmlaringdagi qahramonlarni harakatga keltir.':'Rasmlarni ketma-ketlikka joyla, kamera effekti va musiqa qo‘sh.')} ${edit?'':`<div class="creation-modes"><button data-video-mode="ai" class="${ai?'active':''}">${icon('spark')}<strong>AI jonlantirish</strong><small>Qahramon va muhit harakati</small></button><button data-video-mode="montage" class="${!ai?'active':''}">${icon('video')}<strong>Rasmlardan montaj</strong><small>Rasmlar ketma-ketligi · bepul</small></button></div>`}
 ${ai&&!ready?videoConnectionNotice():''}
 ${S.exportError&&!ai?`<section class="connection-note" role="alert"><strong>Montaj tugamadi</strong><p>${esc(S.exportError)}</p></section>`:""}
 <div class="studio-layout"><section class="panel">${edit?upload('video','Telefon galereyasidan video','MP4 yoki WebM')+(S.video?`<p class="hint">${esc(S.video.name)}</p>`:''):imageSources()+refs()}
 <div class="form-grid">${select('engine',ai?'Jonlantiruvchi AI modeli':'Montaj usuli',rows)}${select('ratio','Nisbat',ai?['9:16','16:9','1:1']:['9:16','16:9','1:1','4:3','3:4','21:9'])}${select('quality','Eksport sifati',[['480','480p'],['720','720p'],['1080','1080p'],['2160','4K']])}</div>
 <div class="form-grid">${num('duration','Davomiylik · soniya',1,null,.1)}${select('fps','Eksport kadr tezligi',[24,30,60])}${edit?num('trimStart','Boshlanish · soniya',0,null,.1):ai?'':select('motion','Kamera effekti',[['zoom','Sekin yaqinlashish'],['pan','Yon tomonga'],['none','Harakatsiz']])}</div>
 ${ai?textArea('prompt','Nima harakat bo‘lsin?','Masalan: Intizor shar ortidan yuradi, yuqoriga qarab jilmayadi. Shamol kiyimi va sochini mayin tebratadi.')+aiVideoOptions()+sceneOptions():'<p class="hint">Bu rejim rasmlarga zoom yoki yon harakat qo‘shadi.</p>'}
 ${textArea('caption','Videoga qo‘shiladigan subtitr','Ixtiyoriy. Har qator alohida subtitr yoki SRT yukla.')}
 <div class="form-grid two"><div>${upload('audio','Musiqa yoki ovoz qo‘shish',S.audio?esc(S.audio.name):'MP3, WAV, OGG yoki WebM')} ${S.audio?'<button class="text-button" data-action="remove-audio">Ovozni olib tashlash ×</button>':''}</div><div>${upload('srt','SRT subtitrni yuklash','Vaqt kodlari saqlanadi')}</div></div>
 ${edit?select('filter','Rang uslubi',[['none','Asl ranglar'],['warm','Iliq ranglar'],['mono','Oq-qora']]):''}
 <p class="hint">${ai?'AI xizmati lavhalar yaratadi. Eksportdagi 4K/60 FPS tanlovi modelning asl tafsiloti yoki harakat tezligini oshirishni kafolatlamaydi.':'Eksport tugaguncha ilovani ochiq tut. Telefon uchun 720p / 30 FPS dan boshlash mumkin. Mos formatda MP4 yoki WebM saqlanadi.'}</p>
 ${videoActions(ai,ready,edit,model)}<button class="secondary full mt" data-page="gallery">Tayyor videolarim →</button>
 </section>${preview()}</div>`;
}
function imagePage(){const rows=S.health?.models?.image||[];return `${head('Rasm studiyasi','Rasmlaringni tahrirla yoki ulangan AI orqali yarat.')}<section class="panel"><div class="form-grid two">${select('imageEngine','Rejim',[['editor','Bepul rasm tahriri'],...rows.map(m=>[m.id,m.name+(m.paid?' · pullik':''),!m.ready])])}${select('imageRatio','Nisbat',['1:1','9:16','16:9','4:3','3:4'])}${select('imageQuality','Qisqa tomon',[['1024','1024 px'],['2048','2048 px'],['4096','4096 px']])}</div>${imageSources()}${refs()}${S.form.imageEngine==='editor'?`<div class="studio-layout mt"><div class="stack">${['brightness','contrast','saturation'].map((p,i)=>`<label>${['Yorqinlik','Kontrast','Rang to‘yinganligi'][i]}<input type="range" data-prop="${p}" min="0" max="200" value="${esc(S.form[p])}"></label>`).join('')}${select('rotation','Aylantirish',[[0,'0°'],[90,'90°'],[180,'180°'],[270,'270°']])}<label class="check"><input type="checkbox" data-prop="removeBackground" ${S.form.removeBackground?'checked':''}> Bir rangli fonni shaffof qilish</label><div class="form-grid two"><label>Fon rangi<input type="color" data-prop="keyColor" value="${esc(S.form.keyColor)}"></label><label>Rangga yaqinlik<input type="range" data-prop="tolerance" min="5" max="180" value="${esc(S.form.tolerance)}"></label></div><p class="hint">Bu bir rangli fon uchun vosita. Murakkab fonni AI bilan olib tashlash alohida model talab qiladi.</p>${select('imageFormat','Saqlash formati',[['png','PNG · shaffoflik bilan'],['jpeg','JPG']])}<button class="primary full" data-action="save-image">Rasmni saqlash ${icon('arrow')}</button></div><div class="preview-stage"><canvas id="imageCanvas" width="720" height="720"></canvas></div></div>`:textArea('imagePrompt','Rasm tavsifi','O‘zbekcha yoki inglizcha yoz…')+promptControls(false)+paidControl()+'<p class="hint">AI chiqish o‘lchami modelga bog‘liq. Reference bilan tahrir OpenAI va sozlangan ComfyUI workflow orqali ishlaydi.</p><button class="primary full mt" data-action="generate-image">AI rasm yaratish ✦</button>'}</section>`;}
function chatPage(){const models=S.health?.models?.chat||[],agent=S.health?.models?.agent;return `${head('AI yordamchi','G‘oya, storyboard, tavsif yoki istalgan savolingni yoz.')}<section class="panel chat-panel"><div class="form-grid two">${select('chatModel','Model',[['auto','Ulangan modelni tanlash'],...models.map(m=>[m.id,m.name+(m.paid?' · pullik':' · mahalliy')]),['agent','n8n agent',!agent]])}<div class="actions"><button class="secondary" data-action="new-chat">Yangi suhbat</button><button class="secondary" data-action="export-chat">Suhbatni saqlash</button></div></div><div class="messages" id="messages">${S.chat.length?S.chat.map(m=>`<div class="message ${esc(m.role)}">${esc(m.content)}</div>`).join(''):'<div class="message">Salom! Shirin AI studiyasiga xush kelibsan. AI bilan suhbat uchun Sozlamalarda o‘z serveringni ula. Mahalliy vositalar hozirdanoq tayyor.</div>'}</div><div class="chips">${['15 soniyali Mini Farm storyboard yoz.','Intizor uchun yangi video g‘oyasi yoz.','YouTube uchun inglizcha sarlavha yoz.'].map(p=>`<button data-chat-prompt="${esc(p)}">${esc(p.split(' uchun')[0].replace(' storyboard yoz.',''))}</button>`).join('')}</div><div class="composer"><textarea id="chatInput" placeholder="Xabaringni yoz…" aria-label="Chat xabari"></textarea><button class="primary" data-action="send-chat" aria-label="Xabar yuborish" ${S.chatBusy?'disabled':''}>${icon('arrow')}</button></div>${paidControl()}<p id="chatStatus" class="hint">${S.chatBusy?'AI javob bermoqda…':models.length?'Mahalliy modelga obuna talab qilinmaydi.':'Ollama yoki OpenAI ulanishi kerak. n8n alohida sozlanadi.'}</p></section>`;}
function voicePage(){return `${head('Ovoz studiyasi','Matnni tingla, ovozingni yoz yoki ulangan ovoz modelidan foydalan.')}<div class="studio-layout"><section class="panel">${textArea('voiceText','O‘qiladigan matn','Salom! Mini Farm sarguzashtiga xush kelibsiz!')}<div class="form-grid two">${select('voiceLanguage','Til',[['uz-UZ','O‘zbekcha'],['en-US','English'],['ru-RU','Русский']])}<label>Tezlik<input type="range" data-prop="voiceRate" min="0.5" max="1.5" step="0.05" value="${esc(S.form.voiceRate)}"></label></div><div class="actions"><button class="primary" data-action="speak">${icon('voice')} Tinglash · bepul</button><button class="secondary" data-action="stop-speech">To‘xtatish</button>${window.ShirinNative?'<button class="secondary" data-action="native-voice">WAV saqlash · qurilmada</button>':''}</div><p class="hint">Ovoz va tillar qurilmangdagi TTS dvigateliga bog‘liq. Brauzer TTS ovozini faylga chiqarmaydi; Android ilovada WAV saqlash bor.</p><div class="small-title">OVOZINGNI YOZIB OL</div><button class="secondary full" data-action="record-voice"><span class="record-indicator"></span> ${S.recorder?'Yozishni tugatish':'Mikrofondan yozish'}</button><div class="small-title">AI OVOZ</div>${paidControl()}<button class="secondary full" data-action="cloud-voice">Ulangan xizmatda ovoz yaratish</button><p class="hint">AI orqali yaratilgan ovoz. Xizmat tarifi va cheklovlari amal qiladi.</p></section><aside class="panel"><h3>Ovoz → video</h3><p class="muted mt">Yaratilgan yoki yozilgan ovoz galereyada saqlanadi. Uni Video yoki Tahrir bo‘limida musiqaga qo‘shishing mumkin.</p><button class="secondary full mt" data-page="gallery">Galereyani ochish</button></aside></div>`;}
function galleryPage(){const rows=S.artifacts.filter(a=>(S.filter==='all'||a.type.startsWith(S.filter))&&a.name.toLowerCase().includes(S.search.toLowerCase()));return `${head('Galereya','Rasmlaring, tayyor videolaring va ovozlaring bir joyda.')}<section class="gallery-import panel"><label class="file-button primary">${icon('upload')} Telefonda bor faylni qo‘shish<input type="file" data-upload="assets" accept="image/*,video/*,audio/*" multiple></label><button class="secondary" data-page="video">Rasmdan video yaratish →</button><p class="hint">Tanlangan fayllar ilova galereyasiga nusxalanadi.</p></section><div class="filterbar">${[['all','Barchasi'],['image','Rasmlar'],['video','Videolar'],['audio','Ovozlar']].map(([k,t])=>`<button data-filter="${k}" class="${S.filter===k?'active':''}">${t}</button>`).join('')}<input id="gallerySearch" type="search" placeholder="Ishlarni qidirish…" aria-label="Galereyadan qidirish" value="${esc(S.search)}"></div>${rows.length?`<div class="gallery-grid">${rows.map(a=>{const url=blobURL(a.blob);return `<article class="gallery-item"><div class="media">${a.type.startsWith('image')?`<img src="${url}" alt="${esc(a.name)}" loading="lazy">`:a.type.startsWith('video')?`<video src="${url}" controls preload="metadata" playsinline></video>`:`<audio src="${url}" controls preload="metadata"></audio>`}</div><div class="gallery-details"><strong>${esc(a.name)}</strong><span class="tag">${esc(a.origin||'Saqlangan fayl')}</span><small>${new Date(a.created).toLocaleDateString('uz-UZ')} · ${(a.blob.size/1048576).toFixed(1)} MB</small><div class="actions"><button data-download="${a.id}">Yuklash ↓</button>${window.ShirinNative?.beginGalleryDownload&&/^(image|video)\//.test(a.type)?`<button data-phone-save="${a.id}">Telefon galereyasiga ↓</button>`:""}<button data-use="${a.id}">${a.type.startsWith('image/')?'Jonlantirish':'Ishlatish'}</button><button data-rename="${a.id}" aria-label="Nomini o‘zgartirish">✎</button><button class="danger" data-delete="${a.id}" aria-label="O‘chirish">×</button></div></div></article>`;}).join('')}</div>`:`<section class="panel empty">${icon('gallery')}Hali ${S.filter==='all'?'saqlangan ish':'bu turdagi ish'} yo‘q.<br>Video yoki rasm yaratib shu yerga saqla.<div class="actions mt" style="justify-content:center"><button class="primary" data-page="video">Video yaratish</button></div></section>`}<div class="section-head"><h2>Serverdagi ishlar</h2><button class="text-button" data-action="refresh-jobs">Yangilash ↻</button></div><div id="serverJobs" class="jobs-list"><p class="hint">${S.connected?'Ishlar yuklanmoqda…':'Serverga ulansang, u yerdagi ishlaring ham ko‘rinadi.'}</p></div>`;}
function templatesPage(){return `${head('Tayyor g‘oyalar','O‘z rasmlaringni qo‘sh. Qahramonlarning ko‘rinishini saqla.')}<section class="template-grid">${TEMPLATES.map((t,i)=>`<article class="template-card"><div class="emoji">${t.emoji}</div><span class="tag">9:16 · 15 soniya</span><h2 class="mt">${esc(t.name)}</h2><p>${esc(t.desc)}</p><button class="secondary" data-template="${i}">Shablonni ishlatish →</button></article>`).join('')}</section>`;}
function settingsPage(){const h=S.health,c=h?.models;const items=[['Server',S.connected],['MP4 montaj',h?.montage&&h.models?.video?.some(m=>m.id==='montage')],['AI chat',c?.chat?.length||h?.chat_ready],['AI rasm',h?.higgsfield?.configured||c?.image?.some(m=>m.ready)||h?.image_ready],['AI video',S.connected&&(h?.higgsfield?.configured||c?.video?.some(m=>m.ready&&AI_VIDEO_KINDS.includes(m.id)))],['n8n agent',c?.agent]];return `${head('Sozlamalar','Mahalliy vositalar va AI ulanishlarini boshqar.')}<div class="settings-layout"><section class="panel"><h2>Serverga ulanish</h2><label class="file-button connection-import">${S.connecting?'Tekshirilmoqda…':'Ulanish faylini ochish'}<input type="file" data-upload="connection" accept=".json,application/json" aria-label="Ulanish faylini ochish" ${S.connecting||S.busy?'disabled':''}></label><p class="hint mt">Shirin-Ulanish.json faylini tanla. Server manzili va kod avtomatik olinadi; ulanish tekshirilgach, shu qurilmada eslab qolinadi.</p><label class="mt">Server manzili<input id="serverBase" type="url" value="${esc(S.settings.base)}" placeholder="https://server-manzili"></label><label class="mt">Ulanish kodi<input id="serverToken" type="password" value="${esc(S.settings.token)}" autocomplete="off" placeholder="Shaxsiy server koding"></label><label class="check"><input id="rememberToken" type="checkbox" ${S.settings.remember?'checked':''}> Shu qurilmada ulanish kodini eslab qolish</label><div class="actions"><button class="primary" data-action="connect" ${S.connecting?'disabled':''}>${S.connecting?'Tekshirilmoqda…':'Saqlash va tekshirish'}</button><button class="secondary" data-action="disconnect">Ulanishni uzish</button></div><p id="connectionStatus" class="hint">${S.connecting?'Ulanish tekshirilmoqda…':S.connected?'Server ulangan · '+esc(h?.release||'versiya noma’lum'):esc(S.connectionError||'Mahalliy rasm tahriri va montaj uchun server shart emas.')}</p><div class="health-grid mt">${items.map(([n,r])=>`<div class="health-item">${n}<b class="${r?'ready':''}">${r?(n==='Server'?'Ulangan':'Sozlangan'):'Ulanmagan'}</b></div>`).join('')}</div>${videoSetupDetails()}</section><section class="panel"><h2>Saqlash</h2><p class="muted">Galereya va qoralamalar shu qurilmada saqlanadi. Brauzer ma’lumotlari tozalansa ular o‘chadi; muhim fayllarni yuklab ol.</p><div class="actions mt"><button class="secondary" data-action="persist-storage">Doimiy saqlashni so‘rash</button><button class="secondary" data-action="export-project">Loyiha nusxasini saqlash</button></div><label class="upload-zone mt">Loyiha nusxasini ochish<input type="file" data-upload="project" accept=".json"></label></section><section class="panel"><h2>Bepul ishlash haqida</h2><p class="muted">Mahalliy vositalarda obuna, kredit, suv belgisi va kunlik mahsulot kvotasi yo‘q. Qurilma xotirasi va tezligi amaliy chegarani belgilaydi.</p><p class="muted mt">Ollama chat va ComfyUI rasm/video o‘z kompyutering yoki serveringda ishlashi mumkin. Modellar va hisoblash quvvati alohida o‘rnatiladi. Pullik xizmatlarning narxi va cheklovlari saqlanadi.</p><p class="hint">Shirin AI Studio 0.1.1 · mustaqil ilova</p></section></div>`;}
function render(){const navScroll=$('navigation').scrollLeft;S.urls.splice(0).forEach(u=>URL.revokeObjectURL(u));nav();$('navigation').scrollLeft=navScroll;$('navigation').querySelector('.active')?.scrollIntoView({block:'nearest',inline:'nearest'});$('view').innerHTML=({home,studio:studioPage,models:modelsPage,effects:effectsPage,canvas:canvasPage,montage:()=>videoPage(false),video:()=>videoPage(false),edit:()=>videoPage(true),image:imagePage,chat:chatPage,voice:voicePage,gallery:galleryPage,templates:templatesPage,settings:settingsPage}[S.page]||home)();if(S.page==='image'&&S.form.imageEngine==='editor')drawEditor().catch(e=>toast(e.message));if(['video','montage','edit'].includes(S.page))drawVideoReference().catch(e=>toast(e.message));if(S.page==='gallery'&&S.connected)loadJobs();if(S.page==='chat'&&$('messages'))$('messages').scrollTop=$('messages').scrollHeight;}
function go(page){closeSheet();if(page==='video'&&!S.busy)S.form.engine=chooseVideoEngine();if(page==='edit'&&!S.busy)S.form.engine=['browser','montage'].includes(S.form.engine)?S.form.engine:'browser';S.page=page;history.replaceState(null,'','#'+page);render();window.scrollTo({top:0});}
const nativeRequests=new Map();
function nativeServerRequest(request,signal){return new Promise((resolve,reject)=>{
 const ticket=id();
 const abort=()=>{nativeRequests.delete(ticket);signal?.removeEventListener('abort',abort);window.ShirinNative?.cancelServerRequest?.(ticket);reject(new DOMException('So‘rov bekor qilindi.','AbortError'));};
 if(signal?.aborted){reject(new DOMException('So‘rov bekor qilindi.','AbortError'));return;}
 nativeRequests.set(ticket,result=>{signal?.removeEventListener('abort',abort);result.error?reject(Error(result.error)):resolve(result);});
 signal?.addEventListener('abort',abort,{once:true});
 try{window.ShirinNative.requestServer(JSON.stringify({...request,id:ticket}));}catch(error){nativeRequests.delete(ticket);signal?.removeEventListener('abort',abort);reject(Error('Qurilma server so‘rovini boshlay olmadi.'));}
});}
window.onNativeServerResult=result=>{const done=nativeRequests.get(result?.id);if(!done){if(result?.url)window.ShirinNative?.releaseServerMedia?.(result.id);return;}nativeRequests.delete(result.id);done(result);};
async function api(path,body,timeout=180000){
 let base=S.settings.base.replace(/\/$/,'');if(!base)base=location.origin;
 if(!/^https:\/\//.test(base)&&!/^http:\/\/(localhost|127\.0\.0\.1)(:\d+)?$/.test(base))throw Error('Server uchun HTTPS manzil kerak.');
 const c=new AbortController(),t=setTimeout(()=>c.abort(),timeout);
 try{
  let r;
  if(window.ShirinNative?.requestServer){
   const result=await nativeServerRequest({type:'api',base,path,token:S.settings.token,body:body===undefined?null:JSON.stringify(body),timeout},c.signal);
   if(!Number.isInteger(result.status))throw Error('Server holati o‘qilmadi.');
   r={status:result.status,ok:result.status>=200&&result.status<300,json:async()=>JSON.parse(result.body)};
  }else r=await fetch(base+path,{method:body===undefined?'GET':'POST',headers:{'Content-Type':'application/json',...(S.settings.token?{Authorization:'Bearer '+S.settings.token}:{})},body:body===undefined?undefined:JSON.stringify(body),signal:c.signal,cache:'no-store',redirect:'error'});
  let d;try{d=await r.json();}catch{throw Error('Server javobi o‘qilmadi (HTTP '+r.status+').');}
  if(!r.ok){const e=Error(d.error||'Server xatosi: '+r.status);e.status=r.status;throw e;}return d;
 }catch(e){if(e.name==='AbortError')throw Error(path==='/health'?'Server 15 soniyada javob bermadi. Manzil va internetni tekshir.':'Javob kechikdi. Qayta yuborishdan oldin Galereyadagi server ishlarini tekshir.');throw e;}finally{clearTimeout(t);}
}
// Connection files contain a private access code. Never include them in the APK.
const DEFAULT_SHIRIN_SERVER='https://begborim-apk-builder4-production.up.railway.app';
function parseConnectionFile(text){
 if(typeof text!=='string'||text.length>65536)throw Error('Ulanish fayli juda katta. Shirin ulanish faylini tanla.');
 let root;try{root=JSON.parse(text.replace(/^\uFEFF/,''));}catch{throw Error('Ulanish fayli o‘qilmadi. JSON faylini qayta tanla.');}
 if(!root||typeof root!=='object'||Array.isArray(root))throw Error('Bu Shirin ulanish fayli emas.');
 let value;
 if(root.format==='shirin-connection'){
  if(root.version!==1)throw Error('Ulanish faylining bu versiyasi qo‘llanmaydi.');
  value=root;
 }else if(root.connection&&typeof root.git_commit==='string')value=root.connection;
 else throw Error('Bu Shirin ulanish fayli emas.');
 if(!value||typeof value!=='object'||Array.isArray(value)||typeof value.server_url!=='string'||typeof value.connection_code!=='string')throw Error('Faylda server manzili yoki ulanish kodi yo‘q.');
 const raw=value.server_url.trim();let url;
 try{url=new URL(raw);}catch{throw Error('Fayldagi server manzili noto‘g‘ri.');}
 if(url.protocol!=='https:'||url.username||url.password||url.pathname!=='/'||url.search||url.hash||/\s/.test(raw))throw Error('Faylda serverning asosiy HTTPS manzili bo‘lishi kerak.');
 const token=value.connection_code.trim();
 if(token.length<32||token.length>4096||/[^\x21-\x7e]/.test(token))throw Error('Fayldagi ulanish kodi noto‘g‘ri yoki to‘liq emas.');
 return {base:url.origin,token,remember:true};
}
async function importConnectionFile(file){
 if(S.busy||S.connecting)throw Error('Avvalgi ish tugashini kut.');
 if(file.size>65536)throw Error('Ulanish fayli juda katta. Shirin ulanish faylini tanla.');
 const settings=parseConnectionFile(await file.text());
 await connect(settings);
}
async function connect(candidate){
 if(S.busy)throw Error('Avvalgi ish tugashini kut.');
 if(S.connecting)throw Error('Ulanish tekshirilmoqda. Javobni kut.');
 const attempt=++S.connectAttempt;
 const base=(candidate?.base??$('serverBase')?.value??S.settings.base).trim().replace(/\/$/,'');
 S.settings={base,token:(candidate?.token??$('serverToken')?.value??S.settings.token).trim(),remember:candidate?.remember??$('rememberToken')?.checked??S.settings.remember};
 S.connected=false;S.health=null;S.connectionError='';S.connecting=true;render();
 try{
  if(base){const url=new URL(base);if(url.pathname!=='/'||url.search||url.hash||url.username||url.password)throw Error('Serverning faqat asosiy HTTPS manzilini yoz.');}
  if((window.ShirinNative||!['localhost','127.0.0.1'].includes(location.hostname))&&!S.settings.token)throw Error('Ulanish kodi bo‘sh. Tayyor ulanish faylini och yoki shaxsiy kodni kirit.');
  const health=await api('/health',undefined,15000);
  if(health?.name!=='Shirin AI')throw Error('Bu Shirin serveri emas. Shirin uchun alohida server manzilini kirit.');
  if(attempt!==S.connectAttempt)return;
  if(!health||typeof health!=='object'||Array.isArray(health)||(!health.models&&typeof health.configured!=='boolean'))throw Error('Bu manzilda Shirin AI serveri aniqlanmadi.');
  if(!health.models){health.models={chat:health.chat_ready?[{id:'auto',name:'Serverdagi chat',paid:true,ready:true}]:[],image:health.image_ready?[{id:'openai_image',name:'Serverdagi rasm modeli',paid:true,ready:true}]:[],video:health.configured&&health.video_provider==='fal'?[{id:'fal_video',name:'Kling · mavjud server',ready:true,paid:true,legacy:true}]:[],vision:!!health.image_text,narration:!!health.voice_languages?.length,agent:false};}
  for(const kind of ['chat','image','video'])if(!Array.isArray(health.models[kind]))health.models[kind]=[];
  S.health=health;S.connected=true;S.connecting=false;
  localStorage.setItem('shirin-studio-settings',JSON.stringify({...S.settings,token:S.settings.remember?S.settings.token:''}));
  sessionStorage.setItem('shirin-studio-token',S.settings.token);
  if(window.ShirinNative?.saveSettings)window.ShirinNative.saveSettings(JSON.stringify(S.settings));
  if(!['browser','montage'].includes(S.form.engine)&&!health.models.video.some(m=>m.id===S.form.engine&&AI_VIDEO_KINDS.includes(m.id)&&m.ready))S.form.engine=chooseVideoEngine();
  render();toast('Server ulandi. Xizmatlar holati yangilandi.');
 }catch(error){
  if(attempt!==S.connectAttempt)return;
  S.connected=false;S.health=null;S.connecting=false;S.connectionError=error instanceof TypeError?'Serverga ulanib bo‘lmadi. Server manzili va internetni tekshir.':error.message;
  render();throw Error(S.connectionError);
 }
}
async function addRefs(files){if(S.busy)throw Error('Eksport tugashini kut.');for(const file of files){if(!file.type.startsWith('image/'))throw Error('Rasm faylini tanla.');const bitmap=await createImageBitmap(file);try{if(bitmap.width*bitmap.height>64000000)throw Error('Rasm juda katta. Uni kichraytirib qayta tanla.');const factor=Math.min(1,2048/Math.max(bitmap.width,bitmap.height)),c=document.createElement('canvas');c.width=Math.max(1,Math.round(bitmap.width*factor));c.height=Math.max(1,Math.round(bitmap.height*factor));const ctx=c.getContext('2d');ctx.drawImage(bitmap,0,0,c.width,c.height);const blob=await new Promise(r=>c.toBlob(r,file.type==='image/png'?'image/png':'image/jpeg',.9));const small=document.createElement('canvas');small.width=140;small.height=Math.round(c.height/c.width*140);small.getContext('2d').drawImage(c,0,0,small.width,small.height);S.refs.push({id:id(),name:file.name,blob,thumb:small.toDataURL('image/jpeg',.65)});}finally{bitmap.close();}}await draft();render();toast(S.refs.length+' ta rasm tayyor.');}
function fit(ctx,source,w,h,cover=false,zoom=1,pan=0){const sw=source.videoWidth||source.width,sh=source.videoHeight||source.height,scale=(cover?Math.max(w/sw,h/sh):Math.min(w/sw,h/sh))*zoom;ctx.drawImage(source,(w-sw*scale)/2+pan,(h-sh*scale)/2,sw*scale,sh*scale);}
let editorSeq=0;
async function drawEditor(){const seq=++editorSeq,c=$('imageCanvas');if(!c)return;const [w,h]=dimensions(S.form.imageRatio,S.form.imageQuality);c.width=w;c.height=h;const ctx=c.getContext('2d');ctx.clearRect(0,0,w,h);if(!S.refs[0]){ctx.fillStyle='#122337';ctx.fillRect(0,0,w,h);ctx.fillStyle='#91a7bf';ctx.textAlign='center';ctx.font='28px sans-serif';ctx.fillText('Rasm tanla',w/2,h/2);return;}const bitmap=await createImageBitmap(S.refs[0].blob);if(seq!==editorSeq){bitmap.close();return;}ctx.save();ctx.filter=`brightness(${S.form.brightness}%) contrast(${S.form.contrast}%) saturate(${S.form.saturation}%)`;ctx.translate(w/2,h/2);ctx.rotate(Number(S.form.rotation)*Math.PI/180);const swapped=Number(S.form.rotation)%180!==0;const dw=swapped?h:w,dh=swapped?w:h;ctx.translate(-dw/2,-dh/2);fit(ctx,bitmap,dw,dh,true);ctx.restore();bitmap.close();if(S.form.removeBackground){const d=ctx.getImageData(0,0,w,h),color=S.form.keyColor.match(/[a-f\d]{2}/gi).map(v=>parseInt(v,16)),tol=Number(S.form.tolerance);for(let i=0;i<d.data.length;i+=4){const dist=Math.hypot(d.data[i]-color[0],d.data[i+1]-color[1],d.data[i+2]-color[2]);d.data[i+3]=Math.min(d.data[i+3],Math.round(Math.max(0,Math.min(1,(dist-tol)/20))*255));}ctx.putImageData(d,0,0);}}
async function saveArtifact(blob,name,origin='Saqlangan fayl'){if(!blob||!blob.size)throw Error('Bo‘sh fayl saqlanmadi.');const artifact={id:id(),created:Date.now(),blob,type:blob.type||'application/octet-stream',name,origin};await dbPut('assets',artifact);S.artifacts.unshift(artifact);toast('Galereyaga saqlandi.');return artifact;}
async function download(blob,name,toGallery=false){if(window.ShirinNative?.beginDownload){const data=await fileData(blob),b=data.split(',')[1],ticket=id();const started=toGallery&&window.ShirinNative.beginGalleryDownload?window.ShirinNative.beginGalleryDownload(ticket,name,blob.type,b.length):window.ShirinNative.beginDownload(ticket,name,blob.type,b.length);if(!started)throw Error('Faylni saqlash boshlanmadi.');for(let i=0;i<b.length;i+=131072){window.ShirinNative.downloadChunk(ticket,b.slice(i,i+131072));await new Promise(r=>setTimeout(r,0));}window.ShirinNative.finishDownload(ticket);return;}const url=URL.createObjectURL(blob),a=document.createElement('a');a.href=url;a.download=name;a.click();setTimeout(()=>URL.revokeObjectURL(url),60000);}
function task(label,progress=0){$('taskbar').hidden=false;$('tasklabel').textContent=label;$('taskprogress').value=progress;}
function endTask(){S.busy=false;S.cancel=false;$('taskbar').hidden=true;}
function parseTime(text){return text.trim().replace(',','.').split(':').reduce((a,v)=>a*60+Number(v),0);}
function cuesFromText(text,duration,count){if(!text.trim())return [];const blocks=text.trim().split(/\n\s*\n/);if(text.includes('-->')){return blocks.map(b=>{const rows=b.split('\n'),index=rows.findIndex(s=>s.includes('-->'));if(index<0)return null;const [a,z]=rows[index].split('-->');return {start:parseTime(a),end:parseTime(z),text:rows.slice(index+1).join('\n')};}).filter(c=>c&&Number.isFinite(c.start)&&Number.isFinite(c.end)&&c.end>c.start);}const lines=text.split('\n').filter(s=>s.trim());return lines.map((line,i)=>{const match=line.match(/^([\d:.]+)\s*[–-]\s*([\d:.]+)\s*\|\s*(.*)$/);return match?{start:parseTime(match[1]),end:parseTime(match[2]),text:match[3]}:{start:i*duration/lines.length,end:(i+1)*duration/lines.length,text:line};});}
function drawCaption(ctx,text,w,h){if(!text)return;const font=Math.max(18,Math.round(h*.035));ctx.font=`600 ${font}px sans-serif`;ctx.textAlign='center';ctx.textBaseline='middle';const lines=[];for(const line of text.split('\n')){let row='';for(const word of line.split(' ')){const next=row?row+' '+word:word;if(ctx.measureText(next).width>w*.85&&row){lines.push(row);row=word;}else row=next;}lines.push(row);}const y=h*.86-(lines.length-1)*font*.6;ctx.lineJoin='round';ctx.lineWidth=Math.max(3,font*.12);for(let i=0;i<lines.length;i++){ctx.strokeStyle='#000c';ctx.strokeText(lines[i],w/2,y+i*font*1.25);ctx.fillStyle='#fff';ctx.fillText(lines[i],w/2,y+i*font*1.25);}}
function exportWait(promise,signal,message,timeout=15000){
 return new Promise((resolve,reject)=>{
  let settled=false,timer;
  const finish=(fn,value)=>{if(settled)return;settled=true;clearTimeout(timer);signal?.removeEventListener('abort',abort);fn(value);};
  const abort=()=>finish(reject,signal.reason||new DOMException('Eksport bekor qilindi.','AbortError'));
  signal?.addEventListener('abort',abort,{once:true});
  timer=setTimeout(()=>finish(reject,Error(message)),timeout);
  Promise.resolve(promise).then(v=>finish(resolve,v),e=>finish(reject,e));
  if(signal?.aborted)abort();
 });
}
function mediaLoaded(el,signal){
 return new Promise((resolve,reject)=>{
  let timer;const events=['loadedmetadata','loadeddata','canplay'];
  const cleanup=()=>{clearTimeout(timer);events.forEach(e=>el.removeEventListener(e,ready));el.removeEventListener('error',fail);signal?.removeEventListener('abort',abort);};
  const finish=(fn,value)=>{cleanup();fn(value);};
  const ready=()=>{if(el.readyState>=(el.tagName==='VIDEO'?2:1))finish(resolve,el);};
  const fail=()=>finish(reject,Error('Media fayli o‘qilmadi. Boshqa video yoki audio tanla.'));
  const abort=()=>finish(reject,signal.reason||new DOMException('Eksport bekor qilindi.','AbortError'));
  events.forEach(e=>el.addEventListener(e,ready));el.addEventListener('error',fail,{once:true});signal?.addEventListener('abort',abort,{once:true});
  timer=setTimeout(()=>finish(reject,Error('Video yoki audio ochilishi cho‘zildi. Faylni qayta tanla.')),15000);
  if(signal?.aborted)abort();else if(el.error)fail();else ready();
 });
}
function seekExportVideo(video,start,signal){
 if(start===0)return Promise.resolve();
 return new Promise((resolve,reject)=>{
  let timer;
  const finish=(fn,value)=>{clearTimeout(timer);video.removeEventListener('seeked',done);video.removeEventListener('error',fail);signal.removeEventListener('abort',abort);fn(value);};
  const done=()=>finish(resolve),fail=()=>finish(reject,Error('Video boshiga o‘tib bo‘lmadi.'));
  const abort=()=>finish(reject,signal.reason||new DOMException('Eksport bekor qilindi.','AbortError'));
  video.addEventListener('seeked',done,{once:true});video.addEventListener('error',fail,{once:true});signal.addEventListener('abort',abort,{once:true});
  timer=setTimeout(fail,15000);if(signal.aborted)return abort();
  try{video.currentTime=start;if(!video.seeking&&Math.abs(video.currentTime-start)<.05)done();}catch{fail();}
 });
}
async function startExportRecorder(stream,bitrate,controller,drawFirst){
 const types=['video/mp4;codecs=avc1.42E01E,mp4a.40.2','video/mp4','video/webm;codecs=vp8,opus','video/webm;codecs=vp9,opus','video/webm'];
 for(const mime of types){
  if(controller.signal.aborted)throw controller.signal.reason;
  if(!MediaRecorder.isTypeSupported(mime))continue;
  let recorder;
  try{
   recorder=new MediaRecorder(stream,{mimeType:mime,videoBitsPerSecond:bitrate});
   const state={recorder,chunks:[],fault:null,done:null};
   state.done=new Promise(resolve=>recorder.onstop=resolve);
   recorder.ondataavailable=e=>{if(e.data.size)state.chunks.push(e.data);};
   recorder.onerror=()=>{state.fault=Error('Telefon video yozishni to‘xtatdi. 720p va 30 FPS bilan qayta urinib ko‘r.');if(!controller.signal.aborted)controller.abort(state.fault);};
   recorder.start(250);
   if(recorder.state!=='recording')throw Error('Video yozish boshlanmadi.');
   // onstart may need live audio packets. Let playback start before waiting for encoded data.
   drawFirst();stream.getVideoTracks()[0]?.requestFrame?.();
   state.type=(recorder.mimeType||mime).split(';')[0];return state;
  }catch(error){
   if(recorder){recorder.onerror=null;try{if(recorder.state!=='inactive')recorder.stop();}catch{}}
   if(controller.signal.aborted)throw controller.signal.reason||error;
  }
 }
 throw Error('Bu sozlamada telefon video yoza olmadi. 720p / 30 FPS tanla yoki serverda MP4 montajdan foydalan.');
}
function runExportFrames(paint,duration,controller){
 return new Promise((resolve,reject)=>{
  const signal=controller.signal;let frame,closed=false;const began=performance.now();
  const finish=(fn,value)=>{if(closed)return;closed=true;cancelAnimationFrame(frame);signal.removeEventListener('abort',abort);fn(value);};
  const abort=()=>finish(reject,signal.reason||new DOMException('Eksport bekor qilindi.','AbortError'));
  signal.addEventListener('abort',abort,{once:true});
  const tick=()=>{try{if(signal.aborted)return abort();if(S.cancel){controller.abort(new DOMException('Eksport bekor qilindi.','AbortError'));return;}const t=(performance.now()-began)/1000;if(t>=duration)return finish(resolve);paint(t);frame=requestAnimationFrame(tick);}catch(e){finish(reject,e);}};
  if(signal.aborted)abort();else frame=requestAnimationFrame(tick);
 });
}
async function localVideo(edit){
 if(S.busy)throw Error('Avvalgi eksport tugashini kut.');
 const form={...S.form},refs=S.refs.slice(),audioFile=S.audio,videoFile=S.video;
 if(edit&&!videoFile)throw Error('Video tanla.');if(!edit&&!refs.length)throw Error('Kamida bitta rasm tanla.');
 if(!window.MediaRecorder||!HTMLCanvasElement.prototype.captureStream)throw Error('Bu qurilmada brauzer eksporti qo‘llanmaydi. Serverda MP4 rejimini tanla.');
 const requested=Number(form.duration),fps=Number(form.fps);
 if(!Number.isFinite(requested)||requested<1)throw Error('Davomiylik kamida 1 soniya bo‘lsin.');
 if(![24,30,60].includes(fps))throw Error('24, 30 yoki 60 FPS tanla.');
 if(!edit&&refs.length>Math.round(requested*fps))throw Error('Har bir rasm ko‘rinishi uchun davomiylikni uzaytir.');
 const controller=new AbortController(),signal=controller.signal;
 S.busy=true;S.cancel=false;S.exportError='';S.localExport=controller;task('Video tayyorlanmoqda…');
 let source=null,audio=null,audioCtx=null,recording=null,stream=null,screenLock=null,alive=true,frameIndex=0,lastProgress=-1;
 const localUrls=[],bitmaps=new Map(),pending=new Map(),decodeErrors=new Map();
 const stopForBackground=()=>{if(document.hidden&&!signal.aborted)controller.abort(Error('Ilova fonda qolgani uchun montaj to‘xtatildi. Qayta boshlaganda eksport tugaguncha ilovani ochiq tut.'));};
 document.addEventListener('visibilitychange',stopForBackground);
 window.ShirinNative?.setExportActive?.(true);
 if(navigator.wakeLock?.request)navigator.wakeLock.request('screen').then(lock=>{if(alive)screenLock=lock;else lock.release().catch(()=>{});}).catch(()=>{});
 const prepareImage=index=>{
  if(index>=refs.length)return Promise.resolve(null);
  if(bitmaps.has(index))return Promise.resolve(bitmaps.get(index));
  if(!pending.has(index))pending.set(index,createImageBitmap(refs[index].blob).then(b=>{if(!alive){b.close();return null;}bitmaps.set(index,b);return b;},e=>{decodeErrors.set(index,e);return null;}));
  return pending.get(index);
 };
 try{
  if(document.hidden)stopForBackground();if(signal.aborted)throw signal.reason;
  const [w,h]=dimensions(form.ratio,form.quality),c=document.createElement('canvas');c.width=w;c.height=h;const ctx=c.getContext('2d');
  if(!ctx)throw Error('Video uchun xotira ajratilmadi. Pastroq sifat bilan urinib ko‘r.');
  let duration=requested,audioReady=null;
  if(audioFile||edit){const Audio=window.AudioContext||window.webkitAudioContext;if(!Audio)throw Error('Bu qurilmada ovozli montaj qo‘llanmaydi.');audioCtx=new Audio();audioReady=exportWait(audioCtx.resume(),signal,'Ovoz dvigateli ishga tushmadi. Ilovani qayta ochib urinib ko‘r.');audioReady.catch(()=>{});}
  if(edit){
   source=document.createElement('video');source.playsInline=true;source.preload='auto';source.src=URL.createObjectURL(videoFile.blob);localUrls.push(source.src);await mediaLoaded(source,signal);
   const start=Number(form.trimStart)||0;if(start<0||(Number.isFinite(source.duration)&&start>=source.duration))throw Error('Boshlanish vaqti video oxiridan katta.');
   if(Number.isFinite(source.duration))duration=Math.min(requested,source.duration-start);
   await seekExportVideo(source,start,signal);
   if(audioFile)source.muted=true;
  }else{
   await exportWait(Promise.all([prepareImage(0),prepareImage(1)]),signal,'Rasm ochilishi cho‘zildi. Rasmni kichraytirib qayta tanla.');
   if(!bitmaps.has(0)||(refs.length>1&&!bitmaps.has(1)))throw Error('Rasm ochilmadi. Rasmlarni qayta tanla.');
  }
  const cues=cuesFromText(form.caption,duration,refs.length);stream=c.captureStream(fps);
  if(audioCtx){
   await audioReady;audio=audioFile?document.createElement('audio'):source;
   if(audioFile){audio.preload='auto';audio.src=URL.createObjectURL(audioFile.blob);localUrls.push(audio.src);await mediaLoaded(audio,signal);}
   const node=audioCtx.createMediaElementSource(audio),dest=audioCtx.createMediaStreamDestination();node.connect(dest);
   for(const track of dest.stream.getAudioTracks())stream.addTrack(track);
  }
  function paint(t){
   ctx.fillStyle='#0a0d14';ctx.fillRect(0,0,w,h);ctx.save();
   if(form.filter==='mono'&&edit)ctx.filter='grayscale(1)';else if(form.filter==='warm'&&edit)ctx.filter='sepia(.2) saturate(1.12)';
   if(source)fit(ctx,source,w,h);
   else{
    const span=duration/refs.length,index=Math.min(refs.length-1,Math.floor(t/span)),fraction=(t-index*span)/span;
    if(index>frameIndex+1)throw Error('Telefon band bo‘lib, sahna o‘tib ketdi. Pastroq sifat yoki uzoqroq davomiylik bilan qayta urinib ko‘r.');
    if(!bitmaps.has(index))throw Error(decodeErrors.has(index)?'Sahna rasmi o‘qilmadi. Uni qayta tanla.':'Sahna rasmi tayyorlanishga ulgurmadi. Davomiylikni uzaytirib qayta urinib ko‘r.');
    if(index!==frameIndex){for(const [old,b] of bitmaps)if(old<index){b.close();bitmaps.delete(old);}frameIndex=index;prepareImage(index+1);}
    fit(ctx,bitmaps.get(index),w,h,false,form.motion==='zoom'?1+.08*fraction:form.motion==='pan'?1.08:1,form.motion==='pan'?(fraction-.5)*w*.06:0);
   }
   ctx.restore();drawCaption(ctx,cues.find(x=>t>=x.start&&t<x.end)?.text,w,h);
   const progress=Math.min(99,Math.floor(t/duration*100));if(progress!==lastProgress){lastProgress=progress;task('Eksport · '+progress+'%',t/duration);}
  }
  paint(0);recording=await startExportRecorder(stream,Math.max(2000000,w*h*fps*.13),controller,()=>paint(0));
  if(source)await exportWait(source.play(),signal,'Video ijrosi boshlanmadi.');
  if(audio&&audio!==source)await exportWait(audio.play(),signal,'Ovoz ijrosi boshlanmadi.');
  await runExportFrames(paint,duration,controller);
  if(!edit&&frameIndex<refs.length-1)throw Error('Oxirgi sahna yozilishga ulgurmadi. Davomiylikni uzaytirib qayta urinib ko‘r.');
  if(audio)audio.pause();if(source)source.pause();task('Video saqlanmoqda…',1);
  if(recording.recorder.state!=='inactive')recording.recorder.stop();
  await exportWait(recording.done,signal,'Video faylini yakunlab bo‘lmadi. Qayta urinib ko‘r.');
  if(recording.fault)throw recording.fault;
  const type=(recording.chunks[0]?.type||recording.type).split(';')[0],blob=new Blob(recording.chunks,{type}),ext=type.includes('mp4')?'mp4':'webm';
  if(!blob.size)throw Error('Video yozilmadi. Pastroq sifat bilan qayta urinib ko‘r.');
  await saveArtifact(blob,'Shirin-'+(edit?'tahrir':'video')+'-'+Date.now()+'.'+ext,edit?'Video tahriri':'Rasmlardan montaj');
  if(S.page==='gallery')render();else go('gallery');
 }catch(error){
  if(error.name==='AbortError'){toast('Eksport bekor qilindi.');return;}
  const message=error.name==='NotAllowedError'?'Video yoki ovoz ijrosiga ruxsat berilmadi. Ilovani qayta ochib montajni boshlang.':error.name==='QuotaExceededError'?'Galereya uchun bo‘sh joy yetmadi. Keraksiz fayllarni yuklab olib, galereyadan o‘chir.':error.message||'Montaj bajarilmadi.';
  S.exportError=message;if(['video','edit'].includes(S.page))render();throw Error(message);
 }finally{
  alive=false;document.removeEventListener('visibilitychange',stopForBackground);
  if(recording){recording.recorder.onerror=null;try{if(recording.recorder.state!=='inactive')recording.recorder.stop();}catch{}}
  if(audio)audio.pause();if(source)source.pause();stream?.getTracks().forEach(t=>t.stop());
  if(audioCtx)audioCtx.close().catch(()=>{});bitmaps.forEach(b=>b.close());localUrls.forEach(u=>URL.revokeObjectURL(u));
  screenLock?.release().catch(()=>{});window.ShirinNative?.setExportActive?.(false);S.localExport=null;endTask();if(['video','edit'].includes(S.page))render();
 }
}
window.onNativeExportInterrupted=()=>{if(S.localExport&&!S.localExport.signal.aborted)S.localExport.abort(Error('Ilova fonda qolgani uchun montaj to‘xtatildi. Eksport tugaguncha Shirin AI oynasini ochiq tut.'));};
async function pollJob(job){while(['IN_QUEUE','IN_PROGRESS','SUBMITTING','ASSEMBLING'].includes(job.status)){if(S.cancel){await api('/jobs/'+job.id+'/cancel',{});toast('Bekor qilish so‘rovi yuborildi.');return null;}task(job.stage||'Serverda tayyorlanmoqda…',job.progress||0);await new Promise(r=>setTimeout(r,2000));job=await api('/jobs/'+job.id);}if(job.status!=='COMPLETED')throw Error(job.error||'Ish tugamadi: '+job.status);return job;}
async function importJob(job){
 const base=S.settings.base||location.origin,url=new URL(job.url,base);if(!['https:','http:'].includes(url.protocol))throw Error('Natija manzili noto‘g‘ri.');
 const c=new AbortController(),timer=setTimeout(()=>c.abort(),180000);let local,blob;
 try{
  if(window.ShirinNative?.requestServer&&url.protocol==='https:'&&url.origin===new URL(base).origin&&url.pathname.startsWith('/media/'))local=await nativeServerRequest({type:'media',base,url:url.href,timeout:180000},c.signal);
  const r=await fetch(local?.url||url,{signal:c.signal});if(!r.ok)throw Error('Natijani yuklab bo‘lmadi.');blob=await r.blob();
 }finally{clearTimeout(timer);if(local)window.ShirinNative?.releaseServerMedia?.(local.id);}
 const type=blob.type.split(';')[0];if(type!==blob.type)blob=new Blob([blob],{type});
 const ext={'video/mp4':'mp4','video/webm':'webm','image/png':'png','image/jpeg':'jpg','image/webp':'webp','audio/mpeg':'mp3','audio/wav':'wav'}[type]||'bin';
 return saveArtifact(blob,'Shirin-'+job.id.slice(0,8)+'.'+ext,['fal_video','image_video','text_video','comfy_video','hf_video'].includes(job.kind)?'AI video':job.kind==='montage'?'Rasmlardan montaj':'Server natijasi');
}
async function serverJob(body,route='/jobs'){
 if(S.busy)throw Error('Avvalgi ish tugashini kut.');
 if(!S.connected)throw Error('Sozlamalarda serverga ulan.');
 const animation=body.video_intent==='animation';
 S.busy=true;S.cancel=false;if(animation)S.videoError='';task('So‘rov yuborilmoqda…');
 const checkAnimation=job=>{
  if(animation&&(!AI_JOB_KINDS.includes(job.kind)||job.video_intent&&job.video_intent!=='animation'||job.image))throw Error('Server AI jonlantirish o‘rniga boshqa turdagi natija qaytardi. Natija AI video sifatida saqlanmadi. Serverni yangila.');
 };
 try{
  let job=await api(route,{id:id(),...body,allow_paid:S.form.paid});checkAnimation(job);
  if(job.image){await saveArtifact(blobFromData(job.image),'Shirin-AI-image-'+Date.now()+'.png');}
  else{job=await pollJob(job);if(!job)return;checkAnimation(job);await importJob(job);}
  if(S.page==='gallery')render();else go('gallery');
 }catch(error){if(animation)S.videoError=error.message;throw error;}
 finally{endTask();if(['video','edit'].includes(S.page))render();}
}
async function createVideo(edit){
 const ai=!edit&&!['browser','montage'].includes(S.form.engine),model=(S.health?.models?.video||[]).find(m=>m.id===S.form.engine);
 if(ai&&(!S.connected||!model?.ready||model.id==='montage'))throw Error('AI video modeli ulanmagan. Sozlamalarda ulanishni tekshir.');
 if(ai&&model.paid&&!S.form.paid)throw Error('Bu AI modeli pullik. Xizmat xarajatiga ruxsatni alohida yoqish kerak.');
 if(ai&&!S.form.prompt.trim()&&!(S.form.engine==='fal_video'&&S.form.autoText)&&!(S.refs.length&&S.refs.every(r=>r.scenePrompt?.trim())))throw Error('Qanday harakat bo‘lishini yoz yoki har bir sahnani tavsifla.');
 if(S.form.engine==='browser')return localVideo(edit);
 if(!S.connected)throw Error('Sozlamalarda serverga ulan.');
 const customScenes=S.refs.some(r=>r.scenePrompt?.trim()),newSceneAPI=S.health?.capabilities?.scene_prompts===true;
 if(ai&&customScenes&&!newSceneAPI)throw Error('Har bir sahna tavsifi uchun serverni 0.1.0 ga yangilash kerak. Hozir umumiy tavsifdan foydalan.');
 if(ai&&customScenes&&S.form.engine==='comfy_video')throw Error('Bu ComfyUI workflow umumiy tavsifdan foydalanadi. Sahna tavsiflari uchun Kling modelini tanla.');
 const body={kind:edit?'edit_video':S.form.engine,video_intent:edit?'edit':ai?'animation':'montage',prompt:composePrompt(S.form.prompt),ratio:S.form.ratio,quality:S.form.quality,duration:Number(S.form.duration),fps:Number(S.form.fps),motion:S.form.motion,filter:S.form.filter,trim_start:Number(S.form.trimStart),subtitles:cuesFromText(S.form.caption,Number(S.form.duration),S.refs.length),auto_text:ai&&S.form.engine==='fal_video'&&S.form.autoText,video_language:ai&&S.form.engine==='fal_video'?S.form.videoLanguage:'none'};
 if(edit){if(!S.video)throw Error('Video tanla.');body.video=await fileData(S.video.blob);}else{
  body.images=await Promise.all(S.refs.map(async r=>fileData(await croppedReference(r,ai?S.form.cropBottom:0))));
  if(ai&&newSceneAPI)body.scene_prompts=S.refs.map(r=>composePrompt(r.scenePrompt?.trim()||S.form.prompt));
  if(body.auto_text&&Number(S.form.cropBottom)>0){if(!newSceneAPI)throw Error('Matnni asl rasmdan o‘qib, kesilgan rasmni jonlantirish uchun serverni yangila.');body.analysis_images=await Promise.all(S.refs.map(r=>fileData(r.blob)));}
 }
 if(model?.legacy){body.kind=S.refs.length?'image_video':'text_video';body.duration=String(body.duration);}
 if(S.audio)body.audio=await fileData(S.audio.blob);
 return serverJob(body);
}
async function sendChat(){const input=$('chatInput'),message=input?.value.trim();if(!message||S.chatBusy)return;const historyRows=S.chat.filter(m=>m.role==='user'||m.role==='assistant').slice(-50);S.chat.push({role:'user',content:message});S.chatBusy=true;render();try{const route=S.form.chatModel==='agent'?'/agent':'/chat';const r=await api(route,{message,history:historyRows,model:S.form.chatModel,session_id:'studio-'+(await dbGet('meta','session')||'default'),allow_paid:S.form.paid});if(!r.reply)throw Error('AI javobi bo‘sh.');S.chat.push({role:'assistant',content:r.reply});}catch(e){S.chat.push({role:'error',content:e.message});}finally{S.chatBusy=false;await dbPut('meta',S.chat,'chat');if(S.page==='chat')render();}}
async function speak(save=false){const text=S.form.voiceText.trim();if(!text)throw Error('O‘qiladigan matnni yoz.');if(window.ShirinNative?.speak){window.ShirinNative.speak(text,S.form.voiceLanguage,Number(S.form.voiceRate),save);return;}if(save)throw Error('Bu brauzer ovozni faylga chiqara olmaydi.');if(!window.speechSynthesis)throw Error('Qurilmada ovoz o‘qish qo‘llanmaydi.');const voices=speechSynthesis.getVoices(),voice=voices.find(v=>v.lang.toLowerCase().startsWith(S.form.voiceLanguage.slice(0,2)));if(!voice)throw Error('Bu til ovozi qurilmada topilmadi. Telefon ovoz sozlamalaridan o‘rnat yoki boshqa til tanla.');speechSynthesis.cancel();const utterance=new SpeechSynthesisUtterance(text);utterance.voice=voice;utterance.lang=S.form.voiceLanguage;utterance.rate=Number(S.form.voiceRate);utterance.onerror=()=>toast('Ovoz o‘qilmadi. Qurilma TTS sozlamalarini tekshir.');speechSynthesis.speak(utterance);}
async function recordVoice(){if(S.recorder){S.recorder.stop();return;}if(!navigator.mediaDevices?.getUserMedia||!window.MediaRecorder)throw Error('Mikrofon yozuvi qo‘llanmaydi.');const stream=await navigator.mediaDevices.getUserMedia({audio:true}),mime=['audio/webm;codecs=opus','audio/mp4','audio/ogg;codecs=opus'].find(t=>MediaRecorder.isTypeSupported(t));S.mediaStream=stream;S.recordChunks=[];S.recorder=new MediaRecorder(stream,mime?{mimeType:mime}:{});S.recorder.ondataavailable=e=>{if(e.data.size)S.recordChunks.push(e.data);};S.recorder.onstop=async()=>{const type=S.recorder.mimeType.split(';')[0];S.recorder=null;S.mediaStream.getTracks().forEach(t=>t.stop());try{await saveArtifact(new Blob(S.recordChunks,{type}),'Shirin-ovoz-'+Date.now()+(type.includes('mp4')?'.m4a':type.includes('ogg')?'.ogg':'.webm'));if(S.page==='voice')render();}catch(e){toast(e.message);}};S.recorder.start();render();toast('Mikrofon yozmoqda. Tugatish tugmasini bos.');}
window.onNativeVoice=async function(data){try{if(data.error)throw Error(data.error);if(data.url){const response=await fetch(data.url);await saveArtifact(await response.blob(),'Shirin-ovoz-'+Date.now()+'.wav');if(S.page==='gallery')render();}else if(data.audio){await saveArtifact(blobFromData('data:audio/wav;base64,'+data.audio),'Shirin-ovoz-'+Date.now()+'.wav');if(S.page==='gallery')render();}else if(data.message)toast(data.message);}catch(e){toast(e.message);}};
window.onNativeDownload=function(message){toast(message);};
async function loadJobs(){const el=$('serverJobs');if(!el||!S.connected)return;try{const result=await api('/jobs');if(!$('serverJobs'))return;$('serverJobs').innerHTML=result.jobs.length?result.jobs.map(job=>`<article class="job"><div class="actions"><strong>${esc(({IN_QUEUE:'Navbatda',IN_PROGRESS:'Tayyorlanmoqda',COMPLETED:'Tayyor',FAILED:'Xato',CANCELLED:'Bekor qilingan',INTERRUPTED:'To‘xtagan'})[job.status]||job.status)}</strong><span class="tag">${esc(job.kind)}</span></div><p>${esc(job.error||job.prompt||'')}</p>${job.scenes?`<details><summary>O‘qilgan sahnalar</summary>${job.scenes.map((x,i)=>`<p><strong>${i+1}.</strong> ${esc(x.visible_text)}<br>${esc(x.narration)}</p>`).join('')}</details>`:''}${job.status==='IN_PROGRESS'?`<progress max="1" value="${job.progress||0}"></progress>`:''}<div class="actions">${job.url?`<button data-server-import="${esc(job.id)}">Galereyaga saqlash ↓</button>`:''}${['IN_QUEUE','IN_PROGRESS'].includes(job.status)?`<button data-server-cancel="${esc(job.id)}">Bekor qilish</button>`:''}</div></article>`).join(''):'<div class="empty">Serverda hali ish yo‘q.</div>';}catch(e){if($('serverJobs'))$('serverJobs').textContent=e.message;}}
async function exportProject(){const payload={format:'shirin-project',version:1,form:S.form,refs:await Promise.all(S.refs.map(async r=>({name:r.name,scenePrompt:r.scenePrompt||'',data:await fileData(r.blob)}))),audio:S.audio?{name:S.audio.name,data:await fileData(S.audio.blob)}:null};await download(new Blob([JSON.stringify(payload)],{type:'application/json'}),'Shirin-loyiha.json');}
async function uploadFile(input){const files=Array.from(input.files||[]),type=input.dataset.upload;if(!files.length)return;if(type==='connection'){try{return await importConnectionFile(files[0]);}finally{input.value='';}}if(type==='refs')return addRefs(files);if(type==='assets'){if(S.busy)throw Error('Eksport tugashini kut.');for(const file of files){if(!/^(image|video|audio)\//.test(file.type))throw Error('Rasm, video yoki ovoz faylini tanla.');await saveArtifact(file,file.name,'Telefondan');}S.filter='all';S.search='';render();return;}if(type==='project'){if(S.busy)throw Error('Eksport tugashini kut.');const value=JSON.parse(await files[0].text());if(value.format!=='shirin-project'||!Array.isArray(value.refs))throw Error('Bu Shirin loyiha fayli emas.');if(value.form){for(const key of ['duration','fps','quality','imageQuality','brightness','contrast','saturation','rotation','tolerance','voiceRate','trimStart','cropBottom']){if(key in value.form&&!Number.isFinite(Number(value.form[key])))throw Error('Loyiha sozlamasi noto‘g‘ri: '+key);}for(const key of ['ratio','imageRatio']){if(key in value.form&&!/^(9:16|16:9|1:1|4:3|3:4|21:9)$/.test(value.form[key]))throw Error('Loyiha nisbati noto‘g‘ri.');}if(value.form.keyColor&&!/^#[a-fA-F0-9]{6}$/.test(value.form.keyColor))throw Error('Fon rangi noto‘g‘ri.');}if(S.refs.length&&!confirm('Hozirgi qoralama loyiha nusxasi bilan almashtirilsinmi?'))return;S.refs=[];for(const key of Object.keys(S.form)){if(value.form&&key in value.form&&['string','number','boolean'].includes(typeof value.form[key]))S.form[key]=value.form[key];}await addRefs(value.refs.map(r=>new File([blobFromData(r.data)],r.name,{type:r.data.slice(5).split(';')[0]})));S.refs.forEach((r,i)=>{r.scenePrompt=String(value.refs[i]?.scenePrompt||'').slice(0,4000);});S.audio=value.audio?{name:value.audio.name,blob:blobFromData(value.audio.data)}:null;draft();render();return;}if(type==='srt'){S.form.caption=await files[0].text();draft();render();return;}S[type]={blob:files[0],name:files[0].name};draft();render();toast('Fayl qo‘shildi.');}
document.addEventListener('input',e=>{if(e.target.dataset.sceneId){const ref=S.refs.find(r=>r.id===e.target.dataset.sceneId);if(ref){ref.scenePrompt=e.target.value;draft();}return;}const p=e.target.dataset.prop;if(p){S.form[p]=e.target.type==='checkbox'?e.target.checked:e.target.value;draft();if(S.page==='image'&&['brightness','contrast','saturation','tolerance','keyColor'].includes(p))drawEditor().catch(x=>toast(x.message));}if(e.target.id==='gallerySearch'){S.search=e.target.value;const pos=e.target.selectionStart;render();$('gallerySearch').focus();if(pos!==null){try{$('gallerySearch').setSelectionRange(pos,pos);}catch{}}}});
document.addEventListener('change',e=>{if(e.target.dataset.upload)uploadFile(e.target).catch(x=>toast(x.message));const p=e.target.dataset.prop;if(p&&['engine','cropBottom','imageEngine','imageRatio','imageQuality','rotation','removeBackground','imageFormat'].includes(p))render();});
document.addEventListener('click',async e=>{const b=e.target.closest('button');if(!b)return;try{
 if(b.dataset.videoMode){if(S.busy)throw Error('Eksport tugashini kut.');S.form.engine=b.dataset.videoMode==='ai'?chooseVideoEngine():'browser';draft();render();return;}if(b.dataset.page){if(b.dataset.page==='edit'&&!['browser','montage'].includes(S.form.engine))S.form.engine='browser';return go(b.dataset.page);}
 if(b.dataset.ref!==undefined){if(S.busy)throw Error('Eksport tugashini kut.');const i=Number(b.dataset.ref),dir=Number(b.dataset.dir);if(!dir)S.refs.splice(i,1);else if(S.refs[i+dir])[S.refs[i],S.refs[i+dir]]=[S.refs[i+dir],S.refs[i]];draft();render();return;}
 if(b.dataset.template!==undefined){const t=TEMPLATES[Number(b.dataset.template)];S.form.prompt=t.prompt;S.form.imagePrompt=t.prompt;S.form.duration=15;S.form.ratio='9:16';draft();go('video');toast('Shablon tavsifga qo‘shildi. O‘z rasmlaringni tanla.');return;}
 if(b.dataset.chatPrompt){$('chatInput').value=b.dataset.chatPrompt;return sendChat();}
 if(b.dataset.filter){S.filter=b.dataset.filter;render();return;}
 if(b.dataset.phoneSave){const a=S.artifacts.find(a=>a.id===b.dataset.phoneSave);return download(a.blob,a.name,true);}
 if(b.dataset.download){const a=S.artifacts.find(a=>a.id===b.dataset.download);return download(a.blob,a.name);}
 if(b.dataset.delete){const a=S.artifacts.find(a=>a.id===b.dataset.delete);if(confirm('“'+a.name+'” galereyadan o‘chirilsinmi?')){await dbDelete(a.id);S.artifacts=S.artifacts.filter(r=>r.id!==a.id);render();}return;}
 if(b.dataset.rename){const a=S.artifacts.find(a=>a.id===b.dataset.rename),name=prompt('Yangi nom:',a.name);if(name?.trim()){a.name=name.trim();await dbPut('assets',a);render();}return;}
 if(b.dataset.use){const a=S.artifacts.find(a=>a.id===b.dataset.use);if(a.type.startsWith('image')){selectHF('seedance25-i2v');HF.files.image_url=[{name:a.name,blob:a.blob}];saveHF();go('studio');}else if(a.type.startsWith('video')){S.video={name:a.name,blob:a.blob};go('edit');}else{S.audio={name:a.name,blob:a.blob};go('montage');}draft();return;}
 if(b.dataset.serverImport){b.disabled=true;await importJob(await api('/jobs/'+b.dataset.serverImport));render();return;}
 if(b.dataset.serverCancel){await api('/jobs/'+b.dataset.serverCancel+'/cancel',{});await loadJobs();return;}
 switch(b.dataset.action){
 case 'video-setup':await draft();go('settings');$('serverBase')?.focus();break;
 case 'more-tools':sheet('Barcha vositalar','<div class="tool-menu">'+NAV.filter(([n])=>!['home','video','gallery'].includes(n)).map(([n,l])=>`<button data-page="${n}">${icon(n)} ${l}</button>`).join('')+'</div>');break;
 case 'close-sheet':closeSheet();break;
 case 'choose-saved-images':showSavedImages();break;
 case 'use-selected-images':{const ids=Array.from(document.querySelectorAll('[data-pick-asset]:checked'),e=>e.dataset.pickAsset);if(!ids.length)throw Error('Kamida bitta rasmni belgila.');const rows=ids.map(id=>S.artifacts.find(a=>a.id===id));closeSheet();await addRefs(rows.map(a=>new File([a.blob],a.name,{type:a.type})));break;}

 case 'connect':b.disabled=true;try{await connect();}finally{b.disabled=false;}break;
 case 'disconnect':S.connectAttempt++;S.connecting=false;S.settings.token='';S.connected=false;S.health=null;S.connectionError='';sessionStorage.removeItem('shirin-studio-token');localStorage.removeItem('shirin-studio-settings');window.ShirinNative?.saveSettings?.(JSON.stringify(S.settings));render();break;
 case 'render-video':S.videoError='';try{await createVideo(b.dataset.edit==='true');}catch(error){if(b.dataset.edit!=='true'&&!['browser','montage'].includes(S.form.engine)){S.videoError=error.message;if(S.page==='video')render();}throw error;}break;
 case 'remove-audio':S.audio=null;draft();render();break;
 case 'save-image':if(!S.refs[0])throw Error('Rasm tanla.');await drawEditor();{const c=$('imageCanvas');let target=c;if(S.form.imageFormat==='jpeg'){target=document.createElement('canvas');target.width=c.width;target.height=c.height;const x=target.getContext('2d');x.fillStyle='#fff';x.fillRect(0,0,c.width,c.height);x.drawImage(c,0,0);}const blob=await new Promise(r=>target.toBlob(r,'image/'+S.form.imageFormat,.93));await saveArtifact(blob,'Shirin-rasm-'+Date.now()+'.'+(S.form.imageFormat==='jpeg'?'jpg':'png'));go('gallery');}break;
 case 'generate-image':if(!S.form.imagePrompt.trim())throw Error('Rasm tavsifini yoz.');if(S.form.imageEngine==='fal_image'&&S.refs.length)throw Error('Bu model reference rasmni qabul qilmaydi. OpenAI yoki ComfyUI tanla.');await serverJob({kind:S.form.imageEngine,prompt:composePrompt(S.form.imagePrompt,false),ratio:S.form.imageRatio,quality:'720',images:await Promise.all(S.refs.map(r=>fileData(r.blob)))},S.form.imageEngine==='openai_image'?'/image':'/jobs');break;
 case 'send-chat':await sendChat();break;
 case 'new-chat':if(S.chat.length&&!confirm('Yangi suhbat ochilsinmi? Hozirgi suhbatni avval faylga saqlashing mumkin.'))return;S.chat=[];await dbPut('meta',[],'chat');render();break;
 case 'export-chat':await download(new Blob([S.chat.map(m=>m.role.toUpperCase()+'\n'+m.content).join('\n\n')],{type:'text/plain'}),'Shirin-suhbat.txt');break;
 case 'speak':await speak();break;
 case 'native-voice':await speak(true);break;
 case 'stop-speech':window.speechSynthesis?.cancel();window.ShirinNative?.stopSpeech?.();break;
 case 'record-voice':await recordVoice();break;
 case 'cloud-voice':await serverJob({kind:'voice',text:S.form.voiceText,language:S.form.voiceLanguage.slice(0,2),voice:'alloy'},'/voice');break;
 case 'refresh-jobs':await loadJobs();break;
 case 'persist-storage':toast(await navigator.storage?.persist?.()?'Doimiy saqlash ruxsati berildi.':'Brauzer doimiy saqlashni kafolatlamaydi. Muhim fayllarni yuklab ol.');break;
 case 'export-project':await exportProject();break;
 }
 }catch(error){toast(error.message||'Xatolik yuz berdi.');b.disabled=false;}});
document.addEventListener('click',e=>{if(e.target.matches('input[type=file]'))window.ShirinNative?.setImagePicker?.(e.target.dataset.picker||'gallery');},true);
$('cancelTask').onclick=()=>{S.cancel=true;if(S.localExport&&!S.localExport.signal.aborted)S.localExport.abort(new DOMException('Eksport bekor qilindi.','AbortError'));};
document.addEventListener('keydown',e=>{if(e.target.id==='chatInput'&&e.key==='Enter'&&!e.shiftKey){e.preventDefault();sendChat().catch(x=>toast(x.message));}});
window.addEventListener('beforeunload',e=>{if(S.busy||S.recorder){e.preventDefault();e.returnValue='';}});
(async()=>{try{S.db=await openDB();await loadHiggsfieldDraft();const saved=await dbGet('meta','draft');if(saved){S.refs=saved.refs||[];S.audio=saved.audio||null;S.video=saved.video||null;Object.assign(S.form,saved.form||{});S.form.paid=false;}if(!saved&&window.ShirinNative?.getLegacyDraft){try{const old=JSON.parse(window.ShirinNative.getLegacyDraft());S.form.prompt=old.prompt||'';const files=[];for(const name of old.files||[]){const r=await fetch('/legacy/'+encodeURIComponent(name));if(r.ok)files.push(new File([await r.blob()],name,{type:'image/jpeg'}));}if(files.length)await addRefs(files);await dbPut('meta',{refs:S.refs,audio:null,video:null,form:S.form},'draft');}catch{toast('Avvalgi qoralamani ko‘chirib bo‘lmadi. Rasmlarni qayta tanlashing mumkin.');}}if(!await dbGet('meta','ai-first-091')){S.form.engine='auto_ai';await dbPut('meta',true,'ai-first-091');}S.artifacts=await dbAll();S.chat=await dbGet('meta','chat')||[];if(!await dbGet('meta','session'))await dbPut('meta',id(),'session');const settings=localStorage.getItem('shirin-studio-settings');if(settings)Object.assign(S.settings,JSON.parse(settings));S.settings.token=sessionStorage.getItem('shirin-studio-token')||S.settings.token;if(window.ShirinNative?.getSettings){Object.assign(S.settings,JSON.parse(window.ShirinNative.getSettings()));}if(window.ShirinNative&&!S.settings.base)S.settings.base=DEFAULT_SHIRIN_SERVER;if(NAV.some(n=>n[0]===location.hash.slice(1)))S.page=location.hash.slice(1);if(S.page==='montage')S.form.engine='browser';else if(S.page!=='edit')S.form.engine='auto_ai';else if(!['browser','montage'].includes(S.form.engine))S.form.engine='browser';render();if((S.settings.token&&S.settings.base)||(!window.ShirinNative&&['localhost','127.0.0.1'].includes(location.hostname))){try{await connect();}catch{}}if('serviceWorker'in navigator&&!window.ShirinNative&&/^https?:$/.test(location.protocol))navigator.serviceWorker.register('./sw.js').catch(()=>{});}catch(e){$('view').innerHTML='<section class="panel"><h1>Saqlash ochilmadi</h1><p class="muted mt">Brauzerda sayt ma’lumotlarini saqlashga ruxsat berib qayta och.</p></section>';toast(e.message);}})();
