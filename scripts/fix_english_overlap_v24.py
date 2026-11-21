#!/usr/bin/env python3
"""Prevent an already playing Chinese girl narrator overlapping en-US word lessons."""
from pathlib import Path
root=Path(__file__).resolve().parent.parent
before="    if(lastVoice){lastVoice.pause();lastVoice=null;}"
after="""    window.StarwhimChineseNarratorV23?.stop?.();
    S.audio?.stopSpeech?.();
    if(lastVoice){lastVoice.pause();lastVoice=null;}"""
for f in [root/'index.html',root/'scripts/learning_v22.js']:
    s=f.read_text(encoding='utf-8')
    if after in s:
        print('ALREADY FIXED',f.name)
        continue
    if s.count(before)!=1:
        raise RuntimeError(f'{f}: expected a single English voice entry point, found {s.count(before)}')
    s=s.replace(before,after,1)
    f.write_text(s,encoding='utf-8')
    print('FIXED',f.name)
