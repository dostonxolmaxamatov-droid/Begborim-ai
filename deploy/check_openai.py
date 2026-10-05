"""Read-only deploy gate: validate OpenAI auth/models without generation.

Only fixed status messages and validated model identifiers are printed.
Credentials and provider response bodies must never be logged.
"""
import json
import os
import re
import sys
from urllib.error import HTTPError, URLError
from urllib.request import Request, build_opener, HTTPRedirectHandler


class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, *args, **kwargs):
        return None


def check():
    key = os.environ.get('OPENAI_API_KEY', '').strip()
    if not key or key.startswith('${{'):
        print('OPENAI_CHECK: credential missing or unresolved', flush=True)
        return 1
    names = {}
    for role, variable in (
        ('chat', 'OPENAI_CHAT_MODEL'),
        ('image', 'OPENAI_IMAGE_MODEL'),
        ('voice', 'OPENAI_TTS_MODEL'),
    ):
        value = os.environ.get(variable, '').strip()
        if not re.fullmatch(r'[A-Za-z0-9_.:/-]{1,120}', value):
            print('OPENAI_CHECK: invalid model setting for ' + role, flush=True)
            return 1
        names[role] = value
    req = Request('https://api.openai.com/v1/models',
                  headers={'Authorization': 'Bearer ' + key})
    try:
        with build_opener(NoRedirect).open(req, timeout=30) as response:
            payload = json.loads(response.read(4 * 1024 * 1024))
    except HTTPError as error:
        print('OPENAI_CHECK: provider HTTP ' + str(error.code), flush=True)
        return 1
    except (URLError, TimeoutError, ValueError, OSError):
        print('OPENAI_CHECK: provider connection or response failed', flush=True)
        return 1
    if not isinstance(payload, dict) or not isinstance(payload.get('data'), list):
        print('OPENAI_CHECK: invalid model catalog', flush=True)
        return 1
    available = {row.get('id') for row in payload['data'] if isinstance(row, dict)}
    print('OPENAI_CHECK: credential accepted; no generation requested', flush=True)
    missing = False
    for role, name in names.items():
        found = name in available
        print('OPENAI_CHECK: ' + role + ' ' + name +
              (' available' if found else ' unavailable'), flush=True)
        missing |= not found
    print('OPENAI_CHECK: generation billing/quota not tested', flush=True)
    return int(missing)


if __name__ == '__main__':
    sys.exit(check())
