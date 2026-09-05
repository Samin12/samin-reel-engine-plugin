#!/usr/bin/env python3
"""Retime an existing supported edit after reviewed 1x pause removals.

Run prepare_take.py first. Supply its new video/word files and a JSON document
with source_duration and cuts [{start,end}] on the OLD output clock. Add music
after this operation. Review internal B-roll actions again: shortening a shot
does not time-warp its source video or retime baked-in visual events.
"""
import argparse
import copy
import json
import math
from pathlib import Path


def retime(spec, decision, source, words):
    spec = copy.deepcopy(spec)
    if spec.get('music'):
        raise ValueError('Remove/replan music after speech retiming; never chop the music bed with word gaps')
    total = float(decision['source_duration'])
    cuts = decision['cuts']
    cursor = 0
    for cut in cuts:
        a, b = float(cut['start']), float(cut['end'])
        if not all(map(math.isfinite, [a, b, total])) or not cursor <= a < b <= total:
            raise ValueError('Cuts must be ordered, disjoint, finite and within source duration')
        cursor = b
    old_duration = sum(float(s['end'])-float(s['start']) for s in spec['source']['segments'])
    if abs(old_duration-total) > 0.001:
        raise ValueError('Cut clock does not match the old timeline duration')

    def t(value):
        value = float(value)
        return value - sum(max(0, min(value, c['end'])-c['start']) for c in cuts)

    duration = t(total)
    for collection in ('shots', 'labels'):
        for item in spec.get(collection, []):
            item['start'], item['end'] = t(item['start']), t(item['end'])
            if item['end'] <= item['start']:
                raise ValueError(f'{collection} item was entirely removed; make an editorial decision')
    for collection in ('zooms', 'flashes'):
        for item in spec.get(collection, []):
            at = float(item['at'])
            if 'duration' in item:
                item['duration'] = t(at + item['duration']) - t(at)
                if item['duration'] <= 0:
                    raise ValueError(f'{collection} event was entirely removed; re-author it')
            item['at'] = t(at)
    # SFX maintain their natural duration; only the onset follows the new clock.
    for sound in spec.get('sfx', []):
        sound['at'] = t(sound['at'])
    spec['source']['path'] = str(Path(source).resolve())
    spec['source']['segments'] = [{'start': 0, 'end': duration}]
    spec['words_path'] = str(Path(words).resolve())
    spec['retime_review'] = {
        'removed_seconds': total-duration, 'cut_count': len(cuts),
        'speech_speed': 1, 'baked_visual_actions': 'must recheck against retimed speech',
        'music': 'add continuous bed on final clock',
        'captions': 'rebuilt from supplied retimed words; phrase word ranges preserved'
    }
    return spec


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ('spec', 'cuts', 'source', 'words', 'output'):
        parser.add_argument('--'+name, required=True, type=Path)
    args = parser.parse_args()
    result = retime(json.loads(args.spec.read_text()), json.loads(args.cuts.read_text()), args.source, args.words)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2)+'\n')
    print(json.dumps(result['retime_review']))
