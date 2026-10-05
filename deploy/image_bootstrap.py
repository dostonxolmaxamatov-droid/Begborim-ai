"""Start a verified Shirin bundle inside the official Python Docker image.

This is an alternative to Railway's GitHub integration. Application files are
supplied as a SHA-256 checked, compressed JSON bundle in service variables.
The original GitHub source remains the canonical editable copy.
"""
import base64
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import zlib

RUNTIME_FILES = frozenset('''hf-models.js hf-models.json higgsfield.py icon.svg
index.html manifest.webmanifest montage.py providers.py server.py shirin.css
shirin.js storyboard.py studio_media.py sw.js web.css web.js'''.split())
APP_ENV = frozenset('''PATH LANG LC_ALL TZ PYTHONUNBUFFERED PORT BIND
PUBLIC_BASE_URL RAILWAY_PUBLIC_DOMAIN SHIRIN_TOKEN SHIRIN_DB SHIRIN_MEDIA
SHIRIN_WORKERS SHIRIN_MAX_IMAGES SHIRIN_MAX_SECONDS SHIRIN_MAX_UPLOAD_MB
SHIRIN_ORIGINS HF_KEY HF_API_KEY_ID HF_API_KEY_SECRET FAL_KEY OPENAI_API_KEY
OPENAI_CHAT_MODELS OPENAI_CHAT_MODEL OPENAI_IMAGE_MODEL OPENAI_TTS_MODEL
OLLAMA_URL COMFYUI_URL COMFYUI_IMAGE_WORKFLOW COMFYUI_VIDEO_WORKFLOW
GEMINI_API_KEY GEMINI_MODEL AZURE_SPEECH_KEY AZURE_SPEECH_REGION
N8N_WEBHOOK_URL N8N_WEBHOOK_TOKEN'''.split())


def decode_bundle(env):
    count = int(env.get('SHIRIN_BUNDLE_COUNT', '0'))
    expected = env.get('SHIRIN_BUNDLE_SHA256', '')
    if not 1 <= count <= 16 or not re.fullmatch('[a-f0-9]{64}', expected):
        raise ValueError('Shirin deployment bundle metadata is missing.')
    encoded = ''.join(env[f'SHIRIN_BUNDLE_{i:02d}'] for i in range(count))
    if len(encoded) > 1000000:
        raise ValueError('Shirin deployment bundle is too large.')
    packed = base64.b64decode(encoded, validate=True)
    if hashlib.sha256(packed).hexdigest() != expected:
        raise ValueError('Shirin deployment bundle checksum does not match.')
    decoder = zlib.decompressobj()
    raw = decoder.decompress(packed, 2000000)
    if not decoder.eof or decoder.unconsumed_tail or decoder.unused_data:
        raise ValueError('Shirin deployment bundle is incomplete or too large.')
    files = json.loads(raw)
    if not isinstance(files, dict) or set(files) != RUNTIME_FILES:
        raise ValueError('Shirin deployment bundle file list does not match.')
    if any(not isinstance(value, str) for value in files.values()):
        raise ValueError('Shirin deployment bundle contains an invalid file.')
    return expected, files


def materialize(env, root):
    digest, files = decode_bundle(env)
    root = Path(root)
    root.mkdir(parents=True, exist_ok=True)
    for name, content in files.items():
        target = root / name
        if target.is_symlink():
            raise ValueError('Shirin deployment target contains a symbolic link.')
        temporary = root / (name + '.new')
        if temporary.is_symlink():
            raise ValueError('Shirin deployment temporary target is invalid.')
        temporary.write_text(content, encoding='utf-8')
        temporary.replace(target)
    (root / 'bundle.sha256').write_text(digest + '\n', encoding='ascii')
    return root


def application_environment(env):
    # The reused APK builder has old signing/source variables. They must not
    # be inherited by Shirin, FFmpeg, or provider request processes.
    result = {key: value for key, value in env.items() if key in APP_ENV}
    result.setdefault('PATH', '/usr/local/bin:/usr/bin:/bin')
    result.setdefault('PYTHONUNBUFFERED', '1')
    return result


def ensure_media_tools():
    if shutil.which('ffmpeg') and shutil.which('ffprobe'):
        return
    clean = {'PATH': '/usr/local/bin:/usr/bin:/bin',
             'DEBIAN_FRONTEND': 'noninteractive', 'LANG': 'C.UTF-8'}
    subprocess.run(['apt-get', '-o', 'Acquire::Retries=2', 'update', '-qq'],
                   check=True, timeout=180, env=clean)
    subprocess.run(['apt-get', 'install', '-y', '-qq', '--no-install-recommends',
                    'ffmpeg', 'fonts-dejavu-core', 'ca-certificates'],
                   check=True, timeout=240, env=clean)
    shutil.rmtree('/var/lib/apt/lists', ignore_errors=True)
    if not shutil.which('ffmpeg') or not shutil.which('ffprobe'):
        raise RuntimeError('FFmpeg installation did not complete.')


def main():
    token = os.environ.get('SHIRIN_TOKEN', '')
    if len(token) < 32 or not token.isascii():
        raise ValueError('Set a private SHIRIN_TOKEN with at least 32 ASCII characters.')
    root = materialize(os.environ, os.environ.get('SHIRIN_APP_ROOT', '/opt/shirin'))
    ensure_media_tools()
    env = application_environment(os.environ)
    os.chdir(root)
    print('Shirin bundle verified; starting server.', flush=True)
    os.execve(sys.executable, [sys.executable, '-u', str(root / 'server.py')], env)


if __name__ == '__main__':
    main()
