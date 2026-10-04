"""Ordered AI clip plan and exact-frame MP4 assembly; requires ffmpeg/ffprobe."""
import json
import math
import subprocess
from pathlib import Path

FPS = 30

def plan(seconds, count):
    if seconds not in (5, 10, 30) or not 1 <= count <= 15:
        raise ValueError('Invalid duration/image count')
    copies = math.ceil(seconds / count / 10)
    n = count * copies
    base, remainder = divmod(seconds * FPS, n)
    return [{'image_index': i // copies, 'frames': base + (i < remainder),
             'duration': '5' if (base + (i < remainder)) <= 5 * FPS else '10'} for i in range(n)]

def run(args):
    subprocess.run(args, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, timeout=300)

def assemble(clips, steps, directory, ratio='9:16'):
    directory = Path(directory)
    w, h = {'9:16': (720,1280), '16:9': (1280,720), '1:1': (720,720)}[ratio]
    for i,(clip,step) in enumerate(zip(clips,steps)):
        vf = f'scale={w}:{h}:force_original_aspect_ratio=decrease,pad={w}:{h}:(ow-iw)/2:(oh-ih)/2,setsar=1,fps=30,tpad=stop_mode=clone:stop_duration=30'
        run(['ffmpeg','-y','-nostdin','-protocol_whitelist','file,pipe','-i',str(clip),'-vf',vf,'-frames:v',str(step['frames']),'-an','-c:v','libx264','-threads','2','-preset','veryfast','-pix_fmt','yuv420p',str(directory/f'part-{i}.mp4')])
    listing=directory/'parts.txt'
    listing.write_text(''.join(f"file 'part-{i}.mp4'\n" for i in range(len(clips))))
    output=directory/'result.mp4'
    run(['ffmpeg','-y','-nostdin','-f','concat','-safe','1','-i',str(listing),'-c','copy','-movflags','+faststart',str(output)])
    info=json.loads(subprocess.check_output(['ffprobe','-v','error','-select_streams','v:0','-show_entries','stream=nb_frames,avg_frame_rate','-of','json',str(output)],timeout=30))['streams'][0]
    if int(info['nb_frames']) != sum(s['frames'] for s in steps) or info['avg_frame_rate'] != '30/1':
        raise ValueError('Output duration verification failed')
    return output
