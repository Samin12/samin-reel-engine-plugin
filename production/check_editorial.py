#!/usr/bin/env python3
"""Check editorial-map structure and joins; never certify truth or semantic quality."""
import argparse
import hashlib
import json
import math
import re
from pathlib import Path

import jsonschema


def normalized(text):
    return re.findall(r'[^\W_]+', str(text).casefold().replace("'", '').replace('’', ''))


def check(map_path):
    path = Path(map_path).resolve(); errors = []; review_status = None
    result = lambda: {'mechanical_ready': not errors, 'requires_semantic_review': True,
                     'recorded_review_status': review_status, 'errors': errors,
                     'scope': 'Structure, timing, joins and render-hash freshness only; truth, fit, readability and listening are not inferred.'}
    try:
        data = json.loads(path.read_text())
        schema = json.loads(Path(__file__).with_name('editorial-map.schema.json').read_text())
        validator = jsonschema.Draft202012Validator(schema, format_checker=jsonschema.FormatChecker())
        for error in validator.iter_errors(data):
            errors.append(f"schema:{'/'.join(map(str, error.absolute_path))}: {error.message}")
        if errors: return result()
        review_status = data['review']['status']
        def load(key):
            target = (path.parent / data[key]).resolve()
            return json.loads(target.read_text())
        words_data, timeline, inventory = load('words_path'), load('timeline_path'), load('asset_index_path')
        words = words_data if isinstance(words_data, list) else words_data['words']
        shots = {s['id']: s for s in timeline['shots']}; assets = {a['id']: a for a in inventory['assets']}
        if len(shots) != len(timeline['shots']): errors.append('timeline: duplicate shot IDs')
        if len(assets) != len(inventory['assets']): errors.append('assets: duplicate asset IDs')
        if len({b['beat_id'] for b in data['beats']}) != len(data['beats']): errors.append('beats: duplicate beat IDs')
        duration = data['canvas']['duration']
        for key in ('width', 'height', 'fps'):
            if timeline.get('output', {}).get(key) != data['canvas'][key]: errors.append(f'canvas: {key} differs from timeline')
        for i, word in enumerate(words):
            a, b = word['start'], word['end']
            if not all(math.isfinite(v) for v in (a, b)) or not 0 <= a <= b <= duration + .15:
                errors.append(f'words:{i}: invalid or out-of-output timing')
        def interval(item, start, end, label):
            if not start <= item['start'] < item['end'] <= end + 1e-6:
                errors.append(f'{label}: nonpositive or outside containing interval')
        def rectangles(value, location='map'):
            if isinstance(value, dict):
                if all(k in value for k in ('x', 'y', 'width', 'height')):
                    if value['x'] + value['width'] > 1 + 1e-9 or value['y'] + value['height'] > 1 + 1e-9:
                        errors.append(f'{location}: rectangle exceeds normalized canvas')
                for k, v in value.items(): rectangles(v, location+'/'+k)
            elif isinstance(value, list):
                for i, v in enumerate(value): rectangles(v, location+'/'+str(i))
        rectangles(data)
        cursor = 0
        for beat in data['beats']:
            label = beat['beat_id']; first, last = beat['word_range']; span = beat['output_interval']
            if first != cursor or not 0 <= first < last <= len(words): errors.append(f'{label}: word ranges must cover every word once in contiguous order')
            cursor = last
            interval(span, 0, duration, label)
            if normalized(beat['spoken_text']) != normalized(' '.join(w.get('word', w.get('text', '')) for w in words[first:last])):
                errors.append(f'{label}: spoken_text differs from referenced words')
            timing = beat['timing']; anchor = timing['anchor_word_index']
            if not first <= anchor < last or not 0 <= anchor < len(words): errors.append(f'{label}: anchor word is outside beat range')
            elif abs(timing['anchor_time'] - words[anchor]['start']) > .15 + 1e-9: errors.append(f'{label}: anchor time differs from word start by more than 0.15s')
            if not 0 <= timing['reveal_time'] <= duration: errors.append(f'{label}: reveal time outside output')
            interval(timing['stable_hold'], span['start'], span['end'], label+'/stable_hold')
            if beat['assessment']['viewed_render_span'] is not None:
                interval(beat['assessment']['viewed_render_span'], 0, duration, label+'/viewed_render_span')
            shot_ids = set(beat['visual']['shot_ids'])
            for sid in shot_ids:
                if sid not in shots: errors.append(f'{label}: unknown shot {sid}')
                elif max(shots[sid]['start'], span['start']) >= min(shots[sid]['end'], span['end']): errors.append(f'{label}: shot {sid} does not overlap beat')
            for aid in beat['visual']['asset_ids']:
                if aid not in assets: errors.append(f'{label}: unknown asset {aid}')
                elif 'shot_ids' in assets[aid] and not shot_ids.intersection(assets[aid]['shot_ids']): errors.append(f'{label}: asset {aid} is not joined to a declared beat shot')
        if cursor != len(words): errors.append('beats: trailing words are not mapped')
        review = data['review']; scores = review['scores']
        expected_total = sum(s['score'] for s in scores.values()) if scores is not None else None
        if review['total_score'] != expected_total: errors.append('review: total_score does not equal component scores')
        for item in review['checked_spans']: interval(item['interval'], 0, duration, 'review/checked_span')
        for bid in review['unmapped_beat_ids'] + [i for f in review['unresolved_hard_failures'] for i in f['beat_ids']]:
            if bid not in {b['beat_id'] for b in data['beats']}: errors.append(f'review: unknown beat {bid}')
        passed = review_status == 'passed' or any(b['assessment']['status'] == 'passed' for b in data['beats'])
        if passed:
            if not review['render_path'] or not review['render_sha256']: errors.append('review: passed assessment requires render path and hash')
            else:
                render = (path.parent / review['render_path']).resolve()
                if not render.is_file() or render.stat().st_size == 0: errors.append('review: passed render is missing or empty')
                else:
                    h = hashlib.sha256()
                    with render.open('rb') as stream:
                        for block in iter(lambda: stream.read(1024*1024), b''): h.update(block)
                    if h.hexdigest() != review['render_sha256']: errors.append('review: stale approval; render SHA-256 differs')
    except (OSError, ValueError, KeyError, TypeError) as exc:
        errors.append(f'input: {type(exc).__name__}: {exc}')
    return result()


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--map', required=True, type=Path)
    ap.add_argument('--out', type=Path, help='Optional receipt path; inputs are never rewritten')
    args = ap.parse_args(); report = check(args.map); output = json.dumps(report, indent=2)+'\n'
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True); args.out.write_text(output)
    print(output, end='')
    return 0 if report['mechanical_ready'] else 1


if __name__ == '__main__': raise SystemExit(main())
