#!/usr/bin/env python3
"""Download an authorized large media URL in verified, resumable byte ranges.

Resolve the URL with the provider first; pass it in an untracked owner-only file.
The URL is never written to receipts or logs. Completed ranges survive retries.
"""
import argparse
import concurrent.futures
import hashlib
import json
import os
import time
from pathlib import Path
from urllib.parse import urlsplit
import requests


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--url-file', required=True)
    ap.add_argument('--output', required=True)
    ap.add_argument('--size', type=int, required=True)
    ap.add_argument('--prefix-file')
    ap.add_argument('--workers', type=int, default=3)
    ap.add_argument('--chunk-mb', type=int, default=32)
    a = ap.parse_args()
    url = Path(a.url_file).read_text().strip()
    parsed = urlsplit(url)
    if parsed.scheme != 'https' or parsed.username or parsed.password:
        raise ValueError('An authorized HTTPS media URL is required')
    out = Path(a.output).resolve(); out.parent.mkdir(parents=True, exist_ok=True)
    partial = out.with_suffix(out.suffix + '.incomplete')
    statepath = out.with_suffix(out.suffix + '.ranges.json')
    if out.exists():
        raise ValueError('Output already exists; verify it rather than overwriting it')
    chunk = a.chunk_mb * 1024 * 1024
    if statepath.exists():
        state = json.loads(statepath.read_text())
        if state['size'] != a.size or state['chunk'] != chunk or not partial.exists():
            raise ValueError('Resume parameters or partial file do not match')
    else:
        prefix = Path(a.prefix_file) if a.prefix_file else None
        start = prefix.stat().st_size if prefix and prefix.exists() else 0
        if start > a.size: raise ValueError('Prefix exceeds expected source size')
        if prefix and prefix.exists(): prefix.rename(partial)
        else: partial.touch(exist_ok=False)
        state = {'size': a.size, 'chunk': chunk, 'prefix_bytes': start, 'completed': []}
        statepath.write_text(json.dumps(state, indent=2))
    fd = os.open(partial, os.O_RDWR)
    os.ftruncate(fd, a.size)
    def get_range(start):
        end = min(start + chunk, a.size) - 1
        expected = f'bytes {start}-{end}/{a.size}'
        for attempt in range(4):
            try:
                with requests.get(url, headers={'Range': f'bytes={start}-{end}', 'Accept-Encoding': 'identity'}, stream=True, timeout=(20, 40)) as r:
                    if r.status_code != 206 or r.headers.get('Content-Range') != expected:
                        raise ValueError(f'Unexpected byte-range response {r.status_code}')
                    offset = start
                    for data in r.iter_content(1024 * 1024):
                        if offset + len(data) > end + 1: raise ValueError('Range overflow')
                        written = 0
                        while written < len(data):
                            written += os.pwrite(fd, data[written:], offset + written)
                        offset += len(data)
                    if offset != end + 1: raise ValueError('Incomplete byte range')
                    return start, end
            except (requests.RequestException, ValueError):
                if attempt == 3: raise RuntimeError(f'Range {start}-{end} failed after 4 attempts') from None
                time.sleep(attempt + 1)
    starts = [s for s in range(state['prefix_bytes'], a.size, chunk) if s not in state['completed']]
    try:
        with concurrent.futures.ThreadPoolExecutor(max_workers=max(1,min(a.workers,6))) as pool:
            for start, end in pool.map(get_range, starts):
                state['completed'].append(start)
                tmp = statepath.with_suffix('.tmp'); tmp.write_text(json.dumps(state, indent=2)); tmp.replace(statepath)
                done = state['prefix_bytes'] + sum(min(chunk, a.size-s) for s in state['completed'])
                print(f'Verified {done}/{a.size} bytes ({done/a.size:.1%})', flush=True)
        os.fsync(fd)
    finally:
        os.close(fd)
    digest = hashlib.sha256()
    with partial.open('rb') as f:
        for data in iter(lambda: f.read(8*1024*1024), b''): digest.update(data)
    partial.replace(out)
    state['complete'] = True; state['sha256'] = digest.hexdigest()
    statepath.write_text(json.dumps(state, indent=2))
    print(json.dumps({'complete':True,'bytes':a.size,'sha256':state['sha256'],'path':str(out)}))


if __name__ == '__main__': main()
