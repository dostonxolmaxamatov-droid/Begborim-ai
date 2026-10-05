import base64
import hashlib
import json
import os
from pathlib import Path
import secrets
import shlex
import socket
import subprocess
import sys
import tempfile
import time
import unittest
import urllib.error
import urllib.request
import zlib

import image_bootstrap as bootstrap
from package_image import package

ROOT = Path(__file__).resolve().parents[1]


class ImageDeploymentTests(unittest.TestCase):
    def setUp(self):
        self.bundle = package(ROOT)

    def test_bundle_is_identical_to_runtime_source(self):
        with tempfile.TemporaryDirectory() as folder:
            bootstrap.materialize(self.bundle['variables'], folder)
            for name in bootstrap.RUNTIME_FILES:
                self.assertEqual((Path(folder)/name).read_bytes(),
                                 (ROOT/'server'/name).read_bytes())

    def test_corruption_is_rejected_before_writing(self):
        env = dict(self.bundle['variables'])
        env['SHIRIN_BUNDLE_SHA256'] = '0' * 64
        with tempfile.TemporaryDirectory() as folder:
            with self.assertRaisesRegex(ValueError, 'checksum'):
                bootstrap.materialize(env, folder)
            self.assertEqual(list(Path(folder).iterdir()), [])

    def test_unexpected_file_path_is_rejected(self):
        env = dict(self.bundle['variables'])
        _, files = bootstrap.decode_bundle(env)
        files['../outside.py'] = 'bad'
        packed = zlib.compress(json.dumps(files).encode())
        env.update(SHIRIN_BUNDLE_COUNT='1',
                   SHIRIN_BUNDLE_00=base64.b64encode(packed).decode(),
                   SHIRIN_BUNDLE_SHA256=hashlib.sha256(packed).hexdigest())
        with self.assertRaisesRegex(ValueError, 'file list'):
            bootstrap.decode_bundle(env)

    def test_legacy_apk_secrets_are_not_inherited(self):
        env = bootstrap.application_environment({'PATH':'/usr/bin',
            'SHIRIN_TOKEN':'test-token','HF_KEY':'test:key',
            'KEYSTORE_B64':'private-signing-key','APP_TOKEN':'old-token',
            'SHIRIN_BOOT_B64':'source','SRC00':'old-code'})
        self.assertEqual(env['HF_KEY'], 'test:key')
        for name in ('KEYSTORE_B64','APP_TOKEN','SHIRIN_BOOT_B64','SRC00'):
            self.assertNotIn(name, env)

    def test_actual_start_command_auth_and_missing_provider(self):
        with tempfile.TemporaryDirectory() as folder, socket.socket() as sock:
            sock.bind(('127.0.0.1', 0))
            port = sock.getsockname()[1]
            sock.close()
            token = secrets.token_urlsafe(32)
            env = {**os.environ, **self.bundle['variables'],
                   'SHIRIN_APP_ROOT':folder+'/app',
                   'SHIRIN_DB':folder+'/data/jobs.sqlite3',
                   'SHIRIN_MEDIA':folder+'/data/media',
                   'SHIRIN_TOKEN':token,'BIND':'127.0.0.1','PORT':str(port)}
            for name in ('HF_KEY','HF_API_KEY_ID','HF_API_KEY_SECRET',
                         'OPENAI_API_KEY','FAL_KEY','OLLAMA_URL','COMFYUI_URL'):
                env.pop(name, None)
            command = shlex.split(self.bundle['startCommand'])
            command[0] = sys.executable
            proc = subprocess.Popen(command, env=env, stdout=subprocess.DEVNULL,
                                    stderr=subprocess.PIPE)
            try:
                url = f'http://127.0.0.1:{port}'
                for _ in range(50):
                    try:
                        with urllib.request.urlopen(url+'/healthz', timeout=1) as r:
                            self.assertTrue(json.load(r)['ok'])
                        break
                    except (OSError, urllib.error.URLError):
                        if proc.poll() is not None:
                            self.fail('Server failed: '+proc.stderr.read().decode()[:500])
                        time.sleep(.05)
                else:
                    self.fail('Server healthcheck timed out')
                with self.assertRaises(urllib.error.HTTPError) as failure:
                    urllib.request.urlopen(url+'/health', timeout=2)
                self.assertEqual(failure.exception.code, 401)
                request = urllib.request.Request(url+'/health',
                    headers={'Authorization':'Bearer '+token})
                with urllib.request.urlopen(request, timeout=2) as r:
                    health = json.load(r)
                self.assertEqual(health['name'], 'Shirin AI')
                self.assertTrue(health['montage'])
                self.assertFalse(health['higgsfield']['configured'])
                with urllib.request.urlopen(url+'/', timeout=2) as r:
                    self.assertIn(b'shirin', r.read().lower())
            finally:
                proc.terminate()
                try:
                    proc.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    proc.kill()
                    proc.wait(timeout=5)
                proc.stderr.close()


if __name__ == '__main__':
    unittest.main()
