import base64, json, os, tempfile, unittest
from pathlib import Path
from unittest.mock import patch
import higgsfield as h, server
PNG=base64.b64decode('iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVQIHWP4z8DwHwAFgAI/ScLbtAAAAABJRU5ErkJggg==')
DATA='data:image/png;base64,'+base64.b64encode(PNG).decode()
class HiggsfieldTests(unittest.TestCase):
 def payload(self,model='seedance25-i2v'):
  m=h.MODELS[model];params={f['key']:f['default'] for f in m['fields'] if 'default' in f}
  for f in m['fields']:
   if f.get('required'):params[f['key']]=[DATA] if f['type']=='images' else 'data:video/mp4;base64,AAAA' if f['type']=='video' else DATA if f['type']=='image' else 'A person waves.'
  return {'id':'abcd1234-abcd-1234-abcd-1234abcd1234','kind':'hf_'+m['type'],'hf_model':model,'hf_params':params,'allow_paid':True,'video_intent':'animation' if m['type']=='video' else None}
 def test_all_catalog_payloads_validate(self):
  for model in h.MODELS:h.validate(self.payload(model))
 def test_missing_image_not_dropped(self):
  d=self.payload();del d['hf_params']['image_url']
  with self.assertRaisesRegex(ValueError,'rasm'):h.validate(d)
 def test_paid_gate_and_type(self):
  d=self.payload();d['allow_paid']=False
  with self.assertRaises(ValueError):h.validate(d)
  d['allow_paid']=True;d['kind']='hf_image'
  with self.assertRaises(ValueError):h.validate(d)
 def test_invalid_parameters(self):
  for key,value in [('duration',31),('duration',float('nan')),('resolution','4k')]:
   d=self.payload();d['hf_params'][key]=value
   with self.assertRaises(ValueError):h.validate(d)
 def test_hf_animation_kind_allowed_and_montage_rejected(self):
  server.validated(self.payload())
  d=self.payload();d['kind']='montage'
  with self.assertRaises(ValueError):server.validated(d)
 def test_missing_credentials_no_job(self):
  with tempfile.TemporaryDirectory() as t,patch.object(server,'DB',t+'/db'),patch.object(server,'MEDIA',Path(t)/'media'),patch.dict(os.environ,{'HF_KEY':'','HF_API_KEY_ID':'','HF_API_KEY_SECRET':''}):
   server.init_db()
   with self.assertRaisesRegex(ValueError,'HF_KEY'):server.submit(self.payload())
   self.assertIsNone(server.get_job(self.payload()['id']))
 def test_credentials_api_origin_idempotency(self):
  with patch.dict(os.environ,{'HF_KEY':'test-id:test-secret'}),patch.object(h,'transport',return_value={'status':'queued'}) as send:
   h.api('/higgsfield-ai/soul/v2/standard',{'prompt':'test'},key='test-job')
   args=send.call_args.args;self.assertEqual(args[2]['Authorization'],'Key test-id:test-secret');self.assertEqual(args[2]['Idempotency-Key'],'test-job')
   with self.assertRaises(ValueError):h.api('https://outside.example/requests/x/status')
   self.assertEqual(send.call_count,1)
 def test_upload_no_secret_at_storage(self):
  ticket={'upload_url':'https://storage.example/upload?signature=dummy','public_url':'https://cdn.example/image.png','upload_headers':{'Content-Type':'image/png','x-amz-tagging':'retention=temporary'}}
  with patch.object(h,'api',return_value=ticket),patch.object(h,'public_url',side_effect=lambda x:x),patch.object(h,'transport',return_value=b'') as put:
   self.assertEqual(h.upload(DATA),ticket['public_url']);args=put.call_args.args;self.assertEqual(args[1],PNG);self.assertNotIn('Authorization',args[2]);self.assertEqual(put.call_args.kwargs['method'],'PUT')
 def test_private_media_rejected(self):
  with patch.object(h.socket,'getaddrinfo',return_value=[(2,1,6,'',('127.0.0.1',443))]):
   with self.assertRaises(ValueError):h.public_url('https://local.example/a')
 def test_completed_image_and_receipt(self):
  receipt={'status':'queued','request_id':'provider-1','status_url':h.API+'/requests/provider-1/status','cancel_url':h.API+'/requests/provider-1/cancel'}
  done={'status':'completed','images':[{'url':'https://cdn.example/out.png'}]}
  with tempfile.TemporaryDirectory() as t,patch.object(h,'ready',return_value=True),patch.object(h,'api',side_effect=[receipt,done]) as api,patch.object(h.time,'sleep'),patch.object(h,'public_url',side_effect=lambda x:x),patch.object(h,'transport',return_value=PNG):
   p,mime=h.generate(self.payload('soul-v2'),t,lambda *a:None,lambda:False)
   self.assertEqual(p.read_bytes(),PNG);self.assertEqual(mime,'image/png');self.assertTrue((Path(t)/'hf-receipt.json').is_file());self.assertEqual(api.call_count,2);self.assertEqual(api.call_args_list[0].kwargs['key'],'shirin-'+self.payload()['id'])
 def test_wrong_output_type_rejected(self):
  receipt={'status':'completed','request_id':'p','status_url':h.API+'/requests/p/status','cancel_url':h.API+'/requests/p/cancel','images':[{'url':'https://cdn.example/p.png'}]}
  with tempfile.TemporaryDirectory() as t,patch.object(h,'ready',return_value=True),patch.object(h,'api',return_value=receipt),patch.object(h,'upload',return_value='https://cdn.example/input.png'):
   with self.assertRaisesRegex(ValueError,'kutilgan turdagi'):h.generate(self.payload(),t,lambda *a:None,lambda:False)
 def test_provider_failure_no_fallback(self):
  with tempfile.TemporaryDirectory() as t,patch.object(h,'ready',return_value=True),patch.object(h,'api',side_effect=ValueError('Provider failed')) as send:
   with self.assertRaisesRegex(ValueError,'Provider failed'):h.generate(self.payload('soul-v2'),t,lambda *a:None,lambda:False)
   self.assertEqual(send.call_count,1);self.assertFalse(list(Path(t).iterdir()))
if __name__=='__main__':unittest.main()
