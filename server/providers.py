"""Explicit, configurable adapters. Keys never enter browser or APK assets."""
import base64, copy, json, os, re, secrets, time
from pathlib import Path
from urllib.request import Request, build_opener, HTTPRedirectHandler
from urllib.parse import urlparse, urlencode
from urllib.error import HTTPError
import studio_media, storyboard

class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self,*args,**kwargs):raise ValueError('Xizmat kutilmagan manzilga yo‘naltirdi.')

def request(url,data=None,headers=None,raw=False,timeout=180):
    h=dict(headers or {})
    if isinstance(data,(dict,list)):
        data=json.dumps(data).encode();h['Content-Type']='application/json'
    try:
        with build_opener(NoRedirect).open(Request(url,data=data,headers=h),timeout=timeout) as r:
            body=r.read(256*1024*1024)
            return body if raw else json.loads(body)
    except HTTPError as e:
        message={401:'Xizmat kaliti qabul qilinmadi.',402:'Xizmat balansi yetarli emas.',429:'Xizmatning vaqtinchalik limiti tugadi. Keyinroq urinib ko‘ring.'}.get(e.code,'AI xizmati so‘rovni bajarmadi (HTTP '+str(e.code)+').')
        raise ValueError(message) from None

def configured(name):return bool(os.environ.get(name,'').strip())

VIDEO_CONFIG={'fal_video':('FAL_KEY',),'comfy_video':('COMFYUI_URL','COMFYUI_VIDEO_WORKFLOW')}

def video_setup():
    missing={kind:[name for name in names if not configured(name)] for kind,names in VIDEO_CONFIG.items()}
    ready=[kind for kind,names in missing.items() if not names]
    return {'state':'configured' if ready else 'unconfigured','configured_providers':ready,'missing_by_provider':missing,'account_verified':False}

def require_video_config(kind):
    missing=video_setup()['missing_by_provider'].get(kind,[])
    if missing:raise ValueError('AI video ulanmagan. Server sozlamalarida '+', '.join(missing)+' kerak. Rasmlar montajga almashtirilmadi.')
def openai(path,data=None,raw=False,content_type=None):
    key=os.environ.get('OPENAI_API_KEY','')
    if not key:raise ValueError('OpenAI ulanmagan.')
    headers={'Authorization':'Bearer '+key}
    if content_type:headers['Content-Type']=content_type
    return request('https://api.openai.com/v1/'+path,data,headers,raw)

def multipart(fields,files):
    boundary='Shirin'+secrets.token_hex(16);body=bytearray()
    for key,value in fields.items():
        body.extend(f'--{boundary}\r\nContent-Disposition: form-data; name="{key}"\r\n\r\n{value}\r\n'.encode())
    for key,name,mime,content in files:
        body.extend(f'--{boundary}\r\nContent-Disposition: form-data; name="{key}"; filename="{name}"\r\nContent-Type: {mime}\r\n\r\n'.encode());body.extend(content);body.extend(b'\r\n')
    body.extend(f'--{boundary}--\r\n'.encode());return bytes(body),'multipart/form-data; boundary='+boundary

def catalog():
    chat=[]
    if configured('OLLAMA_URL'):
        try:
            rows=request(os.environ['OLLAMA_URL'].rstrip('/')+'/api/tags',timeout=8).get('models',[])
            chat += [{'id':'ollama:'+r['name'],'name':r['name'],'provider':'ollama','paid':False,'ready':True} for r in rows]
        except Exception:pass
    if configured('OPENAI_API_KEY'):
        models=os.environ.get('OPENAI_CHAT_MODELS',os.environ.get('OPENAI_CHAT_MODEL','gpt-6-astra')).split(',')
        chat += [{'id':'openai:'+m.strip(),'name':m.strip(),'provider':'openai','paid':True,'ready':True} for m in models if m.strip()]
    return {'chat':chat,'image':[
        {'id':'comfy_image','name':'ComfyUI · mahalliy','ready':configured('COMFYUI_URL') and configured('COMFYUI_IMAGE_WORKFLOW'),'paid':False},
        {'id':'openai_image','name':os.environ.get('OPENAI_IMAGE_MODEL','gpt-image-2'),'ready':configured('OPENAI_API_KEY'),'paid':True},
        {'id':'fal_image','name':'FLUX.1 schnell','ready':configured('FAL_KEY'),'paid':True}],
      'video':[
        {'id':'montage','name':'Bepul montaj · MP4','ready':bool(__import__('shutil').which('ffmpeg')),'paid':False},
        {'id':'comfy_video','name':'ComfyUI · mahalliy','ready':configured('COMFYUI_URL') and configured('COMFYUI_VIDEO_WORKFLOW'),'paid':False},
        {'id':'fal_video','name':'Kling 2.5 Turbo Pro','ready':configured('FAL_KEY'),'paid':True}],
      'voice':{'openai':configured('OPENAI_API_KEY'),'azure':configured('AZURE_SPEECH_KEY') and configured('AZURE_SPEECH_REGION')},
      'vision':storyboard.vision_ready(),'narration':storyboard.voice_ready(),'agent':configured('N8N_WEBHOOK_URL')}

def require_paid(data):
    if data.get('allow_paid') is not True:raise ValueError('Bepul rejim yoqilgan. Bu xizmat alohida to‘lov talab qiladi.')

def chat(data):
    text=str(data.get('message','')).strip()
    if not text or len(text)>32000:raise ValueError('Xabar 1–32000 belgi bo‘lsin.')
    rows=catalog()['chat'];selected=data.get('model','auto')
    if selected=='auto':selected=next((r['id'] for r in rows if not r['paid']),rows[0]['id'] if rows else '')
    row=next((r for r in rows if r['id']==selected),None)
    if not row:raise ValueError('AI chat ulanmagan. Sozlamalarda xizmat holatini tekshir.')
    if row['paid']:require_paid(data)
    history=data.get('history',[])
    if not isinstance(history,list) or len(history)>100:raise ValueError('Suhbat hajmi katta. Yangi suhbat oching.')
    messages=[{'role':'system','content':'You are Shirin AI, a helpful creative assistant. Reply in the user language, usually Uzbek. Never claim to have generated or sent a file unless a tool actually did it.'}]
    for m in history:
        if isinstance(m,dict) and m.get('role') in ('user','assistant') and isinstance(m.get('content'),str):messages.append({'role':m['role'],'content':m['content'][:32000]})
    messages.append({'role':'user','content':text})
    if row['provider']=='ollama':
        result=request(os.environ['OLLAMA_URL'].rstrip('/')+'/api/chat',{'model':row['name'],'messages':messages,'stream':False})
        reply=result.get('message',{}).get('content','')
    else:
        result=openai('responses',{'model':row['name'],'input':messages,'store':False})
        reply='\n'.join(c.get('text','') for item in result.get('output',[]) for c in item.get('content',[]) if c.get('type')=='output_text')
    if not reply:raise ValueError('AI bo‘sh javob qaytardi.')
    return {'reply':reply,'model':row['name']}

def agent(data):
    url=os.environ.get('N8N_WEBHOOK_URL','')
    if not url or urlparse(url).scheme!='https':raise ValueError('n8n agenti serverda ulanmagan.')
    headers={}
    if configured('N8N_WEBHOOK_TOKEN'):headers['Authorization']='Bearer '+os.environ['N8N_WEBHOOK_TOKEN']
    message=str(data.get('message','')).strip()
    if not message or len(message)>32000:raise ValueError('Agent uchun xabar yozing.')
    result=request(url,{'chatInput':message,'message':message,'sessionId':str(data.get('session_id','shirin'))[:100]},headers)
    if isinstance(result,list):result=result[0] if result else {}
    reply=result.get('output') or result.get('reply') or result.get('text')
    if not isinstance(reply,str):raise ValueError('n8n javobida output yoki reply matni yo‘q.')
    return {'reply':reply,'model':'n8n agent'}

def image(data,folder):
    require_paid(data);prompt=str(data.get('prompt','')).strip()
    if not prompt:raise ValueError('Rasm tavsifini yozing.')
    model=os.environ.get('OPENAI_IMAGE_MODEL','gpt-image-2')
    size={'1:1':'1024x1024','9:16':'1024x1536','16:9':'1536x1024'}.get(data.get('ratio'),'1024x1024')
    fields={'model':model,'prompt':prompt,'size':size,'quality':data.get('quality','medium') if data.get('quality') in ('low','medium','high','auto') else 'medium','n':1}
    images=data.get('images',[])
    if len(images)>16:raise ValueError('OpenAI edit uchun 16 tagacha reference rasm tanlang.')
    if images:
        files=[]
        for i,value in enumerate(images):
            p=Path(folder)/f'reference-{i}.img';mime=studio_media.decode_file(value,p,16*1024*1024,True)
            ext={'image/png':'png','image/jpeg':'jpg','image/webp':'webp'}.get(mime,'png')
            files.append(('image[]',f'reference-{i}.{ext}',mime,p.read_bytes()))
        body,mime=multipart(fields,files);result=openai('images/edits',body,content_type=mime)
    else:result=openai('images/generations',fields)
    encoded=(result.get('data') or [{}])[0].get('b64_json')
    if not encoded:raise ValueError('Rasm natijasi olinmadi.')
    p=Path(folder)/'result.png';p.write_bytes(base64.b64decode(encoded,validate=True));return p,'image/png'

def voice(data,folder):
    require_paid(data);text=str(data.get('text','')).strip()
    if not text or len(text)>4000:raise ValueError('Ovoz matni 1–4000 belgi bo‘lsin.')
    if data.get('language')=='uz' and configured('AZURE_SPEECH_KEY') and configured('AZURE_SPEECH_REGION'):
        import html
        region=os.environ['AZURE_SPEECH_REGION']
        if not re.fullmatch('[a-z0-9-]+',region):raise ValueError('Ovoz hududi noto‘g‘ri.')
        body=('<speak version="1.0" xml:lang="uz-UZ"><voice name="uz-UZ-MadinaNeural">'+html.escape(text)+'</voice></speak>').encode()
        content=request('https://'+region+'.tts.speech.microsoft.com/cognitiveservices/v1',body,{'Ocp-Apim-Subscription-Key':os.environ['AZURE_SPEECH_KEY'],'Content-Type':'application/ssml+xml','X-Microsoft-OutputFormat':'audio-24khz-48kbitrate-mono-mp3'},True)
    else:
        name=data.get('voice','alloy')
        if name not in ('alloy','ash','coral','echo','fable','nova','onyx','sage','shimmer'):name='alloy'
        content=openai('audio/speech',{'model':os.environ.get('OPENAI_TTS_MODEL','gpt-4o-mini-tts'),'input':text,'voice':name,'response_format':'mp3'},True)
    p=Path(folder)/'result.mp3';p.write_bytes(content);return p,'audio/mpeg'

def fal_json(path,data=None):
    if not configured('FAL_KEY'):raise ValueError('Video AI xizmati ulanmagan.')
    if path.startswith('https://'):
        if urlparse(path).netloc!='queue.fal.run':raise ValueError('AI javob manzili noto‘g‘ri.')
        url=path
    else:url='https://queue.fal.run/'+path
    return request(url,data,{'Authorization':'Key '+os.environ['FAL_KEY']})

def fal_wait(path,payload,cancelled):
    result=fal_json(path,payload);deadline=time.monotonic()+3600
    while time.monotonic()<deadline:
        if cancelled():raise InterruptedError('Kutilayotgan ish bekor qilindi; yuborilgan AI so‘rovi provayderda davom etishi mumkin.')
        status=fal_json(result['status_url'])
        if status.get('status')=='COMPLETED':return fal_json(result['response_url'])
        if status.get('error') or status.get('status') in ('FAILED','CANCELLED'):raise ValueError('AI generatsiyasi bajarilmadi.')
        time.sleep(3)
    raise ValueError('AI javobi kechikdi. Yangi so‘rovdan oldin provayder tarixini tekshiring.')

def provider_media(url,target):
    p=urlparse(url);host=p.hostname or ''
    if p.scheme!='https' or not (host=='fal.media' or host.endswith('.fal.media') or host=='storage.googleapis.com'):raise ValueError('Natija manbasi ruxsat etilmagan.')
    target.write_bytes(request(url,raw=True));return target

def fal_image(data,folder,cancelled):
    require_paid(data)
    result=fal_wait('fal-ai/flux/schnell',{'prompt':data['prompt'],'image_size':{'9:16':'portrait_16_9','16:9':'landscape_16_9'}.get(data.get('ratio'),'square_hd'),'num_images':1,'enable_safety_checker':True},cancelled)
    return provider_media(result['images'][0]['url'],Path(folder)/'result.jpg'),'image/jpeg'

def fal_video(data,folder,progress,cancelled):
    require_paid(data)
    import montage
    folder=Path(folder);imgs=data.get('images',[]);duration=float(data.get('duration',15))
    prompts=data.get('scene_prompts') or []
    analysis=data.get('analysis_images') or imgs
    def scene_prompt(index):return prompts[index].strip() if index<len(prompts) and prompts[index].strip() else str(data.get('prompt',''))
    scene_count=max(1,len(imgs));copies=math_ceil(duration/scene_count/10)
    count=scene_count*copies;total=round(duration*30)
    if count>total:raise ValueError('Rasmlar soni ko‘p. Davomiylikni uzaytiring.')
    steps=[{'frames':total//count+(i<total%count),'image_index':i//copies} for i in range(count)]
    for step in steps:step['duration']='5' if step['frames']<=150 else '10'
    language=data.get('video_language','none');scenes=None;audio=None
    if data.get('auto_text') or language!='none':
        scenes=[]
        for i in range(scene_count):
            if cancelled():raise InterruptedError('Bekor qilindi.')
            progress(f'Sahna matni {i+1}/{scene_count}',.05)
            seconds=sum(step['frames'] for step in steps if step['image_index']==i)/30
            scenes.append(storyboard.read_scene(analysis[i] if analysis else None,scene_prompt(i),language,seconds,bool(data.get('auto_text'))))
        (folder/'scene-review.json').write_text(json.dumps(scenes,ensure_ascii=False),encoding='utf-8')
        if language!='none':
            progress('Hikoyachi ovozi tayyorlanmoqda',.1)
            audio=storyboard.prepare_audio(scenes,steps,folder,language)
    clips=[]
    for i,step in enumerate(steps):
        if cancelled():raise InterruptedError('Bekor qilindi.')
        index=step['image_index']
        payload={'prompt':scenes[index]['action_prompt'] if scenes else scene_prompt(index),'duration':step['duration']}
        if imgs:payload['image_url']=imgs[index]
        else:payload['aspect_ratio']=data.get('ratio','9:16')
        endpoint='fal-ai/kling-video/v2.5-turbo/pro/'+('image-to-video' if imgs else 'text-to-video')
        progress(f'AI lavha {i+1}/{count}',.15+i/count*.65)
        result=fal_wait(endpoint,payload,cancelled)
        clips.append(provider_media(result['video']['url'],folder/f'clip-{i}.mp4'))
    output=montage.assemble(clips,steps,folder,data.get('ratio','9:16'))
    if audio:storyboard.mux_voice(output,audio,duration,language)
    # Apply the selected export dimensions, frame rate, captions and optional soundtrack.
    source=folder/'generated-source.mp4';output.replace(source)
    return studio_media.render({**data,'trim_start':0,'images':[]},folder,progress,cancelled,source_video=source)

def math_ceil(v):return __import__('math').ceil(v)

def comfy(data,folder,progress,cancelled):
    kind=data['kind'];base=os.environ.get('COMFYUI_URL','').rstrip('/')
    path=os.environ.get('COMFYUI_VIDEO_WORKFLOW' if kind=='comfy_video' else 'COMFYUI_IMAGE_WORKFLOW','')
    if not base or not path:raise ValueError('Mahalliy AI va uning workflow fayli ulanmagan.')
    workflow=json.loads(Path(path).read_text());w,h=studio_media.dimensions(data.get('ratio'),data.get('quality','720'))
    values={'prompt':str(data.get('prompt','')),'width':w,'height':h,'seed':secrets.randbelow(2**31),'frames':int(float(data.get('duration',15))*int(data.get('fps',30))),'fps':int(data.get('fps',30))}
    for i,value in enumerate(data.get('images',[])):
        src=Path(folder)/f'reference-{i}.png';mime=studio_media.decode_file(value,src,16*1024*1024,True)
        body,ct=multipart({'overwrite':'false'},[('image',secrets.token_hex(8)+'.png',mime,src.read_bytes())])
        result=request(base+'/upload/image',body,{'Content-Type':ct});values['image_'+str(i)]=result['name']
    def replace(obj):
        if isinstance(obj,dict):return {k:replace(v) for k,v in obj.items()}
        if isinstance(obj,list):return [replace(v) for v in obj]
        if isinstance(obj,str):
            for k,v in values.items():
                token='${'+k+'}'
                if obj==token:return v
                obj=obj.replace(token,str(v))
        return obj
    result=request(base+'/prompt',{'prompt':replace(workflow),'client_id':secrets.token_hex(16)})
    if not result.get('prompt_id') or result.get('node_errors'):raise ValueError('ComfyUI workflow qabul qilinmadi. Modellar va tugunlarni tekshiring.')
    pid=result['prompt_id'];deadline=time.monotonic()+3600
    while time.monotonic()<deadline:
        if cancelled():raise InterruptedError('Kutilayotgan ish bekor qilindi. ComfyUI navbatini ham tekshiring.')
        history=request(base+'/history/'+pid).get(pid,{})
        if history.get('status',{}).get('status_str')=='error':raise ValueError('Mahalliy AI generatsiyasi bajarilmadi.')
        outputs=history.get('outputs',{})
        for output in outputs.values():
            for group in ('videos','gifs','images'):
                for item in output.get(group,[]):
                    if item.get('type')!='output':continue
                    ext=Path(item.get('filename','')).suffix.lower()
                    allowed=('.mp4','.webm','.gif') if kind=='comfy_video' else ('.png','.jpg','.jpeg','.webp')
                    if ext not in allowed:continue
                    p=Path(folder)/('result'+ext);p.write_bytes(request(base+'/view?'+urlencode({k:item[k] for k in ('filename','subfolder','type') if k in item}),raw=True))
                    return p,__import__('mimetypes').guess_type(p.name)[0] or 'application/octet-stream'
        time.sleep(2);progress('Mahalliy AI ishlayapti',.3)
    raise ValueError('Mahalliy AI javobi kechikdi.')
