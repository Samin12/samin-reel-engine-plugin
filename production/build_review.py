#!/usr/bin/env python3
"""Package aligned versions of one script for synchronized local playback review."""
import argparse
import hashlib
import html
import json
import math
from pathlib import Path
import shutil
import subprocess


def duration(path):
    data = json.loads(subprocess.check_output([
        'ffprobe', '-v', 'error', '-show_streams', '-of', 'json', str(path)]))
    return next(float(s['duration']) for s in data['streams'] if s['codec_type'] == 'video')


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--reference', required=True, type=Path)
    ap.add_argument('--candidate', required=True, type=Path)
    ap.add_argument('--out', required=True, type=Path)
    ap.add_argument('--title', default='Reel comparison')
    ap.add_argument('--moments', type=Path, help='JSON list of {time, label} review anchors')
    a = ap.parse_args()
    sources = [p.resolve(strict=True) for p in [a.reference, a.candidate]]
    if any(p.suffix.lower() != '.mp4' for p in sources):
        ap.error('This player requires MP4 inputs')
    durations = [duration(p) for p in sources]
    if any(not math.isfinite(d) or d <= 0 for d in durations):
        ap.error('Invalid video duration')
    if abs(durations[0] - durations[1]) > .15:
        ap.error('Use aligned versions of the same script; video durations differ by more than 0.15s')
    end = min(durations)
    moments = json.loads(a.moments.read_text()) if a.moments else []
    if not isinstance(moments, list):
        ap.error('Moments must be a list')
    for item in moments:
        if (not isinstance(item, dict) or not isinstance(item.get('label'), str)
            or not isinstance(item.get('time'), (int, float))
            or not math.isfinite(item['time']) or not 0 <= item['time'] < end):
            ap.error('Every moment needs a label and a finite time inside the video')
    a.out.mkdir(parents=True, exist_ok=False)
    artifacts = []
    for source, name, seconds in zip(sources, ['reference.mp4', 'candidate.mp4'], durations):
        target = a.out / name
        shutil.copy2(source, target)
        with target.open('rb') as media:
            digest = hashlib.file_digest(media, 'sha256').hexdigest()
        artifacts.append({'path': name, 'duration_seconds': seconds, 'bytes': target.stat().st_size,
                          'sha256': digest})
    template = Path(__file__).with_name('review-player.html').read_text()
    seconds = math.ceil(end)
    clock = f'{seconds // 60}:{seconds % 60:02}'
    buttons = ''.join(f'<button data-time="{m["time"]}">{html.escape(m["label"])}</button>' for m in moments)
    for token, value in {'TITLE': html.escape(a.title), 'DURATION': str(end),
                         'CLOCK': clock, 'MOMENTS': buttons}.items():
        template = template.replace(f'@@{token}@@', value)
    (a.out / 'index.html').write_text(template)
    receipt = {'purpose': 'Synchronized playback for editorial comparison', 'assets': artifacts,
               'same_script_alignment': 'Must be established by the editor; equal duration alone is not proof',
               'moments': moments, 'whole_render_watched_with_sound': False,
               'editorial_approval': 'pending', 'open': 'index.html'}
    (a.out / 'review-manifest.json').write_text(json.dumps(receipt, indent=2) + '\n')
    print(json.dumps({'review': str((a.out / 'index.html').resolve()), 'assets': artifacts}, indent=2))


if __name__ == '__main__':
    main()
