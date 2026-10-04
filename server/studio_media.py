"""Local media tools. No paid service, product quota or watermark."""
import base64, json, math, os, re, shutil, subprocess
from pathlib import Path

SIZES={'480':480,'720':720,'1080':1080,'2160':2160}
RATIOS={'9:16':(9,16),'16:9':(16,9),'1:1':(1,1),'4:3':(4,3),'3:4':(3,4),'21:9':(21,9)}

def dimensions(ratio,quality):
    a,b=RATIOS.get(ratio,(9,16)); edge=SIZES.get(str(quality),720)
    return tuple(max(2,round(v*edge/min(a,b)/2)*2) for v in (a,b))

def command(args,timeout=1200):
    p=subprocess.run(args,stdout=subprocess.PIPE,stderr=subprocess.PIPE,timeout=timeout)
    if p.returncode: raise ValueError('Media fayl qayta ishlanmadi: '+p.stderr.decode(errors='replace')[-700:])
    return p.stdout

def probe(path):
    info=json.loads(command(['ffprobe','-v','error','-protocol_whitelist','file,pipe','-show_format','-show_streams','-of','json',str(path)],30))
    formats=set(info.get('format',{}).get('format_name','').split(','))
    if not formats.intersection({'mov','mp4','matroska','webm','mp3','wav','ogg','flac','aac'}):raise ValueError('Bu media konteyneri qo‘llanmaydi.')
    return info

def decode_file(value,target,limit=128*1024*1024,image=False):
    if not isinstance(value,str) or not value.startswith('data:') or ';base64,' not in value:
        raise ValueError('Fayl o‘qilmadi. Uni qayta tanlang.')
    header,encoded=value.split(',',1)
    if len(encoded)>limit*4//3+16:raise ValueError('Fayl server xotirasi uchun katta.')
    try: data=base64.b64decode(encoded,validate=True)
    except Exception:raise ValueError('Fayl formati noto‘g‘ri.')
    if not data or len(data)>limit:raise ValueError('Fayl hajmi noto‘g‘ri.')
    if image and not (data.startswith(b'\xff\xd8\xff') or data.startswith(b'\x89PNG\r\n\x1a\n') or (data[:4]==b'RIFF' and data[8:12]==b'WEBP')):
        raise ValueError('PNG, JPG yoki WebP rasm tanlang.')
    Path(target).write_bytes(data)
    return header[5:].split(';')[0]

def ass_time(seconds):
    n=round(seconds*100);return f'{n//360000}:{n//6000%60:02d}:{n//100%60:02d}.{n%100:02d}'

def subtitles(path,cues,w,h):
    font=max(18,round(h*.037))
    text=f'''[Script Info]\nScriptType: v4.00+\nPlayResX: {w}\nPlayResY: {h}\n[V4+ Styles]\nFormat: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding\nStyle: Default,DejaVu Sans,{font},&H00FFFFFF,&H00FFFFFF,&H00000000,&H90000000,-1,0,0,0,100,100,0,0,1,2,1,2,30,30,{round(h*.08)},1\n[Events]\nFormat: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text\n'''
    for cue in cues:
        content=str(cue.get('text','')).replace('\\','').replace('{','').replace('}','').replace('\r','').replace('\n',r'\N')
        start=max(0,float(cue.get('start',0)));end=float(cue.get('end',start+2))
        if end>start and content:text+=f'Dialogue: 0,{ass_time(start)},{ass_time(end)},Default,,0,0,0,,{content}\n'
    Path(path).write_text(text,encoding='utf-8')


def render(data,folder,progress,cancelled,source_video=None):
    folder=Path(folder);w,h=dimensions(data.get('ratio'),data.get('quality','720'))
    fps=int(data.get('fps',30))
    if fps not in (24,30,60):raise ValueError('24, 30 yoki 60 FPS tanlang.')
    duration=float(data.get('duration',15))
    if not math.isfinite(duration) or not 1<=duration<=int(os.environ.get('SHIRIN_MAX_SECONDS','600')):raise ValueError('Davomiylik server imkoniyatidan tashqarida.')
    total_frames=round(duration*fps);out=folder/'result.mp4'
    images=data.get('images',[]);cues=data.get('subtitles',[])
    clips=[]
    if source_video or data.get('video'):
        src=Path(source_video) if source_video else folder/'input-video'
        if not source_video:decode_file(data['video'],src)
        info=probe(src)
        if not any(s.get('codec_type')=='video' for s in info.get('streams',[])):raise ValueError('Faylda video treki yo‘q.')
        start=max(0,float(data.get('trim_start',0)))
        actual=float(info.get('format',{}).get('duration',duration))
        if not math.isfinite(start) or start>=actual:raise ValueError('Boshlanish vaqti video oxiridan katta.')
        duration=min(duration,actual-start)
        vf=f'scale={w}:{h}:force_original_aspect_ratio=decrease,pad={w}:{h}:(ow-iw)/2:(oh-ih)/2,setsar=1,fps={fps}'
        if data.get('filter')=='mono':vf+=',hue=s=0'
        elif data.get('filter')=='warm':vf+=',colorbalance=rs=.07:bs=-.05'
        if cues:
            sub=folder/'captions.ass';subtitles(sub,cues,w,h);vf+=',ass='+str(sub.resolve())
        progress('Tahrirlanmoqda',.2)
        command(['ffmpeg','-y','-v','error','-ss',str(start),'-i',str(src),'-t',str(duration),'-vf',vf,'-c:v','libx264','-preset','veryfast','-crf','20','-pix_fmt','yuv420p','-c:a','aac','-movflags','+faststart',str(out)])
    else:
        if not images:raise ValueError('Kamida bitta rasm tanlang.')
        if len(images)>total_frames:raise ValueError('Har bir rasm uchun kamida bitta kadr kerak. Vaqtni uzaytiring.')
        for i,value in enumerate(images):
            if cancelled():raise InterruptedError('Bekor qilindi.')
            src=folder/f'input-{i}.img';decode_file(value,src,16*1024*1024,True)
            frames=total_frames//len(images)+(i<total_frames%len(images))
            vf=f'scale={w}:{h}:force_original_aspect_ratio=decrease,pad={w}:{h}:(ow-iw)/2:(oh-ih)/2,setsar=1'
            if data.get('motion','zoom')=='zoom':
                vf+=f",zoompan=z='1+.08*on/{frames}':x='iw/2-iw/zoom/2':y='ih/2-ih/zoom/2':d={frames}:s={w}x{h}:fps={fps}"
            elif data.get('motion')=='pan':
                vf+=f",zoompan=z='1.08':x='(iw-iw/zoom)*on/{frames}':y='ih/2-ih/zoom/2':d={frames}:s={w}x{h}:fps={fps}"
            else:vf+=f',fps={fps}'
            clip=folder/f'clip-{i}.mp4'
            command(['ffmpeg','-y','-v','error','-loop','1','-i',str(src),'-vf',vf,'-frames:v',str(frames),'-an','-c:v','libx264','-preset','veryfast','-crf','20','-pix_fmt','yuv420p',str(clip)])
            clips.append(clip);progress('Rasmlar birlashtirilmoqda',(i+1)/len(images)*.7)
        listing=folder/'clips.txt';listing.write_text(''.join("file '"+str(p.resolve())+"'\n" for p in clips))
        args=['ffmpeg','-y','-v','error','-f','concat','-safe','0','-i',str(listing)]
        if cues:
            sub=folder/'captions.ass';subtitles(sub,cues,w,h)
            args+=['-vf','ass='+str(sub.resolve()),'-c:v','libx264','-preset','veryfast','-crf','20']
        else:args+=['-c:v','copy']
        command(args+['-an','-movflags','+faststart',str(out)])
    if cancelled():raise InterruptedError('Bekor qilindi.')
    if data.get('audio'):
        audio=folder/'input-audio';decode_file(data['audio'],audio);probe(audio)
        muxed=folder/'with-audio.mp4'
        command(['ffmpeg','-y','-v','error','-i',str(out),'-i',str(audio),'-map','0:v:0','-map','1:a:0','-c:v','copy','-c:a','aac','-af','apad','-t',str(duration),'-movflags','+faststart',str(muxed)])
        muxed.replace(out)
    progress('Tayyor',1)
    return out,'video/mp4'
