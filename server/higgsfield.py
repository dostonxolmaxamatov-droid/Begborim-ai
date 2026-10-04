"""Server-side Higgsfield REST adapter. No credentials are exposed to the client."""
import base64, hashlib, ipaddress, json, os, socket, time
from pathlib import Path
from urllib.parse import urlparse
from urllib.request import Request, build_opener, HTTPRedirectHandler
from urllib.error import HTTPError

API='https://api.higgsfield.ai'
CATALOG=json.loads(Path(__file__).with_name('hf-models.json').read_text())
MODELS={m['id']:m for m in CATALOG}
MAX_FILE=128*1024*1024
class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self,*args,**kwargs):raise ValueError('Xizmat boshqa manzilga yo‘naltirdi. So‘rov qayta yuborilmadi.')

def credentials():
    raw=os.environ.get('HF_KEY','').strip()
    if not raw:raw=':'.join([os.environ.get('HF_API_KEY_ID','').strip(),os.environ.get('HF_API_KEY_SECRET','').strip()])
    return raw if ':' in raw and all(raw.split(':',1)) and raw.isascii() and not any(c.isspace() for c in raw) else ''

def ready():return bool(credentials())

def public_url(url):
    p=urlparse(url)
    if p.scheme!='https' or not p.hostname or p.username or p.password or p.fragment or p.port not in (None,443):raise ValueError('Xizmat xavfsiz HTTPS media manzilini qaytarmadi.')
    try:
        addresses=socket.getaddrinfo(p.hostname,443,type=socket.SOCK_STREAM)
        if not addresses or any(not ipaddress.ip_address(a[4][0]).is_global for a in addresses):raise ValueError('Ichki tarmoq media manzili qabul qilinmadi.')
    except OSError:raise ValueError('Media server manzili topilmadi.') from None
    return url

def api_url(url):
    p=urlparse(url)
    if p.scheme!='https' or p.netloc!='api.higgsfield.ai' or p.username or p.password or p.fragment:raise ValueError('Higgsfield javobidagi API manzili noto‘g‘ri.')
    return url

def transport(url,body=None,headers=None,method=None,binary=False,limit=8*1024*1024):
    headers=dict(headers or {})
    if isinstance(body,dict):body=json.dumps(body,ensure_ascii=False).encode();headers['Content-Type']='application/json'
    try:
        with build_opener(NoRedirect).open(Request(url,data=body,headers=headers,method=method),timeout=90) as r:
            raw=r.read(limit+1)
            if len(raw)>limit:raise ValueError('Xizmat javobi ruxsat etilgan hajmdan katta.')
            if binary:return raw
            return json.loads(raw) if raw else {}
    except HTTPError as e:
        messages={401:'Higgsfield API kaliti qabul qilinmadi.',402:'Higgsfield API balansi yetarli emas.',403:'Bu modelga foydalanish ruxsati yo‘q.',404:'Model yoki so‘rov topilmadi.',422:'Model parametrlarni qabul qilmadi. Tavsif va fayllarni tekshir.',429:'Higgsfield so‘rov limiti. Keyinroq urinib ko‘r.'}
        raise ValueError(messages.get(e.code,'Higgsfield javobi: HTTP '+str(e.code)+'. Avtomatik qayta yuborilmadi.')) from None

def api(path,body=None,key=None):
    secret=credentials()
    if not secret:raise ValueError('Higgsfield ulanmagan: serverda HF_KEY kerak.')
    url=api_url(path if path.startswith('https:') else API+path)
    headers={'Authorization':'Key '+secret}
    if key:headers['Idempotency-Key']=key
    return transport(url,body,headers)

def upload(data):
    if not isinstance(data,str) or not data.startswith('data:') or ';base64,' not in data:raise ValueError('Telefon galereyasidan fayl tanla.')
    meta,encoded=data.split(',',1);mime=meta[5:].split(';')[0]
    if mime not in ('image/jpeg','image/png','image/webp','image/gif','video/mp4','audio/wav','audio/x-wav'):raise ValueError('Model uchun JPG, PNG, WebP, GIF, MP4 yoki WAV tanla.')
    try:raw=base64.b64decode(encoded,validate=True)
    except Exception:raise ValueError('Yuklangan fayl buzilgan.') from None
    if not raw or len(raw)>MAX_FILE:raise ValueError('Fayl 128 MB dan kichik bo‘lsin.')
    ticket=api('/files/generate-upload-url',{'content_type':mime})
    url=public_url(ticket['upload_url']);result=public_url(ticket['public_url'])
    headers=ticket.get('upload_headers',{'Content-Type':mime})
    if not isinstance(headers,dict) or any(not isinstance(k,str) or not (k.lower()=='content-type' or k.lower().startswith('x-amz-')) for k in headers):raise ValueError('Yuklash sarlavhalari tekshiruvdan o‘tmadi.')
    transport(url,raw,headers,method='PUT',binary=True,limit=1024*1024)
    return result

def validate(data):
    m=MODELS.get(data.get('hf_model'))
    if not m:raise ValueError('Higgsfield modelini tanla.')
    if data.get('kind')!='hf_'+m['type']:raise ValueError('Model va natija turi mos emas.')
    if data.get('allow_paid') is not True:raise ValueError('AI generatsiyasi pullik. Xarajatga rozilikni belgila.')
    params=data.get('hf_params',{})
    if not isinstance(params,dict) or set(params)-{f['key'] for f in m['fields']}:raise ValueError('Model parametrlari noto‘g‘ri.')
    result={}
    for f in m['fields']:
        k=f['key'];v=params.get(k,f.get('default'))
        if v is None or v=='':
            if f.get('required'):raise ValueError(f['label']+' kerak.')
            continue
        t=f['type']
        if t in ('image','video','images'):
            vals=v if t=='images' else [v]
            if not isinstance(vals,list) or not 1<=len(vals)<=f.get('max_items',1):raise ValueError(f['label']+' soni noto‘g‘ri.')
            prefix='data:video/mp4;base64,' if t=='video' else 'data:image/'
            if any(not isinstance(x,str) or not x.startswith(prefix) or len(x)>MAX_FILE*1.4 for x in vals):raise ValueError(f['label']+' formati noto‘g‘ri.')
        elif t=='number':
            if isinstance(v,bool) or not isinstance(v,(int,float)) or v!=v or not f.get('min',-1e9)<=v<=f.get('max',1e9) or (f.get('integer',True) and v!=int(v)):raise ValueError(f['label']+' qiymati noto‘g‘ri.')
        elif t=='boolean':
            if not isinstance(v,bool):raise ValueError(f['label']+' qiymati noto‘g‘ri.')
        else:
            if not isinstance(v,str) or len(v)>10000:raise ValueError(f['label']+' 10000 belgigacha bo‘lsin.')
        if f.get('options') and v not in f['options']:raise ValueError(f['label']+' tanlovi noto‘g‘ri.')
        result[k]=v
    return m,result

def generate(data,folder,progress,cancelled):
    m,params=validate(data)
    if not ready():raise ValueError('Higgsfield ulanmagan: serverda HF_KEY kerak.')
    if cancelled():raise InterruptedError('Bekor qilindi.')
    body=dict(params)
    for f in m['fields']:
        k=f['key']
        if k not in body:continue
        if f['type'] in ('image','video'):progress('Reference yuklanmoqda',.08);body[k]=upload(body[k])
        elif f['type']=='images':body[k]=[upload(v) for v in body[k]]
    if cancelled():raise InterruptedError('Generatsiya yuborilishidan oldin bekor qilindi.')
    progress('AI so‘rovi yuborilmoqda',.15)
    receipt=api('/'+m['endpoint'],body,key='shirin-'+data['id'])
    status_url=api_url(receipt.get('status_url',''))
    cancel_url=api_url(receipt.get('cancel_url',''))
    (Path(folder)/'hf-receipt.json').write_text(json.dumps({'request_id':receipt.get('request_id'),'status_url':status_url,'cancel_url':cancel_url,'idempotency_key':'shirin-'+data['id']}))
    started=time.monotonic();result=receipt
    while result.get('status') in ('queued','in_progress'):
        if cancelled():
            try:api(cancel_url,{})
            except ValueError:raise ValueError('AI ishlashni boshlagan; bekor qilish rad etildi. API konsolidan ishni tekshir.') from None
            raise InterruptedError('Navbatdagi so‘rov bekor qilindi.')
        if time.monotonic()-started>1800:raise ValueError('Kutish 30 daqiqadan oshdi. API konsolidan so‘rov holatini tekshir; qayta generatsiya avtomatik yuborilmadi.')
        progress('AI navbatida' if result['status']=='queued' else 'AI yaratmoqda',.3)
        time.sleep(3);result=api(status_url)
    if result.get('status')!='completed':raise ValueError({'failed':'AI generatsiyasi tugamadi.','nsfw':'Xizmat bu so‘rovni qabul qilmadi.','canceled':'AI so‘rovi bekor qilindi.'}.get(result.get('status'),'AI noma’lum holat qaytardi.'))
    if m['type']=='video':items=[result.get('video',{})];default='video/mp4';ext='mp4'
    else:items=result.get('images',[]);default='image/png';ext='png'
    if not items or not isinstance(items[0],dict) or not items[0].get('url'):raise ValueError('AI kutilgan turdagi natijani qaytarmadi.')
    # One output per request in this build. The UI never requests a multi-image batch.
    url=public_url(items[0]['url']);raw=transport(url,binary=True,limit=512*1024*1024)
    if m['type']=='image':
        if raw.startswith(b'\x89PNG\r\n\x1a\n'):default,ext='image/png','png'
        elif raw.startswith(b'\xff\xd8\xff'):default,ext='image/jpeg','jpg'
        elif raw[:4]==b'RIFF' and raw[8:12]==b'WEBP':default,ext='image/webp','webp'
        else:raise ValueError('AI natijasi rasm fayli emas.')
    elif len(raw)<12 or raw[4:8]!=b'ftyp':raise ValueError('AI natijasi MP4 video emas.')
    path=Path(folder)/('result.'+ext);path.write_bytes(raw);progress('Natija saqlanmoqda',.95)
    return path,default
