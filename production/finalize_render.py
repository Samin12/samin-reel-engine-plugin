#!/usr/bin/env python3
"""Normalize a rendered reel's audio and verify the final MP4 without re-encoding video.

python3 finalize_render.py --input raw.mp4 --output final.mp4 --receipt verification.json
"""
import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess
from datetime import datetime, timezone


def run(args):
    result = subprocess.run(args, text=True, capture_output=True)
    if result.returncode:
        raise RuntimeError(result.stderr[-6000:])
    return result


def measure(path, target, peak):
    result = run(["ffmpeg", "-hide_banner", "-nostats", "-i", str(path), "-vn", "-af",
                  f"loudnorm=I={target}:TP={peak}:LRA=7:print_format=json", "-f", "null", "-"])
    blocks = re.findall(r'\{\s*"input_i".*?\}', result.stderr, re.S)
    if not blocks:
        raise RuntimeError("FFmpeg returned no loudness measurement")
    return json.loads(blocks[-1])


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--receipt", required=True)
    parser.add_argument("--target-lufs", type=float, default=-14.2)
    parser.add_argument("--true-peak", type=float, default=-1.0)
    parser.add_argument("--codec-headroom-db", type=float, default=0.8,
                        help="Extra limiter headroom before AAC encoding; verify the decoded final peak")
    args = parser.parse_args()
    if not 0 <= args.codec_headroom_db <= 3:
        raise ValueError("codec-headroom-db must be between 0 and 3")
    limiter_ceiling = args.true_peak - args.codec_headroom_db
    source, output = Path(args.input).resolve(), Path(args.output).resolve()
    if source == output or output.exists():
        raise ValueError("Use a new final output path; input and existing renders are preserved")
    output.parent.mkdir(parents=True, exist_ok=True)
    source_probe = json.loads(run(["ffprobe", "-v", "error", "-show_streams", "-of", "json", str(source)]).stdout)
    video_duration = next(float(s['duration']) for s in source_probe['streams'] if s.get('codec_type') == 'video')
    measured = measure(source, args.target_lufs, limiter_ceiling)
    # Second pass uses the actual mixed render, including sound accents.
    effect = (f"loudnorm=I={args.target_lufs}:TP={limiter_ceiling}:LRA=7:"
              f"measured_I={measured['input_i']}:measured_TP={measured['input_tp']}:"
              f"measured_LRA={measured['input_lra']}:measured_thresh={measured['input_thresh']}:"
              f"offset={measured['target_offset']}:linear=true,"
              # A rendered mix is continuous. Rebuild its timestamps from samples
              # after resampling so an AAC timestamp gap cannot truncate the tail.
              f"aresample=48000,asetpts=N/SR/TB,atrim=duration={video_duration}")
    run(["ffmpeg", "-hide_banner", "-v", "error", "-i", str(source), "-map", "0:v:0", "-map", "0:a:0",
         "-c:v", "copy", "-af", effect, "-c:a", "aac", "-b:a", "192k", "-ar", "48000",
         "-t", str(video_duration), "-movflags", "+faststart", str(output)])
    decoded = run(["ffmpeg", "-hide_banner", "-v", "error", "-i", str(output), "-f", "null", "-"])
    if decoded.stderr.strip():
        raise RuntimeError("Final decode reported errors: " + decoded.stderr[-3000:])
    probe = json.loads(run(["ffprobe", "-v", "error", "-show_streams", "-show_format", "-of", "json", str(output)]).stdout)
    audio = measure(output, args.target_lufs, args.true_peak)
    digest = hashlib.sha256()
    with output.open('rb') as media:
        for chunk in iter(lambda: media.read(8 * 1024 * 1024), b''):
            digest.update(chunk)
    receipt = {"verified_at": datetime.now(timezone.utc).isoformat(), "output_filename": output.name,
               "bytes": output.stat().st_size, "sha256": digest.hexdigest(), "complete_decode": "passed",
               "video_reencoded_during_finalization": False, "target_lufs": args.target_lufs,
               "target_true_peak_dbtp": args.true_peak, "raw_audio_measurement": measured,
               "pre_aac_limiter_ceiling_dbtp": limiter_ceiling,
               "codec_headroom_db": args.codec_headroom_db,
               "final_integrated_lufs": float(audio['input_i']), "final_true_peak_dbtp": float(audio['input_tp']),
               "final_loudness_range_lu": float(audio['input_lra']), "duration_seconds": float(probe['format']['duration']),
               "streams": [{k: stream.get(k) for k in ('codec_type','codec_name','width','height','r_frame_rate','sample_rate','channels','duration','nb_frames')} for stream in probe['streams']],
               "visual_review": "pending", "subjective_sound_match": "not claimed"}
    if abs(receipt['final_integrated_lufs'] - args.target_lufs) > 1:
        raise RuntimeError("Final loudness is more than 1 LU from target")
    # AAC may introduce small intersample changes; measure and report, never silently call it exact.
    receipt['true_peak_review_needed'] = receipt['final_true_peak_dbtp'] > args.true_peak + 0.3
    target = Path(args.receipt)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(receipt, indent=2) + "\n")
    print(json.dumps(receipt, indent=2))


if __name__ == "__main__":
    main()
