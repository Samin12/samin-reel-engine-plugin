#!/usr/bin/env python3
"""Apply a source-relative edit decision list and retime actual word captions."""
import argparse
import json
import math
import subprocess
from fractions import Fraction
from pathlib import Path


def frame_rate_for_edit(spec, source):
    """Opt in only for an explicitly identified constant-frame-rate source.

    Legacy EDLs retain timestamp trims. A declared frame_rate is a contract:
    callers must use a CFR source/proxy and cuts on its frame grid. Metadata
    checks catch common wrong-rate inputs; they cannot prove every frame is CFR.
    """
    if 'frame_rate' not in spec:
        return None
    try:
        rate = Fraction(str(spec['frame_rate']))
    except (ValueError, ZeroDivisionError):
        raise ValueError('frame_rate must be a positive number or ratio') from None
    if rate <= 0 or rate > 240:
        raise ValueError('frame_rate must be greater than zero and at most 240')
    probe = json.loads(subprocess.run(
        ['ffprobe', '-v', 'error', '-select_streams', 'v:0',
         '-show_entries', 'stream=r_frame_rate,avg_frame_rate,start_time',
         '-of', 'json', source], capture_output=True, text=True, check=True).stdout)
    streams = probe.get('streams', [])
    if not streams:
        raise ValueError('Source has no video stream')
    stream = streams[0]
    for key in ('r_frame_rate', 'avg_frame_rate'):
        try:
            observed = Fraction(stream.get(key, '0/1'))
        except (ValueError, ZeroDivisionError):
            observed = Fraction(0)
        if observed != rate:
            raise ValueError(f'Source {key} does not match declared frame_rate; use a verified CFR proxy')
    if abs(float(stream.get('start_time', 0))) > 1e-6:
        raise ValueError('Frame-index editing requires a zero-origin video stream; use a CFR proxy')
    for i, segment in enumerate(spec['segments']):
        for edge in ('start', 'end'):
            frame = float(segment[edge]) * float(rate)
            if not math.isfinite(frame) or abs(frame - round(frame)) > 1e-6:
                raise ValueError(f'Segment {i} {edge} is not on the declared frame grid; inspect and align the cut first')
    return rate


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--source',required=True)
    ap.add_argument('--transcript',required=True)
    ap.add_argument('--edit',required=True)
    ap.add_argument('--output',required=True)
    ap.add_argument('--words-output',required=True)
    a=ap.parse_args()
    spec=json.loads(Path(a.edit).read_text()); segments=spec['segments']; speed=float(spec.get('speed',1))
    if not .8 <= speed <= 1.25: raise ValueError('Review larger delivery-speed changes manually')
    frame_rate=frame_rate_for_edit(spec,a.source)
    data=json.loads(Path(a.transcript).read_text())
    words=data if isinstance(data,list) else data.get('words', [w for s in data.get('segments',[]) for w in s['words']])
    if not words: raise ValueError('Transcript contains no word timestamps')
    for correction in spec.get('word_timing_overrides', []):
        word=words[correction['index']]
        if word['word'].strip() != correction['word']: raise ValueError('Timing correction targets a different word')
        word.update({key:correction[key] for key in ('start','end')})
    duration=float(subprocess.run(['ffprobe','-v','error','-show_entries','format=duration','-of','csv=p=0',a.source],capture_output=True,text=True,check=True).stdout)
    filters=[]; mapped=[]; cursor=0
    for i,seg in enumerate(segments):
        start,end=seg['start'],seg['end'];length=end-start
        if not 0 <= start < end <= duration: raise ValueError(f'Segment {i} outside source duration')
        if frame_rate is not None:
            first,last=round(start*float(frame_rate)),round(end*float(frame_rate))
            # Exact indices avoid decimal timestamps selecting one extra frame,
            # which makes concat pad audio and shifts all later word mappings.
            filters.append(f'[0:v]trim=start_frame={first}:end_frame={last},setpts=PTS-STARTPTS[v{i}]')
        else:
            filters.append(f'[0:v]trim=start={start}:end={end},setpts=PTS-STARTPTS[v{i}]')
        filters.append(f'[0:a]atrim=start={start}:end={end},asetpts=PTS-STARTPTS,afade=t=in:d=0.005,afade=t=out:st={max(0,length-.005)}:d=0.005[a{i}]')
        for w in words:
            if start <= (w['start']+w['end'])/2 < end:
                mapped.append({'word':w['word'].strip(),'start':round((cursor+max(w['start'],start)-start)/speed,4),'end':round((cursor+min(w['end'],end)-start)/speed,4),'source_start':w['start'],'source_end':w['end']})
        cursor+=length
    labels=''.join(f'[v{i}][a{i}]' for i in range(len(segments)))
    filters.append(f'{labels}concat=n={len(segments)}:v=1:a=1[vc][ac]')
    filters.append(f'[vc]setpts=PTS/{speed},fps=30[vout]')
    # Even at 1.0 atempo processes the samples; leave identity-speed speech alone.
    filters.append('[ac]anull[aout]' if speed==1 else f'[ac]atempo={speed}[aout]')
    output=Path(a.output).resolve();output.parent.mkdir(parents=True,exist_ok=True)
    graph=output.with_suffix('.ffmpeg.txt');graph.write_text(';\n'.join(filters))
    subprocess.run(['ffmpeg','-hide_banner','-loglevel','error','-y','-i',a.source,'-filter_complex_script',str(graph),'-map','[vout]','-map','[aout]','-c:v','h264_videotoolbox','-b:v','10M','-pix_fmt','yuv420p','-c:a','aac','-b:a','192k','-movflags','+faststart',str(output)],check=True)
    result={'words':mapped,'duration':cursor/speed,'source_video_offset':spec.get('source_video_offset',0),'speed':speed}
    if frame_rate is not None: result['frame_rate']=str(frame_rate)
    Path(a.words_output).write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({'output':str(output),'duration':cursor/speed,'words':len(mapped),'wpm':len(mapped)*60/(cursor/speed),'segments':len(segments)}))


if __name__=='__main__': main()
