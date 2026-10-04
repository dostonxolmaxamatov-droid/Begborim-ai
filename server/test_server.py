import base64, io, json, os, tempfile, threading, time, unittest, urllib.request, urllib.error, wave, math, struct
from pathlib import Path
from unittest.mock import patch
from PIL import Image
import server,providers,studio_media

class StudioIntegration(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.tmp=tempfile.TemporaryDirectory();server.DB=cls.tmp.name+'/db.sqlite3';server.MEDIA=Path(cls.tmp.name)/'media';server.TOKEN='unit-test-token-01234567890123456789';server.init_db()
  cls.http=server.ThreadingHTTPServer(('127.0.0.1',0),server.Handler);cls.port=cls.http.server_port
  cls.thread=threading.Thread(target=cls.http.serve_forever,daemon=True);cls.thread.start()
 @classmethod
 def tearDownClass(cls):cls.http.shutdown();cls.http.server_close();cls.tmp.cleanup()
 def request(self,path,body=None,auth=True,headers=None):
  h={'Content-Type':'application/json',**(headers or {})}
  if auth:h['Authorization']='Bearer '+server.TOKEN
  try:
   with urllib.request.urlopen(urllib.request.Request('http://127.0.0.1:'+str(self.port)+path,data=json.dumps(body).encode() if body is not None else None,headers=h),timeout=20) as r:return r.status,r.read(),r.headers
  except urllib.error.HTTPError as e:return e.code,e.read(),e.headers
 def test_auth_and_csrf(self):
  self.assertEqual(self.request('/health',auth=False)[0],401)
  self.assertEqual(self.request('/jobs',{'kind':'montage'},headers={'Origin':'https://outside.example'})[0],403)
  self.assertEqual(self.request('/healthz',auth=False)[0],200)
  health=json.loads(self.request('/health')[1]);self.assertTrue(health['capabilities']['scene_prompts']);self.assertTrue(health['capabilities']['analysis_images'])
 def test_paid_gate_and_no_sora(self):
  status,body,_=self.request('/jobs',{'kind':'fal_video','prompt':'hello','duration':5})
  self.assertEqual(status,400);self.assertIn('Bepul',json.loads(body)['error'])
  c=providers.catalog();self.assertFalse(any('sora' in m['id'] for m in c['video']))
 def test_missing_video_config_never_queues_job(self):
  with patch.dict(os.environ,{'FAL_KEY':'  ','COMFYUI_URL':'','COMFYUI_VIDEO_WORKFLOW':''}),patch.object(server.WORKERS,'submit') as worker:
   for kind,required in [('fal_video','FAL_KEY'),('comfy_video','COMFYUI_URL')]:
    jid='missing-provider-'+kind.replace('_','-')
    status,body,_=self.request('/jobs',{'id':jid,'kind':kind,'video_intent':'animation','prompt':'Walk forward','allow_paid':True})
    self.assertEqual(status,400);self.assertIn(required,json.loads(body)['error']);self.assertIsNone(server.get_job(jid))
   worker.assert_not_called()
 def test_health_reports_config_without_claiming_live_verification(self):
  secret='not-a-real-key-for-test-only'
  with patch.dict(os.environ,{'FAL_KEY':secret,'COMFYUI_URL':'','COMFYUI_VIDEO_WORKFLOW':''}):
   status,body,_=self.request('/health');health=json.loads(body)
  self.assertEqual(status,200);self.assertNotIn(secret,body.decode())
  self.assertTrue(health['capabilities']['animation_intent'])
  self.assertEqual(health['video_status']['configured_providers'],['fal_video'])
  self.assertFalse(health['video_status']['account_verified'])
  self.assertEqual(health['video_status']['missing_by_provider']['comfy_video'],['COMFYUI_URL','COMFYUI_VIDEO_WORKFLOW'])
 def test_animation_intent_rejects_montage_without_queuing(self):
  jid='animation-montage-guard-0001'
  with patch.object(server.WORKERS,'submit') as worker:
   status,body,_=self.request('/jobs',{'id':jid,'kind':'montage','video_intent':'animation','prompt':'Wave'})
   self.assertEqual(status,400);self.assertIn('Montajga',json.loads(body)['error']);self.assertIsNone(server.get_job(jid));worker.assert_not_called()
 def test_existing_job_survives_provider_config_removal(self):
  job={'id':'existing-ai-job-0000000001','kind':'fal_video','video_intent':'animation','status':'COMPLETED','release':server.VERSION}
  server.save(job)
  with patch.dict(os.environ,{'FAL_KEY':''}),patch.object(server.WORKERS,'submit') as worker:
   status,body,_=self.request('/jobs',{'id':job['id'],'kind':'fal_video','video_intent':'animation','prompt':'Wave','allow_paid':True})
   self.assertEqual(status,202);self.assertEqual(json.loads(body),job);worker.assert_not_called()
 def test_exact_order_duration_audio_caption_and_range(self):
  images=[]
  for color in ['red','green','blue']:
   f=io.BytesIO();Image.new('RGB',(160,160),color).save(f,format='PNG');images.append('data:image/png;base64,'+base64.b64encode(f.getvalue()).decode())
  audio=io.BytesIO()
  with wave.open(audio,'wb') as w:
   w.setnchannels(1);w.setsampwidth(2);w.setframerate(8000);w.writeframes(b'\x00\x00'*24000)
  data={'id':'test-render-0000000000000001','kind':'montage','images':images,'duration':3,'ratio':'1:1','quality':'480','fps':30,'motion':'none','audio':'data:audio/wav;base64,'+base64.b64encode(audio.getvalue()).decode(),'subtitles':[{'start':0,'end':1,'text':'Salom!'}]}
  status,body,_=self.request('/jobs',data);self.assertEqual(status,202);job=json.loads(body)
  duplicate=json.loads(self.request('/jobs',data)[1]);self.assertEqual(duplicate['id'],job['id'])
  deadline=time.time()+45
  while time.time()<deadline:
   job=json.loads(self.request('/jobs/'+job['id'])[1])
   if job['status'] not in ('IN_QUEUE','IN_PROGRESS'):break
   time.sleep(.2)
  self.assertEqual(job['status'],'COMPLETED',job)
  p=server.MEDIA/job['id']/'result.mp4';info=studio_media.probe(p);video=next(s for s in info['streams'] if s['codec_type']=='video')
  self.assertEqual(int(video['nb_frames']),90);self.assertEqual(video['avg_frame_rate'],'30/1');self.assertTrue(any(s['codec_type']=='audio' for s in info['streams']))
  self.assertAlmostEqual(float(info['format']['duration']),3,places=1)
  for t,channel in [(.5,0),(1.5,1),(2.5,2)]:
   rgb=studio_media.command(['ffmpeg','-v','error','-ss',str(t),'-i',str(p),'-frames:v','1','-vf','crop=10:10:100:100,scale=1:1','-f','rawvideo','-pix_fmt','rgb24','-'])
   self.assertEqual(max(range(3),key=lambda i:rgb[i]),channel)
  status,body,h=self.request(job['url'],auth=False,headers={'Range':'bytes=0-63'});self.assertEqual(status,206);self.assertEqual(len(body),64)
  bad=job['url'].rsplit('/',1)[0]+'/invalid';self.assertEqual(self.request(bad,auth=False)[0],404)
 def test_empty_references_rejected_by_renderer(self):
  folder=Path(self.tmp.name)/'empty';folder.mkdir(exist_ok=True)
  with self.assertRaisesRegex(ValueError,'rasm'):studio_media.render({'duration':3,'images':[]},folder,lambda *a:None,lambda:False)
 def test_media_rejects_playlist(self):
  p=Path(self.tmp.name)/'bad.m3u8';p.write_text('#EXTM3U\n#EXTINF:5,\nhttps://example.com/a.mp4\n')
  with self.assertRaises(ValueError):studio_media.probe(p)
 def test_ollama_contract(self):
  calls=[]
  def fake(url,data=None,headers=None,raw=False,timeout=180):
   calls.append((url,data))
   return {'models':[{'name':'test-local'}]} if url.endswith('/api/tags') else {'message':{'content':'Salom'}}
  with patch.dict(os.environ,{'OLLAMA_URL':'http://127.0.0.1:11434'},clear=True),patch.object(providers,'request',fake):
   result=providers.chat({'message':'Salom','history':[],'model':'auto'})
  self.assertEqual(result['reply'],'Salom');self.assertFalse(calls[-1][1]['stream']);self.assertEqual(calls[-1][1]['messages'][-1]['content'],'Salom')

 def test_cloud_video_postprocess_without_paid_calls(self):
  import shutil
  folder=Path(self.tmp.name)/'cloud-contract';folder.mkdir()
  source=Path(self.tmp.name)/'source.mp4'
  studio_media.command(['ffmpeg','-y','-v','error','-f','lavfi','-i','color=c=blue:s=160x160:r=30:d=5','-an','-c:v','libx264',str(source)])
  audio=io.BytesIO()
  with wave.open(audio,'wb') as w:
   w.setnchannels(1);w.setsampwidth(2);w.setframerate(8000);w.writeframes(b'\x00\x00'*40000)
  calls=[]
  def fake_wait(endpoint,payload,cancelled):calls.append(payload);return {'video':{'url':'https://fal.media/test.mp4'}}
  def fake_media(url,target):shutil.copyfile(source,target);return target
  with patch.object(providers,'fal_wait',fake_wait),patch.object(providers,'provider_media',fake_media):
   output,mime=providers.fal_video({'allow_paid':True,'prompt':'test','duration':3.5,'ratio':'16:9','quality':'480','fps':24,'audio':'data:audio/wav;base64,'+base64.b64encode(audio.getvalue()).decode(),'subtitles':[{'start':0,'end':3,'text':'Test'}]},folder,lambda *a:None,lambda:False)
  info=studio_media.probe(output);v=next(s for s in info['streams'] if s['codec_type']=='video')
  self.assertEqual(v['height'],480);self.assertEqual(v['avg_frame_rate'],'24/1');self.assertEqual(int(v['nb_frames']),84);self.assertTrue(any(s['codec_type']=='audio' for s in info['streams']));self.assertEqual(len(calls),1)
 def test_ocr_failure_stops_before_video_request(self):
  folder=Path(self.tmp.name)/'ocr-failed';folder.mkdir()
  with patch.object(providers.storyboard,'read_scene',side_effect=ValueError('Matn o‘qilmadi')),patch.object(providers,'fal_wait') as paid:
   with self.assertRaisesRegex(ValueError,'o‘qilmadi'):providers.fal_video({'allow_paid':True,'auto_text':True,'images':['data:image/png;base64,AA=='],'duration':5},folder,lambda *a:None,lambda:False)
   paid.assert_not_called()

class AnimationContract(unittest.TestCase):
 def test_intent_validation_and_legacy_animation_alias(self):
  data={'kind':'image_video','video_intent':'animation','prompt':'Wave','allow_paid':True}
  self.assertEqual(server.validated(data)['kind'],'fal_video')
  for update in ({'kind':'edit_video'},{'kind':'openai_image'},{'video_intent':'montage'},{'video_intent':'edit'},{'video_intent':'unknown'}):
   with self.assertRaises(ValueError):server.validated({**data,**update})
 def test_provider_failure_never_becomes_slideshow_or_text_only(self):
  with tempfile.TemporaryDirectory() as temp,patch.object(providers,'fal_wait',side_effect=ValueError('Provider rejected reference')) as wait,patch.object(providers.studio_media,'render') as render:
   with self.assertRaisesRegex(ValueError,'rejected reference'):
    providers.fal_video({'allow_paid':True,'prompt':'Wave','images':['data:image/png;base64,YQ=='],'duration':5},Path(temp),lambda *a:None,lambda:False)
   self.assertEqual(wait.call_count,1);self.assertIn('image-to-video',wait.call_args.args[0]);self.assertIn('image_url',wait.call_args.args[1]);render.assert_not_called()
 def test_scene_input_validation(self):
  base={'kind':'fal_video','allow_paid':True,'images':['frame-a','frame-b'],'duration':10,'scene_prompts':['Walk forward','Smile and wave']}
  self.assertEqual(server.validated(base)['scene_prompts'],base['scene_prompts'])
  for extra in ({'scene_prompts':['One']},{'scene_prompts':[42,'Two']},{'analysis_images':['data:image/png;base64,YQ==']}):
   with self.assertRaises(ValueError):server.validated({**base,**extra})
  with patch.object(server.storyboard,'vision_ready',return_value=True):
   with self.assertRaisesRegex(ValueError,'buzilgan'):server.validated({**base,'auto_text':True,'analysis_images':['data:image/png;base64,***']*2})

 def test_each_scene_uses_its_own_action_and_uncropped_ocr(self):
  with tempfile.TemporaryDirectory() as temp:
   folder=Path(temp);payloads=[];reads=[]
   def read(image,prompt,language,seconds,auto):
    reads.append((image,prompt));return {'action_prompt':'Read: '+prompt,'visible_text':'Caption','narration':''}
   def wait(endpoint,payload,cancel):payloads.append((endpoint,payload));return {'video':{'url':'https://fal.media/test.mp4'}}
   def assemble(clips,steps,folder,ratio):
    p=folder/'result.mp4';p.write_bytes(b'test fixture');return p
   data={'allow_paid':True,'images':['cropped-a','cropped-b'],'analysis_images':['original-a','original-b'],'scene_prompts':['Walk forward','Smile and wave'],'auto_text':True,'duration':10,'ratio':'9:16'}
   with patch.object(providers.storyboard,'read_scene',read),patch.object(providers,'fal_wait',wait),patch.object(providers,'provider_media',side_effect=lambda u,p:p),patch('montage.assemble',assemble),patch.object(providers.studio_media,'render',return_value=(folder/'result.mp4','video/mp4')):
    providers.fal_video(data,folder,lambda *a:None,lambda:False)
   self.assertEqual(reads,[('original-a','Walk forward'),('original-b','Smile and wave')])
   self.assertEqual([p['image_url'] for _,p in payloads],['cropped-a','cropped-b'])
   self.assertEqual([p['prompt'] for _,p in payloads],['Read: Walk forward','Read: Smile and wave'])
   self.assertTrue(all(e.endswith('/image-to-video') for e,_ in payloads))
   self.assertEqual([p['duration'] for _,p in payloads],['5','5'])

 def test_custom_actions_without_ocr(self):
  with tempfile.TemporaryDirectory() as temp:
   folder=Path(temp);payloads=[]
   def wait(endpoint,payload,cancel):
    payloads.append(payload)
    if len(payloads)==2:raise ValueError('Intentional provider failure')
    return {'video':{'url':'https://fal.media/test.mp4'}}
   with patch.object(providers,'fal_wait',wait),patch.object(providers,'provider_media',side_effect=lambda u,p:p),patch.object(providers.studio_media,'render') as render,patch('montage.assemble') as assemble:
    with self.assertRaisesRegex(ValueError,'Intentional'):providers.fal_video({'allow_paid':True,'images':['a','b'],'scene_prompts':['Walk','Wave'],'duration':10},folder,lambda *a:None,lambda:False)
    self.assertEqual([p['prompt'] for p in payloads],['Walk','Wave'])
    render.assert_not_called();assemble.assert_not_called()

if __name__=='__main__':unittest.main()
