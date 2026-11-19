#!/usr/bin/env python3
"""Cloud-only F5-TTS generation using the already embedded user-supplied reference MP3.

Uses CPU on GitHub Actions; no user machine, Tencent/Voxy credential or paid API.
This is an approximate voice clone, NOT Voxy's officially generated voice.
"""
import argparse
import base64
import json
import os
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
REF_TEXT = (
    '丁一一小朋友，你好呀！我是泡泡。欢迎来到星绒岛！'
    '瞧，云朵像棉花糖一样软软的。我们一起去寻找亮晶晶的小星星，好不好呀？'
)


def load_reference():
    html = (ROOT / 'index.html').read_text(encoding='utf-8')
    match = re.search(r'window\.StarwhimVoicePack\s*=\s*({.*?});\s*</script>', html, re.S)
    if not match:
        raise RuntimeError('Game voice pack missing')
    pack = json.loads(match.group(1))
    uri = next((value for value in pack.get('audio', {}).values()
                if isinstance(value, str) and value.startswith('data:audio/mpeg;base64,')), None)
    if uri is None:
        raise RuntimeError('Original user MP3 is not embedded in index.html')
    raw = base64.b64decode(uri.partition(',')[2])
    if len(raw) < 40000:
        raise RuntimeError('Unexpectedly small reference recording')
    reference = ROOT / 'generated' / 'original.wav'
    reference.parent.mkdir(exist_ok=True, parents=True)
    mp3 = ROOT / 'generated' / 'original.mp3'
    mp3.write_bytes(raw)
    subprocess.run(['ffmpeg', '-y', '-hide_banner', '-loglevel', 'error', '-i', str(mp3),
                    '-ac', '1', '-ar', '24000', str(reference)], check=True)
    return reference


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--shard', type=int, default=0)
    parser.add_argument('--shards', type=int, default=4)
    parser.add_argument('--limit', type=int, default=0, help='Generate only first N assigned clips for smoke testing')
    parser.add_argument('--extra-plan', action='store_true', help='Use supplemental game voice manifest')
    parser.add_argument('--manifest', default='', help='Explicit JSON manifest filename')
    args = parser.parse_args()
    if args.shard < 0 or args.shard >= args.shards:
        parser.error('shard out of range')
    manifest = args.manifest or ('voice-extra-plan.json' if args.extra_plan else 'voice-plan.json')
    plan = json.loads((ROOT / manifest).read_text(encoding='utf-8'))['lines']
    picked = [(n, r) for n, r in enumerate(plan) if n % args.shards == args.shard]
    if args.limit > 0:
        picked = picked[:args.limit]
    ref = load_reference()
    import torch
    torch.set_num_threads(max(1, min(4, os.cpu_count() or 1)))
    from f5_tts.api import F5TTS
    tts = F5TTS(model='F5TTS_v1_Base', device='cpu')
    saved = []
    for count, (number, row) in enumerate(picked, start=1):
        out_wav = ROOT / 'generated' / (row['id'] + '.wav')
        out_mp3 = ROOT / 'generated' / (row['id'] + '.mp3')
        if out_mp3.is_file() and out_mp3.stat().st_size > 500:
            saved.append(row['id'])
            continue
        print(f'[{count}/{len(picked)}] #{number} {row["context"]} {row["text"][:30]}', flush=True)
        tts.infer(ref_file=str(ref), ref_text=REF_TEXT, gen_text=row['text'],
                  file_wave=str(out_wav), nfe_step=16, seed=20261118 + number, speed=1.04,
                  show_info=lambda *arg, **kwargs: None)
        subprocess.run(['ffmpeg', '-y', '-hide_banner', '-loglevel', 'error',
                        '-i', str(out_wav), '-ac', '1', '-ar', '24000',
                        '-codec:a', 'libmp3lame', '-b:a', '56k', str(out_mp3)], check=True)
        if out_mp3.stat().st_size < 500:
            raise RuntimeError(f'Empty audio for {row["id"]}')
        out_wav.unlink(missing_ok=True)
        saved.append(row['id'])
    report = {'shard': args.shard, 'expected': len(picked), 'generated': len(saved), 'ids': saved}
    (ROOT / 'generated' / f'report-{args.shard}.json').write_text(json.dumps(report, ensure_ascii=False), encoding='utf-8')
    print(f'Completed shard {args.shard}: {len(saved)}/{len(picked)}', flush=True)


if __name__ == '__main__':
    main()