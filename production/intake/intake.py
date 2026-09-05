#!/usr/bin/env python3
"""Transcribe a completed local filming batch and index likely script take ranges."""
import argparse
import hashlib
import json
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path


def now():
    return datetime.now(timezone.utc).isoformat()


def save(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + '.tmp')
    temporary.write_text(json.dumps(value, indent=2, ensure_ascii=False) + '\n')
    temporary.replace(path)


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def normalize(text):
    text = text.lower().replace('’', "'")
    tokens = re.findall(r"[a-z0-9]+(?:'[a-z]+)?", text)
    numbers = {'one': '1', 'two': '2', 'three': '3', 'four': '4', 'five': '5',
               'six': '6', 'seven': '7', 'eight': '8', 'nine': '9', 'ten': '10'}
    return [numbers.get(token, token) for token in tokens]


def read_words(data):
    words = data if isinstance(data, list) else data.get('words')
    if words is None:
        words = [w for segment in data.get('segments', []) for w in segment.get('words', [])]
    result = []
    for w in words:
        start, end = float(w['start']), float(w['end'])
        if not 0 <= start <= end or not end < float('inf'):
            raise ValueError('Invalid ASR word timing')
        if result and start < result[-1]['start']:
            raise ValueError('ASR words must be in timestamp order')
        text = w.get('word', w.get('text', '')).strip()
        if text:
            result.append({'word': text, 'start': start, 'end': end,
                           'probability': w.get('probability')})
    if not result:
        raise ValueError('No word timestamps found; segment-only timing is insufficient')
    return result


def tokenize_words(words):
    tokens, indices = [], []
    for i, word in enumerate(words):
        for token in normalize(word['word']):
            tokens.append(token)
            indices.append(i)
    return tokens, indices


def align(reference, spoken, max_takes=4):
    """Smith-Waterman local alignment; score exact normalized words, not semantic guesses."""
    m, n = len(reference), len(spoken)
    if not m or not n:
        return []
    # Store only directions plus two score rows; memory stays O(m*n) bytes.
    trace = [bytearray(n + 1) for _ in range(m + 1)]
    previous = [0] * (n + 1)
    endpoints = [(0, 0)] * (n + 1)
    for i, token in enumerate(reference, 1):
        row = [0] * (n + 1)
        directions = trace[i]
        for j, observed in enumerate(spoken, 1):
            diagonal = previous[j - 1] + (3 if token == observed else -2)
            up, left = previous[j] - 2, row[j - 1] - 2
            score = max(0, diagonal, up, left)
            row[j] = score
            directions[j] = 0 if score == 0 else 1 if score == diagonal else 2 if score == up else 3
            if score > endpoints[j][0]:
                endpoints[j] = (score, i)
        previous = row
    candidates = []
    for last_j in sorted(range(1, n + 1), key=lambda j: endpoints[j][0], reverse=True):
        score, i = endpoints[last_j]
        if score < max(24, m * .45):
            break
        if any(c['spoken_start'] <= last_j - 1 <= c['spoken_end'] for c in candidates):
            continue
        j, matches, path_steps, gaps, max_gap = last_j, [], 0, 0, 0
        while i and j and trace[i][j]:
            direction = trace[i][j]
            path_steps += 1
            if direction == 1:
                if reference[i - 1] == spoken[j - 1]:
                    matches.append((i - 1, j - 1)); max_gap = max(max_gap, gaps); gaps = 0
                else:
                    gaps += 1
                i -= 1; j -= 1
            elif direction == 2:
                i -= 1; gaps += 1
            else:
                j -= 1; gaps += 1
        if len(matches) < max(12, m * .25):
            continue
        matches.reverse()
        first, last = matches[0][1], matches[-1][1]
        if any(max(0, min(last, c['spoken_end']) - max(first, c['spoken_start']) + 1) /
               min(last - first + 1, c['spoken_end'] - c['spoken_start'] + 1) > .35 for c in candidates):
            continue
        coverage, precision = len(matches) / m, len(matches) / max(1, path_steps)
        edge = min(12, m)
        opening = sum(a < edge for a, _ in matches) / edge
        ending = sum(a >= m - edge for a, _ in matches) / edge
        strong = coverage >= .85 and precision >= .70 and opening >= .60 and ending >= .60 and max_gap <= 18
        confidence = 'high' if strong else 'medium' if coverage >= .60 and precision >= .55 else 'low'
        candidates.append({'spoken_start': first, 'spoken_end': last, 'alignment_score': score,
                           'matched_tokens': len(matches), 'reference_tokens': m,
                           'reference_coverage': round(coverage, 4), 'alignment_precision': round(precision, 4),
                           'opening_coverage': round(opening, 4), 'ending_coverage': round(ending, 4),
                           'longest_unmatched_run': max(max_gap, gaps), 'confidence': confidence,
                           'classification': 'strong_script_overlap' if strong else 'partial_script_overlap',
                           'full_match_verified': False, 'requires_review': True})
        if len(candidates) >= max_takes:
            break
    return sorted(candidates, key=lambda c: c['spoken_start'])


def script_index(samples, words, max_takes):
    spoken, indices = tokenize_words(words)
    scripts = []
    paths = sorted(samples.glob('*.md'), key=lambda p: [int(t) if t.isdigit() else t for t in re.split(r'(\d+)', p.name)])
    if not paths:
        raise ValueError(f'No Markdown scripts in {samples}')
    for path in paths:
        content = path.read_text()
        candidates = align(normalize(content), spoken, max_takes)
        for candidate in candidates:
            first, last = indices[candidate.pop('spoken_start')], indices[candidate.pop('spoken_end')]
            candidate.update({'start': words[first]['start'], 'end': words[last]['end'],
                              'word_start_index': first, 'word_end_index': last,
                              'observed_text': ' '.join(w['word'] for w in words[first:last + 1]),
                              'timing_basis': 'first_and_last_exactly_aligned_ASR_words'})
        scripts.append({'script_id': path.stem, 'script_path': str(path.resolve()),
                        'script_sha256': digest(path), 'script_word_count': len(normalize(content)),
                        'status': 'candidates_need_review' if candidates else 'no_sufficient_overlap_found',
                        'candidates': candidates})
        print(f'Indexed {path.name}: {len(candidates)} candidate(s)', flush=True)
    return scripts


def safe_drive(path):
    if not path:
        return None
    data = json.loads(Path(path).read_text())
    data = data.get('selected', data)
    allowed = ('id', 'name', 'size', 'modifiedTime', 'webViewLink', 'mimeType', 'duration_seconds')
    return {key: data[key] for key in allowed if key in data}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', required=True, type=Path)
    parser.add_argument('--out', required=True, type=Path)
    parser.add_argument('--samples', type=Path, default=Path(__file__).resolve().parents[2] / 'voice/samples')
    parser.add_argument('--work-dir', type=Path, default=Path('work/intake/batch'))
    parser.add_argument('--drive-metadata', type=Path)
    parser.add_argument('--transcript', type=Path, help='Reuse a word-timestamp JSON; never transcribes when supplied')
    parser.add_argument('--model-path', type=Path, default=Path.home() / '.cache/whisper/base.en.pt')
    parser.add_argument('--threads', type=int, default=4, choices=range(1, 9))
    parser.add_argument('--max-takes', type=int, default=4, choices=range(1, 11))
    args = parser.parse_args()
    out = args.out.resolve(); out.mkdir(parents=True, exist_ok=True)
    manifest = {'schema_version': 1, 'status': 'running', 'started_at': now(), 'errors': [],
                'source_path': str(args.source.resolve()), 'transcription_executed': False}
    receipt = out / 'intake-manifest.json'; save(receipt, manifest)
    try:
        source = args.source.resolve()
        if not source.is_file() or source.name.endswith(('.incomplete', '.part', '.tmp')):
            raise ValueError('Source must be a completed local file, not a partial download')
        metadata = safe_drive(args.drive_metadata)
        if metadata and metadata.get('size') and source.stat().st_size != int(metadata['size']):
            raise ValueError('Local source byte size does not match selected Drive file metadata')
        probe = subprocess.run(['ffprobe', '-v', 'error', '-show_format', '-show_streams', '-of', 'json', str(source)],
                               capture_output=True, text=True, check=True)
        probe_data = json.loads(probe.stdout); save(out / 'source-probe.json', probe_data)
        duration = float(probe_data['format']['duration'])
        if metadata and metadata.get('duration_seconds') and abs(float(metadata['duration_seconds']) - duration) > 2:
            raise ValueError('Local source duration differs from selected Drive metadata')
        stat = source.stat()
        manifest.update({'drive': metadata, 'source_bytes': stat.st_size, 'source_mtime_ns': stat.st_mtime_ns,
                         'source_duration': duration, 'samples_path': str(args.samples.resolve())})
        if args.transcript:
            data = json.loads(args.transcript.read_text())
            manifest['reused_transcript'] = {'path': str(args.transcript.resolve()), 'sha256': digest(args.transcript)}
        else:
            if not args.model_path.is_file():
                raise ValueError(f'Cached model missing: {args.model_path}; no automatic model download is permitted')
            import torch
            import whisper
            torch.set_num_threads(args.threads)
            args.work_dir.mkdir(parents=True, exist_ok=True)
            wav = args.work_dir.resolve() / 'batch-16khz.wav'
            print(f'Extracting complete audio ({duration / 60:.1f} minutes)', flush=True)
            subprocess.run(['ffmpeg', '-hide_banner', '-loglevel', 'error', '-xerror', '-y', '-i', str(source),
                            '-vn', '-ac', '1', '-ar', '16000', '-c:a', 'pcm_s16le', str(wav)], check=True)
            if source.stat().st_size != stat.st_size or source.stat().st_mtime_ns != stat.st_mtime_ns:
                raise ValueError('Source changed during extraction; wait for a completed download')
            manifest.update({'model': {'name': args.model_path.name, 'sha256': digest(args.model_path),
                                      'device': 'cpu', 'threads': args.threads, 'fp16': False},
                             'transcription_started_at': now(), 'transcription_executed': True})
            save(receipt, manifest)
            print('Transcribing locally; full batch may take several minutes. Progress follows.', flush=True)
            model = whisper.load_model(str(args.model_path.resolve()), device='cpu')
            data = model.transcribe(str(wav), language='en', word_timestamps=True, fp16=False, verbose=False)
            manifest['transcription_finished_at'] = now()
        words = read_words(data)
        if words[-1]['end'] > duration + 1:
            raise ValueError('Transcript extends beyond this source; verify the transcript/source pairing')
        save(out / 'transcript.json', data)
        save(out / 'word-transcript.json', {'schema_version': 1, 'words': words,
             'time_origin': 'local_source_start_seconds', 'timing_quality': 'ASR_estimate_requires_review',
             'source_duration': duration})
        scripts = script_index(args.samples.resolve(), words, args.max_takes)
        save(out / 'script-takes.json', {'schema_version': 1, 'generated_at': now(), 'source': manifest['source_path'],
             'source_duration': duration, 'method': 'normalized_exact_word_local_alignment',
             'confidence_is_calibrated_probability': False, 'full_match_verified': False,
             'review_note': 'Candidate bounds are observed aligned words, not approved cuts. Check starts, endings, retakes, omissions and ASR errors against audio.',
             'scripts': scripts})
        manifest.update({'status': 'complete', 'word_count': len(words), 'script_count': len(scripts),
                         'candidate_count': sum(len(s['candidates']) for s in scripts),
                         'scripts_without_candidates': [s['script_id'] for s in scripts if not s['candidates']]})
    except Exception as exc:
        manifest['status'] = 'failed'; manifest['errors'].append(f'{type(exc).__name__}: {exc}')
        print(manifest['errors'][-1], file=sys.stderr)
    finally:
        manifest['finished_at'] = now(); save(receipt, manifest)
    print(json.dumps({'status': manifest['status'], 'manifest': str(receipt)}))
    return 0 if manifest['status'] == 'complete' else 1


if __name__ == '__main__':
    raise SystemExit(main())
