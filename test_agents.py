import json
import os
import sqlite3
import tempfile
import unittest
from unittest.mock import patch
import agents
from test_server import GatewayTest

class AgentTest(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.db=self.tmp.name+'/test.db';agents.init(self.db)
        self.env=patch.dict(os.environ, {'OPENAI_API_KEY':'test-only','BEGBORIM_AGENTS_ENABLED':'1','AGENT_DAILY_CALL_LIMIT':'200'});self.env.start()
        self.thread=patch.object(agents,'start_worker');self.worker=self.thread.start()
        self.payload={'id':'12345678-12345678','prompt':'Write a simple story','agents':['agent-011','agent-021']}
    def tearDown(self):self.thread.stop();self.env.stop();self.tmp.cleanup()
    def test_catalog_is_100_unique_specialists(self):
        self.assertEqual(len(agents.CATALOG),100);self.assertEqual(len(agents.BY_ID),100)
        self.assertEqual(len({a['name'] for a in agents.CATALOG}),100)
    def test_idempotency_and_conflict(self):
        agents.submit(self.db,self.payload);agents.submit(self.db,self.payload)
        self.assertEqual(self.worker.call_count,1)
        with self.assertRaises(agents.RequestError) as ex:agents.submit(self.db,dict(self.payload,prompt='Other task'))
        self.assertEqual(ex.exception.code,409)
    def test_lifecycle_and_synthesis(self):
        agents.submit(self.db,self.payload)
        with patch.object(agents,'ask',return_value=('Result',{'input_tokens':20,'output_tokens':10})) as ask:
            agents.execute(self.db,self.payload['id'])
        run=agents.get(self.db,self.payload['id'])
        self.assertEqual(run['status'],'COMPLETED');self.assertEqual(ask.call_count,3)
        self.assertEqual(run['answer'],'Result');self.assertEqual(run['usage']['output_tokens'],30)
        self.assertIn('Specialist notes',ask.call_args.args[1])
    def test_cancel_before_provider_call(self):
        agents.submit(self.db,self.payload);agents.cancel(self.db,self.payload['id'])
        with patch.object(agents,'ask') as ask:agents.execute(self.db,self.payload['id'])
        ask.assert_not_called();self.assertEqual(agents.get(self.db,self.payload['id'])['status'],'CANCELLED')
    def test_cancel_during_call_preserves_partial_result(self):
        agents.submit(self.db,self.payload)
        def provider(*args):
            agents.cancel(self.db,self.payload['id']);return 'Partial',{'input_tokens':1,'output_tokens':1}
        with patch.object(agents,'ask',side_effect=provider) as ask:agents.execute(self.db,self.payload['id'])
        run=agents.get(self.db,self.payload['id']);self.assertEqual(ask.call_count,1)
        self.assertEqual(run['status'],'CANCELLED');self.assertEqual(len(run['results']),1)
    def test_budget_reservation_is_persistent_and_all_or_nothing(self):
        with patch.dict(os.environ,{'AGENT_DAILY_CALL_LIMIT':'2'}):
            with self.assertRaises(agents.RequestError) as ex:agents.submit(self.db,self.payload)
            self.assertEqual(ex.exception.code,429)
        self.assertEqual(agents.recent(self.db),[])
        agents.submit(self.db,self.payload);agents.init(self.db,recover=True)
        with sqlite3.connect(self.db) as db:self.assertEqual(db.execute('SELECT reserved FROM agent_budget').fetchone()[0],3)
        self.assertEqual(agents.get(self.db,self.payload['id'])['status'],'UNKNOWN')
    def test_disabled_gate_and_missing_key(self):
        for values in ({'BEGBORIM_AGENTS_ENABLED':'0'},{'OPENAI_API_KEY':''}):
            with patch.dict(os.environ,values):
                with self.assertRaises(agents.RequestError) as ex:agents.submit(self.db,self.payload)
                self.assertEqual(ex.exception.code,503)
    def test_timeout_is_not_retried(self):
        agents.submit(self.db,self.payload)
        with patch.object(agents,'ask',side_effect=TimeoutError()) as ask:agents.execute(self.db,self.payload['id'])
        self.assertEqual(ask.call_count,1);self.assertEqual(agents.get(self.db,self.payload['id'])['status'],'UNKNOWN')
    def test_invalid_agent_rejected(self):
        for ids in ([],['evil'],['agent-001','agent-001'],[{}]):
            with self.assertRaises(ValueError):agents.validate(dict(self.payload,agents=ids))
    def test_all_100_agents_supported(self):
        p=dict(self.payload,agents=list(agents.BY_ID));run=agents.submit(self.db,p)
        self.assertEqual(run['calls_reserved'],101)
    def test_no_second_active_run(self):
        agents.submit(self.db,self.payload)
        with self.assertRaises(agents.RequestError) as ex:agents.submit(self.db,dict(self.payload,id='87654321-87654321'))
        self.assertEqual(ex.exception.code,409)
    def test_transport_uses_astra_and_no_secret_in_body(self):
        import io
        fake=io.BytesIO(json.dumps({'status':'completed','output':[{'type':'message','content':[{'type':'output_text','text':'Hello'}]}],'usage':{'input_tokens':3,'output_tokens':2}}).encode())
        with patch.object(agents,'build_opener') as opener:
            opener.return_value.open.return_value=fake
            answer,usage=agents.ask('Python','Hello',2048)
            req=opener.return_value.open.call_args.args[0]
            body=json.loads(req.data)
            self.assertEqual(req.full_url,'https://api.openai.com/v1/responses')
            self.assertEqual(body['model'],'gpt-6-astra');self.assertFalse(body['store'])
            self.assertNotIn('test-only',req.data.decode());self.assertEqual(answer,'Hello')

class AgentHTTPTest(GatewayTest):
    def test_agents_routes_require_auth(self):
        for route in ('/agents','/agent-runs','/agent-runs/not-found'):
            self.assertEqual(self.req(route,auth=False)[0],401)
        self.assertEqual(self.req('/agent-runs',{},auth=False)[0],401)
        self.assertEqual(self.req('/agent-runs/12345678-12345678/cancel',{},auth=False)[0],401)
        code,data=self.req('/agents');self.assertEqual(code,200);self.assertEqual(len(data['agents']),100)
        self.assertNotIn('OPENAI_API_KEY',json.dumps(data))
    def test_run_polling_and_cancellation_routes(self):
        import server
        payload={'id':'12345678-12345678','prompt':'Test prompt','agents':['agent-001']}
        with patch.dict(os.environ,{'OPENAI_API_KEY':'test','BEGBORIM_AGENTS_ENABLED':'1'}),patch.object(agents,'start_worker'):
            code,run=self.req('/agent-runs',payload);self.assertEqual(code,200)
        self.assertEqual(self.req('/agent-runs/'+run['id'])[1]['id'],run['id'])
        self.assertEqual(self.req('/agent-runs/'+run['id']+'/cancel',{})[1]['status'],'CANCELLING')
        self.assertEqual(len(self.req('/agent-runs')[1]['runs']),1)

if __name__=='__main__':unittest.main()
