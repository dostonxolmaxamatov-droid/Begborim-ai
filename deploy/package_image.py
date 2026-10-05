"""Create deterministic Railway variables from the checked-in runtime files.

Output contains source code, never credentials. Set SHIRIN_TOKEN separately.
"""
import base64
import hashlib
import json
from pathlib import Path
import shlex
import sys
import zlib

from image_bootstrap import RUNTIME_FILES


def package(root):
    root = Path(root)
    files = {name: (root / 'server' / name).read_text(encoding='utf-8')
             for name in sorted(RUNTIME_FILES)}
    packed = zlib.compress(json.dumps(files, ensure_ascii=False,
                                     separators=(',', ':')).encode(), 9)
    encoded = base64.b64encode(packed).decode('ascii')
    chunks = [encoded[i:i+12000] for i in range(0, len(encoded), 12000)]
    boot = (root / 'deploy' / 'image_bootstrap.py').read_bytes()
    digest = hashlib.sha256(boot).hexdigest()
    loader = ('import base64,hashlib,os\n'
              'b=base64.b64decode(os.environ["SHIRIN_BOOT_B64"],validate=True)\n'
              f'if hashlib.sha256(b).hexdigest()!="{digest}":\n'
              ' raise SystemExit("Bootstrap checksum mismatch")\n'
              'exec(compile(b,"shirin_bootstrap.py","exec"))')
    return {'image': 'python:3.12-slim-bookworm',
            'startCommand': 'python -u -c ' + shlex.quote(loader),
            'variables': {
                **{f'SHIRIN_BUNDLE_{i:02d}': value for i, value in enumerate(chunks)},
                'SHIRIN_BUNDLE_COUNT': str(len(chunks)),
                'SHIRIN_BUNDLE_SHA256': hashlib.sha256(packed).hexdigest(),
                'SHIRIN_BOOT_B64': base64.b64encode(boot).decode('ascii'),
                'BIND': '0.0.0.0', 'PORT': '8080', 'PYTHONUNBUFFERED': '1',
                'SHIRIN_DB': '/data/shirin.sqlite3', 'SHIRIN_MEDIA': '/data/media',
                'SHIRIN_WORKERS': '1', 'SHIRIN_MAX_UPLOAD_MB': '32'
            }}


if __name__ == '__main__':
    print(json.dumps(package(Path(__file__).resolve().parents[1])))
