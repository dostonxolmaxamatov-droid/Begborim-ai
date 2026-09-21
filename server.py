"""Begborim AI single-owner gateway. Python 3.11+, standard library only."""
import base64
import hmac
import json
import os
import re
import sqlite3
import threading
import time
import secrets
import shutil
from pathlib import Path
import montage
import storyboard
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.request import Request, HTTPRedirectHandler, build_opener
from urllib.error import HTTPError
from urllib.parse import urlparse

DB = os.environ.get('BEGBORIM_DB', 'begborim.sqlite3')
TOKEN = os.environ.get('BEGBORIM_TOKEN', '')
KEY = os.environ.get('FAL_KEY', '')
LOCK = threading.Lock()
MEDIA = Path(os.environ.get('BEGBORIM_MEDIA', 'begborim-media'))
PUBLIC_BASE = (os.environ.get('PUBLIC_BASE_URL') or
               ('https://' + os.environ['RAILWAY_PUBLIC_DOMAIN'] if os.environ.get('RAILWAY_PUBLIC_DOMAIN') else '')).rstrip('/')
MODELS = {'image': 'fal-ai/flux/schnell',
          'text_video': 'fal-ai/kling-video/v2.5-turbo/pro/text-to-video',
          'image_video': 'fal-ai/kling-video/v2.5-turbo/pro/image-to-video'}

def init_db():
    Path(DB).parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(DB) as db:
        db.execute('CREATE TABLE IF NOT EXISTS jobs (id TEXT PRIMARY KEY, payload TEXT NOT NULL)')

def save(job):
    with sqlite3.connect(DB) as db:
        db.execute('INSERT OR REPLACE INTO jobs VALUES (?,?)', (job['id'], json.dumps(job)))

def all_jobs():
    with sqlite3.connect(DB) as db:
        return [json.loads(r[0]) for r in db.execute('SELECT payload FROM jobs ORDER BY rowid DESC LIMIT 100')]

def get_job(jid):
    with sqlite3.connect(DB) as db:
        row = db.execute('SELECT payload FROM jobs WHERE id=?', (jid,)).fetchone()
        return json.loads(row[0]) if row else None

def public(job, include_scenes=True):
    return {k: v for k, v in job.items() if k not in ('status_url', 'response_url', 'media_token') and (include_scenes or k!='scenes')}

class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        raise ValueError('Unexpected provider redirect')

def fal(url, data=None):
    # Never forward a provider key to an arbitrary URL or redirect.
    p = urlparse(url)
    if p.scheme != 'https' or p.netloc != 'queue.fal.run':
        raise ValueError('Invalid provider URL')
    req = Request(url, data=None if data is None else json.dumps(data).encode(),
                  headers={'Authorization': 'Key ' + KEY, 'Content-Type': 'application/json'})
    with build_opener(NoRedirect).open(req, timeout=55) as response:
        return json.load(response)

def validate(data):
    if not isinstance(data, dict):
        raise ValueError('So‘rov noto‘g‘ri.')
    kind = data.get('kind')
    prompt = data.get('prompt', '')
    ratio = data.get('ratio', '9:16')
    auto = data.get('auto_text', False)
    language = data.get('video_language','none')
    if not isinstance(auto,bool) or language not in ('uz','en','none'): raise ValueError('Til yoki matn rejimi noto‘g‘ri.')
    auto = auto and kind == 'image_video'
    if kind not in MODELS or not isinstance(prompt, str) or len(prompt.strip())>2500 or (not auto and len(prompt.strip())<3):
        raise ValueError('Tavsif 3–2500 belgidan iborat bo‘lsin.')
    if ratio not in ('9:16', '16:9', '1:1'):
        raise ValueError('Format noto‘g‘ri.')
    inp = {'prompt': prompt.strip()}
    if kind == 'image':
        inp.update(image_size={'9:16': 'portrait_16_9', '16:9': 'landscape_16_9', '1:1': 'square_hd'}[ratio], num_images=1, enable_safety_checker=True)
    else:
        duration = str(data.get('duration', '5'))
        if duration not in ('5', '10', '30'):
            raise ValueError('5, 10 yoki 30 soniya tanlang.')
        if auto: inp['auto_text'] = True
        if language!='none': inp['video_language'] = language
        inp['duration'] = duration
        inp['aspect_ratio'] = ratio
        if kind == 'image_video':
            images = data.get('images', [data.get('image', '')])
            if not isinstance(images, list) or not 1 <= len(images) <= 15:
                raise ValueError('1–15 ta rasm tanlang.')
            for image in images:
                if not isinstance(image, str) or not re.match(r'^data:image/(jpeg|png|webp);base64,', image):
                    raise ValueError('JPG, PNG yoki WebP rasm tanlang.')
                try:
                    raw = base64.b64decode(image.split(',', 1)[1], validate=True)
                except Exception:
                    raise ValueError('Rasm o‘qilmadi.')
                if not 16 <= len(raw) <= 6 * 1024 * 1024:
                    raise ValueError('Har bir rasm 6 MB dan oshmasin.')
                if not (raw.startswith(b'\xff\xd8\xff') or raw.startswith(b'\x89PNG\r\n\x1a\n') or (raw[:4] == b'RIFF' and raw[8:12] == b'WEBP')):
                    raise ValueError('Rasm formati noto‘g‘ri.')
            inp['images'] = images
    return kind, inp

def montage_ready():
    p = urlparse(PUBLIC_BASE)
    return bool(p.scheme == 'https' and p.netloc and not p.query and not p.fragment and not p.username and shutil.which('ffmpeg') and shutil.which('ffprobe'))

def media_download(url, target):
    p = urlparse(url)
    # Provider media only, no bearer credentials, no arbitrary redirects.
    host = p.hostname or ''
    if p.scheme != 'https' or p.port not in (None,443) or p.username or not (host.endswith('.fal.media') or host in ('fal.media','storage.googleapis.com')):
        raise ValueError('Unsupported media origin')
    with build_opener(NoRedirect).open(Request(url), timeout=90) as stream, open(target,'wb') as out:
        size=0
        while True:
            chunk=stream.read(1024*1024)
            if not chunk: break
            size += len(chunk)
            if size > 256*1024*1024: raise ValueError('Clip too large')
            out.write(chunk)

def run_montage(job, inp):
    folder=MEDIA/job['id']
    clips=[]
    try:
        folder.mkdir(parents=True,exist_ok=True)
        steps=montage.plan(int(inp['duration']),len(inp.get('images',[None])))
        job.update(status='IN_PROGRESS', completed_clips=0, total_clips=len(steps))
        save(job)
        scenes=None;audio=None
        language=inp.get('video_language','none')
        if inp.get('auto_text') or language!='none':
            job.update(stage='ANALYZING',analyzed_images=0);save(job)
            scenes=[]
            source_images=inp.get('images',[None])
            for index,image in enumerate(source_images):
                seconds=sum(st['frames'] for st in steps if st['image_index']==index)/30
                try: scene=storyboard.read_scene(image,inp['prompt'],language,seconds,inp.get('auto_text',False))
                except ValueError as e: raise ValueError(f'Rasm {index+1}: {e}')
                scenes.append(scene);job.update(analyzed_images=index+1,scenes=list(scenes));save(job)
            if language!='none':
                job.update(stage='VOICE',video_language=language);save(job)
                audio=storyboard.prepare_audio(scenes,steps,folder,language)
        for i,step in enumerate(steps):
            action=scenes[step['image_index']]['action_prompt'] if scenes else inp['prompt']
            payload={'prompt': action, 'duration': step['duration']}
            if 'images' in inp: payload['image_url']=inp['images'][step['image_index']]
            else: payload['aspect_ratio']=inp['aspect_ratio']
            job['stage']='SUBMITTING_CLIP';save(job)
            try:
                result=fal('https://queue.fal.run/'+MODELS[job['kind']],payload)
            except HTTPError as e:
                if e.code>=500: job['status']='UNKNOWN'
                raise
            except Exception:
                job['status']='UNKNOWN'
                raise
            job.update(stage='WAITING_CLIP',provider_id=result['request_id'])
            save(job)
            deadline=time.monotonic()+3600
            while True:
                if time.monotonic()>deadline:
                    job['status']='UNKNOWN'
                    raise TimeoutError('Provider timeout')
                status=fal(result['status_url'])
                if status.get('error') or status.get('status') in ('FAILED','CANCELLED'): raise ValueError('Generation failed')
                if status.get('status')=='COMPLETED': break
                time.sleep(5)
            out=fal(result['response_url'])
            clip=folder/f'clip-{i}.mp4'
            media_download(out['video']['url'],clip);clips.append(clip)
            job['completed_clips']=i+1;save(job)
        job.update(status='ASSEMBLING',stage='ASSEMBLING');save(job)
        video=montage.assemble(clips,steps,folder,inp['aspect_ratio'])
        if audio: storyboard.mux_voice(video,audio,int(inp['duration']),language)
        secret=secrets.token_urlsafe(32)
        job.update(status='COMPLETED',stage='DONE',media_token=secret,url=PUBLIC_BASE+'/media/'+job['id']+'/'+secret)
        save(job)
    except Exception as exc:
        if job.get('stage')=='WAITING_CLIP': job['status']='UNKNOWN'
        if job['status']!='UNKNOWN': job['status']='FAILED'
        job['error']='Video tugallanmadi. Tayyorlangan qismlar uchun haq olinishi mumkin. Qayta yuborishdan oldin fal hisobini tekshiring.'
        if job.get('stage') in ('ANALYZING','VOICE'):
            job['error']=str(exc) if isinstance(exc,ValueError) else 'Matn yoki ovoz xizmati bilan bog‘lanib bo‘lmadi. Server kalitlarini tekshiring.'
        save(job)
    finally:
        # Keep successful final output; remove intermediate clips and image data from memory.
        for f in folder.glob('*'):
            if f.name!='result.mp4': f.unlink(missing_ok=True)

class Handler(BaseHTTPRequestHandler):
    def log_message(self, *args):
        pass  # Do not log prompts, uploaded images or authorization tokens.

    def send(self, code, data):
        body = json.dumps(data, ensure_ascii=False).encode()
        self.send_response(code)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Content-Length', str(len(body)))
        self.send_header('Cache-Control', 'no-store')
        self.end_headers()
        self.wfile.write(body)

    def auth(self):
        supplied = self.headers.get('Authorization', '')
        # compare_digest(str, str) rejects non-ASCII text. Reject malformed
        # headers without raising or changing the constant-time token check.
        ok = bool(TOKEN) and supplied.isascii() and hmac.compare_digest(
            supplied.encode('utf-8'), ('Bearer ' + TOKEN).encode('utf-8'))
        if not ok:
            self.send(401, {'error': 'Ulanish kodi noto‘g‘ri.'})
        return ok

    def do_GET(self):
        if self.path == '/healthz':
            return self.send(200, {'ok': True})
        if self.path.startswith('/media/'):
            pieces=self.path.split('/')
            if len(pieces)!=4 or not re.fullmatch(r'[a-zA-Z0-9-]{16,64}',pieces[2]):
                return self.send(404, {'error':'Topilmadi.'})
            job=get_job(pieces[2])
            if not job or job.get('status')!='COMPLETED' or not job.get('media_token') or not hmac.compare_digest(pieces[3],job['media_token']):
                return self.send(404, {'error':'Topilmadi.'})
            target=MEDIA/pieces[2]/'result.mp4'
            if not target.is_file(): return self.send(404, {'error':'Fayl topilmadi.'})
            self.send_response(200)
            self.send_header('Content-Type','video/mp4')
            self.send_header('Content-Length',str(target.stat().st_size))
            self.send_header('Content-Disposition','attachment; filename="Begborim-video.mp4"')
            self.send_header('Cache-Control','private, no-store')
            self.end_headers()
            with target.open('rb') as f: shutil.copyfileobj(f,self.wfile)
            return
        if not self.auth():
            return
        if self.path == '/health':
            return self.send(200, {'configured': bool(KEY), 'name': 'Begborim AI', 'montage': montage_ready(), 'max_images':15, 'max_duration':30, 'image_text':storyboard.vision_ready(), 'voice_languages':['uz','en'] if storyboard.voice_ready() else []})
        if self.path == '/jobs':
            return self.send(200, {'jobs': [public(j,False) for j in all_jobs()]})
        if self.path.startswith('/jobs/'):
            with LOCK:
                job = get_job(self.path[6:])
                if job is None:
                    return self.send(404, {'error': 'Ish topilmadi.'})
                if not job.get('montage') and job['status'] in ('IN_QUEUE', 'IN_PROGRESS'):
                    try:
                        result = fal(job['status_url'])
                        job['status'] = result['status']
                        if result.get('error'):
                            job.update(status='FAILED', error='AI xizmati so‘rovni bajara olmadi.')
                        elif job['status'] == 'COMPLETED':
                            out = fal(job['response_url'])
                            media = out.get('video') if job['kind'] != 'image' else (out.get('images') or [{}])[0]
                            url = (media or {}).get('url', '')
                            if not url.startswith('https://'):
                                raise ValueError('No media in response')
                            job['url'] = url
                        save(job)
                    except HTTPError as e:
                        if e.code == 422:
                            job.update(status='FAILED', error='AI so‘rovni rad etdi. Tavsif yoki rasmni tekshiring.')
                            save(job)
                        else:
                            return self.send(502, {'error': 'AI bilan aloqa uzildi. Keyinroq yangilang.'})
                    except Exception:
                        return self.send(502, {'error': 'Natija hali olinmadi. Keyinroq yangilang.'})
            return self.send(200, public(job))
        self.send(404, {'error': 'Topilmadi.'})

    def do_POST(self):
        if not self.auth():
            return
        if self.path != '/jobs':
            return self.send(404, {'error': 'Topilmadi.'})
        if not KEY:
            return self.send(503, {'error': 'AI hali ulanmagan. Serverga FAL_KEY qo‘shish kerak.'})
        try:
            n = int(self.headers.get('Content-Length', '0'))
            if not 0 < n <= 36 * 1024 * 1024:
                return self.send(413, {'error': 'Rasm hajmi juda katta.'})
            data = json.loads(self.rfile.read(n))
            kind, inp = validate(data)
            combined = kind != 'image' and (inp['duration']=='30' or len(inp.get('images',[]))>1 or inp.get('auto_text') or inp.get('video_language','none')!='none')
            if combined and not montage_ready():
                return self.send(503, {'error':'30 soniya va ko‘p rasm uchun serverni 0.2 ga yangilang, FFmpeg va PUBLIC_BASE_URL sozlang.'})
            if (inp.get('auto_text') or inp.get('video_language','none')!='none') and not storyboard.vision_ready():
                return self.send(503,{'error':'Rasmdagi matnni o‘qish/tarjima uchun serverga GEMINI_API_KEY qo‘shish kerak.'})
            if inp.get('video_language','none')!='none' and not storyboard.voice_ready():
                return self.send(503,{'error':'O‘zbekcha/English ovoz uchun serverga Azure Speech ulanishi kerak.'})
            jid = data.get('id', '')
            if not isinstance(jid, str) or not re.fullmatch(r'[a-zA-Z0-9-]{16,64}', jid):
                raise ValueError('So‘rov identifikatori noto‘g‘ri.')
        except (ValueError, TypeError) as e:
            return self.send(400, {'error': str(e)})
        # Persist before submission: an uncertain timeout cannot silently double-bill.
        with LOCK:
            existing = get_job(jid)
            if existing:
                return self.send(200, public(existing))
            recent = all_jobs()
            if any(j['status'] in ('SUBMITTING', 'IN_QUEUE', 'IN_PROGRESS', 'ASSEMBLING', 'UNKNOWN') for j in recent):
                return self.send(409, {'error': 'Avvalgi ish tugashini kuting. Noma’lum holat bo‘lsa fal hisobini tekshiring.'})
            if recent and time.time() - recent[0]['created'] < 15:
                return self.send(429, {'error': '15 soniyadan keyin urinib ko‘ring.'})
            job = {'id': jid, 'kind': kind, 'prompt': inp['prompt'] or 'Rasmlardagi matn asosida', 'created': time.time(), 'status': 'SUBMITTING'}
            if combined:
                job.update(montage=True,status='IN_PROGRESS',duration=int(inp['duration']),completed_clips=0,total_clips=len(montage.plan(int(inp['duration']),len(inp.get('images',[None])))))
                save(job)
                threading.Thread(target=run_montage,args=(job.copy(),inp),daemon=True).start()
                return self.send(200,public(job))
            if kind=='image_video':
                inp['image_url']=inp.pop('images')[0]
                inp.pop('aspect_ratio',None)
            save(job)
            try:
                result = fal('https://queue.fal.run/' + MODELS[kind], inp)
                job.update(status='IN_QUEUE', status_url=result['status_url'], response_url=result['response_url'], provider_id=result['request_id'])
            except HTTPError as e:
                job.update(status='FAILED' if e.code < 500 else 'UNKNOWN', error='AI so‘rovi qabul qilinmadi yoki holati noma’lum. fal hisobini tekshiring.')
            except Exception:
                job.update(status='UNKNOWN', error='Javob olinmadi. Takrorlashdan oldin fal hisobidagi navbatni tekshiring.')
            save(job)
        self.send(200, public(job))

if __name__ == '__main__':
    if len(TOKEN) < 32:
        raise SystemExit('Set BEGBORIM_TOKEN to a random secret of at least 32 characters.')
    init_db()
    # A process crash during submission leaves an explicitly uncertain job.
    with sqlite3.connect(DB) as db:
        for (payload,) in db.execute('SELECT payload FROM jobs').fetchall():
            job = json.loads(payload)
            if job['status'] == 'SUBMITTING' or (job.get('montage') and job['status'] in ('IN_PROGRESS','ASSEMBLING')):
                job.update(status='UNKNOWN', error='Server qayta ishga tushdi. fal hisobidagi so‘rovni tekshiring.')
                db.execute('UPDATE jobs SET payload=? WHERE id=?', (json.dumps(job), job['id']))
    print('Begborim gateway listening; place behind an HTTPS reverse proxy.', flush=True)
    ThreadingHTTPServer((os.environ.get('BIND', '127.0.0.1'), int(os.environ.get('PORT', '8080'))), Handler).serve_forever()
