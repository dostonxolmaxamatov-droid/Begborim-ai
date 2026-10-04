"""Shirin AI Studio 0.1.0. One-owner service with optional AI adapters."""
import base64, binascii, concurrent.futures, hmac, json, mimetypes, os, re, secrets, shutil, sqlite3, threading, time
from pathlib import Path
from http.server import BaseHTTPRequestHandler,ThreadingHTTPServer
from urllib.parse import urlparse,parse_qs
import providers, studio_media, storyboard, higgsfield

VERSION='0.1.0'
ROOT=Path(__file__).parent
DB=os.environ.get('SHIRIN_DB','shirin.sqlite3')
MEDIA=Path(os.environ.get('SHIRIN_MEDIA','shirin-media')).resolve()
TOKEN=os.environ.get('SHIRIN_TOKEN','')
BIND=os.environ.get('BIND','127.0.0.1')
PUBLIC=(os.environ.get('PUBLIC_BASE_URL') or ('https://'+os.environ['RAILWAY_PUBLIC_DOMAIN'] if os.environ.get('RAILWAY_PUBLIC_DOMAIN') else '')).rstrip('/')
MAX_IMAGES=int(os.environ.get('SHIRIN_MAX_IMAGES','100'))
MAX_SECONDS=int(os.environ.get('SHIRIN_MAX_SECONDS','600'))
WORKERS=concurrent.futures.ThreadPoolExecutor(max_workers=int(os.environ.get('SHIRIN_WORKERS','2')))
LOCK=threading.RLock();CANCEL={}
ORIGINS={'https://appassets.androidplatform.net'}|set(filter(None,os.environ.get('SHIRIN_ORIGINS','').split(',')))
KINDS={'montage','edit_video','openai_image','fal_image','fal_video','comfy_image','comfy_video','voice','hf_image','hf_video'}

def init_db():
    Path(DB).parent.mkdir(parents=True,exist_ok=True);MEDIA.mkdir(parents=True,exist_ok=True)
    with sqlite3.connect(DB) as db:
        db.execute('PRAGMA journal_mode=WAL');db.execute('CREATE TABLE IF NOT EXISTS jobs (id TEXT PRIMARY KEY,payload TEXT NOT NULL)')
        for jid,raw in db.execute('SELECT id,payload FROM jobs').fetchall():
            job=json.loads(raw)
            if job.get('release') in ('0.9.0','0.9.1','0.9.2',VERSION) and job.get('status') in ('IN_QUEUE','IN_PROGRESS'):
                job.update(status='INTERRUPTED',error='Server qayta ishga tushdi. Ish avtomatik qayta yuborilmadi.')
                db.execute('UPDATE jobs SET payload=? WHERE id=?',(json.dumps(job),jid))

def save(job):
    with LOCK,sqlite3.connect(DB) as db:db.execute('INSERT OR REPLACE INTO jobs VALUES (?,?)',(job['id'],json.dumps(job,ensure_ascii=False)))

def get_job(jid):
    with sqlite3.connect(DB) as db:
        row=db.execute('SELECT payload FROM jobs WHERE id=?',(jid,)).fetchone();return json.loads(row[0]) if row else None

def public(job):return {k:v for k,v in job.items() if k not in ('media_token','status_url','response_url','output_file','inputs')}

def validated(data):
    if not isinstance(data,dict):raise ValueError('So‘rov JSON obyekt bo‘lishi kerak.')
    data=dict(data);kind=data.get('kind')
    if kind in ('image_video','text_video'):kind='fal_video'
    elif kind=='image':kind='openai_image' if providers.configured('OPENAI_API_KEY') else 'fal_image'
    data['kind']=kind
    if kind not in KINDS:raise ValueError('Yaratish turi noto‘g‘ri.')
    intent=data.get('video_intent')
    if intent not in (None,'animation','montage','edit'):raise ValueError('Video rejimi noto‘g‘ri.')
    if intent=='animation' and kind not in ('fal_video','comfy_video','hf_video'):raise ValueError('AI jonlantirish so‘rovi faqat AI video modeliga yuboriladi. Montajga almashtirish mumkin emas.')
    if intent=='montage' and kind!='montage':raise ValueError('Montaj so‘rovi AI modeliga yuborilmadi.')
    if intent=='edit' and kind!='edit_video':raise ValueError('Video tahrirlash turi noto‘g‘ri.')
    jid=data.setdefault('id',secrets.token_hex(16))
    if not isinstance(jid,str) or not re.fullmatch('[a-zA-Z0-9-]{16,64}',jid):raise ValueError('Ish raqami noto‘g‘ri.')
    if kind.startswith('hf_'):
        higgsfield.validate(data)
        return data
    imgs=data.get('images',[])
    if not isinstance(imgs,list) or len(imgs)>MAX_IMAGES:raise ValueError(f'Server bir ishda {MAX_IMAGES} tagacha rasm qabul qiladi.')
    prompts=data.get('scene_prompts',[])
    if not isinstance(prompts,list) or (prompts and len(prompts)!=len(imgs)) or any(not isinstance(p,str) or len(p)>4000 for p in prompts):raise ValueError('Har bir rasmga bittadan, 4000 belgigacha sahna tavsifi kerak.')
    analysis=data.get('analysis_images',[])
    if not isinstance(analysis,list) or (analysis and (len(analysis)!=len(imgs) or kind!='fal_video' or not data.get('auto_text'))):raise ValueError('Asl rasmlar faqat sahna matnini o‘qish uchun va jonlantirish rasmlari bilan bir tartibda yuboriladi.')
    for value in analysis:
        if not isinstance(value,str) or not re.match(r'^data:image/(png|jpeg|webp);base64,',value):raise ValueError('Matn o‘qiladigan rasm formati noto‘g‘ri.')
        try:raw=base64.b64decode(value.split(',',1)[1],validate=True)
        except (binascii.Error,ValueError):raise ValueError('Matn o‘qiladigan rasm buzilgan.') from None
        if not raw or len(raw)>16*1024*1024:raise ValueError('Matn o‘qiladigan rasm 16 MB dan kichik bo‘lsin.')
    if data.get('ratio','9:16') not in studio_media.RATIOS:raise ValueError('Nisbat noto‘g‘ri.')
    if kind in ('montage','edit_video','fal_video','comfy_video'):
        sec=float(data.get('duration',15))
        if not 1<=sec<=MAX_SECONDS:raise ValueError(f'Davomiylik 1–{MAX_SECONDS} soniya bo‘lsin.')
    if kind=='fal_video' and data.get('ratio','9:16') not in ('9:16','16:9','1:1'):raise ValueError('Bu AI video modeli uchun 9:16, 16:9 yoki 1:1 tanlang.')
    if kind in ('openai_image','fal_image','fal_video','voice'):providers.require_paid(data)
    if data.get('auto_text') and (kind!='fal_video' or not imgs or not storyboard.vision_ready()):raise ValueError('Rasm matnini o‘qish uchun rasmlar va Gemini vision ulanishi kerak.')
    language=data.get('video_language','none')
    if language not in ('none','uz','en'):raise ValueError('Ovoz tili noto‘g‘ri.')
    if language!='none':
        if kind!='fal_video' or not storyboard.vision_ready() or not storyboard.voice_ready():raise ValueError('Hikoyachi uchun Gemini va Azure Speech ulanishi kerak.')
        if data.get('audio'):raise ValueError('Hikoyachi ovozi yoki yuklangan audiodan birini tanlang.')
    if kind not in ('montage','edit_video','voice') and not data.get('auto_text') and not str(data.get('prompt','')).strip() and not (kind=='fal_video' and prompts and all(p.strip() for p in prompts)):raise ValueError('Tavsif yozing.')
    if kind=='openai_image' and len(imgs)>16:raise ValueError('OpenAI edit uchun 16 tagacha reference rasm tanlang.')
    return data

def execute(job,data):
    folder=MEDIA/job['id'];event=CANCEL[job['id']]
    try:
        if event.is_set():raise InterruptedError('Bekor qilindi.')
        folder.mkdir(exist_ok=True);job.update(status='IN_PROGRESS');save(job)
        def progress(stage,value):
            job.update(stage=stage,progress=value);save(job)
        kind=data['kind']
        if kind in ('montage','edit_video'):output,mime=studio_media.render(data,folder,progress,event.is_set)
        elif kind.startswith('hf_'):output,mime=higgsfield.generate(data,folder,progress,event.is_set)
        elif kind=='openai_image':output,mime=providers.image(data,folder)
        elif kind=='fal_image':output,mime=providers.fal_image(data,folder,event.is_set)
        elif kind=='fal_video':output,mime=providers.fal_video(data,folder,progress,event.is_set)
        elif kind.startswith('comfy_'):output,mime=providers.comfy(data,folder,progress,event.is_set)
        else:output,mime=providers.voice(data,folder)
        if event.is_set():raise InterruptedError('Bekor qilindi.')
        review=folder/'scene-review.json'
        if review.is_file():job['scenes']=json.loads(review.read_text())
        token=secrets.token_urlsafe(24)
        job.update(status='COMPLETED',progress=1,stage='Tayyor',output_file=output.name,mime=mime,media_token=token,url=PUBLIC+'/media/'+job['id']+'/'+token)
    except InterruptedError as e:job.update(status='CANCELLED',error=str(e))
    except Exception as e:
        message=str(e) if isinstance(e,ValueError) else 'Xizmat bilan aloqa uzildi yoki faylni qayta ishlash tugamadi. Holatni tekshirib qayta urinib ko‘ring.'
        job.update(status='FAILED',error=message[:900])
    finally:
        save(job)
        if folder.exists():
            for p in folder.iterdir():
                if p.is_file() and p.name not in (job.get('output_file'),'hf-receipt.json'):p.unlink(missing_ok=True)
        CANCEL.pop(job['id'],None)

def submit(data):
    data=validated(data)
    with LOCK:
        old=get_job(data['id'])
        if old:return old
        if data['kind'].startswith('hf_') and not higgsfield.ready():raise ValueError('Higgsfield ulanmagan. Serverda HF_KEY kerak; generatsiya boshlanmadi.')
        providers.require_video_config(data['kind'])
        job={'id':data['id'],'kind':data['kind'],'prompt':str(data.get('prompt') or data.get('text') or 'Bepul montaj')[:4000],'created':time.time(),'status':'IN_QUEUE','progress':0,'release':VERSION}
        if data.get('video_intent'):job['video_intent']=data['video_intent']
        save(job);CANCEL[job['id']]=threading.Event();WORKERS.submit(execute,job.copy(),data)
        return job

class Handler(BaseHTTPRequestHandler):
    def log_message(self,*a):pass
    def cors(self):
        origin=self.headers.get('Origin','')
        if origin in ORIGINS:self.send_header('Access-Control-Allow-Origin',origin);self.send_header('Vary','Origin')
    def send(self,code,data):
        body=json.dumps(data,ensure_ascii=False).encode();self.send_response(code);self.cors()
        for k,v in {'Content-Type':'application/json; charset=utf-8','Content-Length':str(len(body)),'Cache-Control':'no-store','X-Content-Type-Options':'nosniff'}.items():self.send_header(k,v)
        self.end_headers();self.wfile.write(body)
    def auth(self):
        value=self.headers.get('Authorization','')
        local=not TOKEN and BIND in ('127.0.0.1','::1') and self.client_address[0] in ('127.0.0.1','::1')
        if local or (TOKEN and value.isascii() and hmac.compare_digest(value,'Bearer '+TOKEN)):return True
        self.send(401,{'error':'Ulanish kodi noto‘g‘ri. Sozlamalarda server va kodni tekshir.'});return False
    def do_OPTIONS(self):
        if self.headers.get('Origin') not in ORIGINS:return self.send(403,{'error':'Origin not allowed'})
        self.send_response(204);self.cors();self.send_header('Access-Control-Allow-Methods','GET, POST, OPTIONS');self.send_header('Access-Control-Allow-Headers','Authorization, Content-Type');self.send_header('Access-Control-Max-Age','600');self.end_headers()
    def do_GET(self):
        parsed=urlparse(self.path);path=parsed.path
        assets={'/':'index.html','/index.html':'index.html','/web.js':'web.js','/web.css':'web.css','/manifest.webmanifest':'manifest.webmanifest','/sw.js':'sw.js','/icon.svg':'icon.svg','/shirin.js':'shirin.js','/shirin.css':'shirin.css','/hf-models.js':'hf-models.js'}
        if path in assets:
            file=ROOT/assets[path]
            if not file.exists():return self.send(404,{'error':'Topilmadi.'})
            body=file.read_bytes();self.send_response(200)
            self.send_header('Content-Type',mimetypes.guess_type(file.name)[0] or 'application/octet-stream');self.send_header('Content-Length',str(len(body)));self.send_header('Cache-Control','no-cache');self.send_header('X-Content-Type-Options','nosniff');self.send_header('Referrer-Policy','no-referrer');self.send_header('X-Frame-Options','DENY')
            self.send_header('Content-Security-Policy',"default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; img-src 'self' data: blob:; media-src 'self' blob: data: https:; connect-src 'self' https: http://127.0.0.1:* http://localhost:*; worker-src 'self' blob:; object-src 'none'; base-uri 'self'; frame-ancestors 'none'")
            self.end_headers();self.wfile.write(body);return
        if path=='/healthz':return self.send(200,{'ok':True,'release':VERSION})
        if path.startswith('/media/'):
            pieces=path.split('/')
            if len(pieces)!=4:return self.send(404,{'error':'Topilmadi.'})
            job=get_job(pieces[2])
            if not job or job.get('status')!='COMPLETED' or not hmac.compare_digest(str(job.get('media_token','')),pieces[3]):return self.send(404,{'error':'Topilmadi.'})
            p=MEDIA/job['id']/job.get('output_file','result.mp4')
            if not p.is_file():return self.send(404,{'error':'Fayl topilmadi.'})
            size=p.stat().st_size;start=0;end=size-1;code=200
            range_header=self.headers.get('Range','')
            if range_header:
                match=re.fullmatch(r'bytes=(\d*)-(\d*)',range_header)
                if not match:return self.send(416,{'error':'Range invalid'})
                a,b=match.groups()
                if not a and b:start=max(0,size-int(b))
                elif a:start=int(a);end=min(end,int(b)) if b else end
                if start>end or start>=size:return self.send(416,{'error':'Range invalid'})
                code=206
            self.send_response(code);self.cors();self.send_header('Content-Type',job.get('mime','video/mp4'));self.send_header('Content-Length',str(end-start+1));self.send_header('Accept-Ranges','bytes');self.send_header('Cache-Control','private, no-store');self.send_header('Content-Disposition','inline; filename="Shirin-'+job['id'][:8]+p.suffix+'"')
            if code==206:self.send_header('Content-Range',f'bytes {start}-{end}/{size}')
            self.end_headers()
            with p.open('rb') as f:
                f.seek(start);remaining=end-start+1
                while remaining:
                    chunk=f.read(min(1024*1024,remaining))
                    if not chunk:break
                    self.wfile.write(chunk);remaining-=len(chunk)
            return
        if not self.auth():return
        if path=='/health':
            c=providers.catalog();return self.send(200,{'name':'Shirin AI','release':VERSION,'configured':any(m['ready'] for m in c['video'] if m['id']!='montage'),'video_provider':'fal' if providers.configured('FAL_KEY') else 'local','montage':bool(shutil.which('ffmpeg')),'max_images':MAX_IMAGES,'max_duration':MAX_SECONDS,'durations':[5,10,15,30,60,120,300,600],'image_ready':any(m['ready'] for m in c['image']),'chat_ready':bool(c['chat']),'voice_languages':['uz','en'] if any(c['voice'].values()) else [],'image_text':storyboard.vision_ready(),'models':c,'video_status':providers.video_setup(),'capabilities':{'scene_prompts':True,'analysis_images':True,'animation_intent':True},'higgsfield':{'configured':higgsfield.ready(),'account_verified':False,'models':len(higgsfield.CATALOG)},'free_mode':True})
        if path=='/models':return self.send(200,providers.catalog())
        if path=='/jobs':
            try:offset=max(0,int(parse_qs(parsed.query).get('offset',['0'])[0]))
            except ValueError:return self.send(400,{'error':'Offset invalid'})
            with sqlite3.connect(DB) as db:rows=db.execute('SELECT payload FROM jobs ORDER BY rowid DESC LIMIT 51 OFFSET ?',(offset,)).fetchall()
            return self.send(200,{'jobs':[public(json.loads(r[0])) for r in rows[:50]],'next_offset':offset+50 if len(rows)>50 else None})
        if path.startswith('/jobs/'):
            job=get_job(path[6:]);return self.send(200,public(job)) if job else self.send(404,{'error':'Ish topilmadi.'})
        self.send(404,{'error':'Topilmadi.'})
    def do_POST(self):
        origin=self.headers.get('Origin','')
        if origin and origin not in ORIGINS and urlparse(origin).netloc!=self.headers.get('Host',''):
            return self.send(403,{'error':'Origin not allowed'})
        if self.headers.get('Content-Type','').split(';')[0]!='application/json':
            return self.send(415,{'error':'application/json required'})
        if not self.auth():return
        try:
            size=int(self.headers.get('Content-Length','0'))
            if not 0<size<=int(os.environ.get('SHIRIN_MAX_UPLOAD_MB','256'))*1024*1024:return self.send(413,{'error':'Yuklama server xotirasi uchun katta.'})
            data=json.loads(self.rfile.read(size));path=urlparse(self.path).path
            if not isinstance(data,dict):raise ValueError('So‘rov turi noto‘g‘ri.')
            if path=='/chat':return self.send(200,providers.chat(data))
            if path=='/agent':return self.send(200,providers.agent(data))
            if path in ('/image','/voice'):
                data['kind']='openai_image' if path=='/image' else 'voice'
                return self.send(202,public(submit(data)))
            if path=='/jobs':return self.send(202,public(submit(data)))
            if path.startswith('/jobs/') and path.endswith('/cancel'):
                jid=path.split('/')[2]
                with LOCK:
                    if jid in CANCEL:CANCEL[jid].set();return self.send(200,{'ok':True})
                return self.send(409,{'error':'Ish allaqachon tugagan.'})
            return self.send(404,{'error':'Topilmadi.'})
        except (ValueError,TypeError,KeyError) as e:return self.send(400,{'error':str(e)[:900]})
        except Exception:return self.send(502,{'error':'Xizmat bilan bog‘lanib bo‘lmadi. Keyinroq urinib ko‘ring.'})

if __name__=='__main__':
    if BIND not in ('127.0.0.1','::1') and len(TOKEN)<32:raise SystemExit('SHIRIN_TOKEN must contain at least 32 characters for remote access.')
    init_db();print('Shirin AI Studio '+VERSION+' ready',flush=True)
    ThreadingHTTPServer((BIND,int(os.environ.get('PORT','8080'))),Handler).serve_forever()
