import json
import os
import tempfile
import threading
import unittest
import urllib.request
import urllib.error
from unittest.mock import patch
import server

class GatewayTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        server.DB = os.path.join(self.tmp.name, 'test.sqlite')
        server.TOKEN = 'x' * 40
        server.KEY = 'test-only'
        server.init_db()
        self.http = server.ThreadingHTTPServer(('127.0.0.1', 0), server.Handler)
        threading.Thread(target=self.http.serve_forever, daemon=True).start()
        self.base = 'http://127.0.0.1:' + str(self.http.server_port)

    def test_non_ascii_authorization_returns_401(self):
        for path, data in [('/health', None), ('/jobs', b'{}')]:
            request = urllib.request.Request(self.base + path, data=data,
                headers={'Authorization': 'Bearer caf\xe9', 'Content-Type': 'application/json'})
            with self.assertRaises(urllib.error.HTTPError) as result:
                urllib.request.urlopen(request)
            self.assertEqual(result.exception.code, 401)
            self.assertEqual(json.load(result.exception)['error'], 'Ulanish kodi noto‘g‘ri.')
        self.assertEqual(self.req('/health')[0], 200)

    def tearDown(self):
        self.http.shutdown()
        self.http.server_close()
        self.tmp.cleanup()

    def req(self, path, data=None, auth=True):
        headers = {'Content-Type': 'application/json'}
        if auth:
            headers['Authorization'] = 'Bearer ' + server.TOKEN
        r = urllib.request.Request(self.base + path, data=None if data is None else json.dumps(data).encode(), headers=headers)
        try:
            with urllib.request.urlopen(r) as out:
                return out.status, json.load(out)
        except urllib.error.HTTPError as e:
            return e.code, json.load(e)

    def test_hosting_probe_keeps_private_routes_protected(self):
        self.assertEqual(self.req('/healthz', auth=False), (200, {'ok': True}))
        for route in ('/health', '/jobs'):
            self.assertEqual(self.req(route, auth=False)[0], 401)

    def test_auth_and_missing_provider(self):
        self.assertEqual(self.req('/jobs', auth=False)[0], 401)
        server.KEY = ''
        self.assertFalse(self.req('/health')[1]['configured'])
        self.assertEqual(self.req('/jobs', {})[0], 503)

    def test_full_job_lifecycle_and_idempotency(self):
        submission = {'request_id': 'provider-1', 'status_url': 'https://queue.fal.run/model/requests/1/status', 'response_url': 'https://queue.fal.run/model/requests/1'}
        payload = {'id': '12345678-12345678', 'kind': 'image', 'prompt': 'Red tractor', 'ratio': '9:16'}
        with patch.object(server, 'fal', return_value=submission) as fake:
            self.assertEqual(self.req('/jobs', payload)[1]['status'], 'IN_QUEUE')
            self.req('/jobs', payload)
            self.assertEqual(fake.call_count, 1)
            self.assertEqual(self.req('/jobs', dict(payload, id='87654321-12345678'))[0], 409)
        with patch.object(server, 'fal', side_effect=[{'status': 'COMPLETED'}, {'images': [{'url': 'https://example.com/result.jpg'}]}]):
            code, result = self.req('/jobs/' + payload['id'])
            self.assertEqual(result['status'], 'COMPLETED')
            self.assertNotIn('status_url', result)
            self.assertTrue(result['url'].endswith('.jpg'))

    def test_unknown_submission_blocks_retry(self):
        payload = {'id': '12345678-12345678', 'kind': 'text_video', 'prompt': 'Red tractor'}
        with patch.object(server, 'fal', side_effect=TimeoutError()):
            self.assertEqual(self.req('/jobs', payload)[1]['status'], 'UNKNOWN')
        self.assertEqual(self.req('/jobs', dict(payload, id='87654321-12345678'))[0], 409)

    def test_validation_and_key_destination(self):
        self.assertEqual(self.req('/jobs', {'kind': 'invalid'})[0], 400)
        self.assertEqual(self.req('/jobs', {'kind': 'image_video', 'prompt': 'tractor', 'image': 'http://localhost'})[0], 400)
        with self.assertRaises(ValueError):
            server.fal('https://attacker.example/steal')
        kind, inp = server.validate({'kind': 'text_video', 'prompt': 'A tractor', 'ratio': '9:16', 'duration': '10'})
        self.assertEqual(inp['aspect_ratio'], '9:16')
        self.assertEqual(inp['duration'], '10')

if __name__ == '__main__':
    unittest.main()
