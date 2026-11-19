#!/usr/bin/env python3
"""Verify that the live public game contains the latest complete voice package."""
import hashlib
import json
import os
import re
import sys
import urllib.request
from pathlib import Path

root=Path(__file__).resolve().parent.parent
local=(root/'index.html').read_bytes()
url=os.environ.get('STARWHIM_URL','https://starwhim-island.vercel.app')
req=urllib.request.Request(url,headers={'User-Agent':'StarwhimDeliveryAudit/1.0','Cache-Control':'no-cache'})
with urllib.request.urlopen(req,timeout=30) as response:
    remote=response.read()
    code=response.status
if code!=200:
    raise SystemExit(f'Production server returned HTTP {code}')
remote_text=remote.decode('utf-8')
def voice_count(t):
    match=re.search(r'window\.StarwhimVoicePack\s*=\s*({.*?});\s*</script>',t,re.S)
    if not match:return 0
    return len(json.loads(match.group(1)).get('audio',{}))
local_count=voice_count(local.decode('utf-8'))
remote_count=voice_count(remote_text)
print('Local version:',len(local),'bytes,',local_count,'voice clips')
print('Production version:',len(remote),'bytes,',remote_count,'voice clips')
print('Local SHA256:',hashlib.sha256(local).hexdigest())
print('Production SHA256:',hashlib.sha256(remote).hexdigest())
if remote_count!=local_count or remote_count<194:
    raise SystemExit('STALE PRODUCTION: missing latest 194-recording package')
if hashlib.sha256(remote).digest()!=hashlib.sha256(local).digest():
    raise SystemExit('STALE PRODUCTION: production content differs from current main/index.html')
print('PASS production exactly matches the completed narrated game')
