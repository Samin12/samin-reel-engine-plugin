"""Music validation and native render checks.

Run unit-only validation with:
    python3 production/editor/test_music.py -v

Run the one-second HyperFrames integration render with:
    RUN_HYPERFRAMES_INTEGRATION=1 python3 production/editor/test_music.py -v
"""
import json
import math
import os
import re
import struct
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent


def command(args, cwd=None):
    result = subprocess.run(args, cwd=cwd, capture_output=True, text=True)
    if result.returncode:
        raise AssertionError(f"command failed: {args}\n{result.stderr[-3000:]}")
    return result.stdout


def decoded_rms(video, start, duration):
    result = subprocess.run(
        ["ffmpeg", "-hide_banner", "-loglevel", "error", "-ss", str(start),
         "-t", str(duration), "-i", str(video), "-vn", "-ac", "1",
         "-ar", "48000", "-f", "f32le", "pipe:1"],
        capture_output=True)
    if result.returncode:
        raise AssertionError(result.stderr.decode(errors="replace")[-3000:])
    samples = struct.unpack("<" + "f" * (len(result.stdout) // 4), result.stdout)
    return math.sqrt(sum(sample * sample for sample in samples) / len(samples))


class MusicValidationTests(unittest.TestCase):
    def write_fixture(self, root, music=None, policy=None):
        source = root / "source.mp4"
        command(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y",
                 "-f", "lavfi", "-i", "color=c=black:size=160x280:rate=10",
                 "-t", "1", "-an", "-c:v", "libx264", "-pix_fmt", "yuv420p", str(source)])
        spec = {
            "title": "music fixture",
            "source": {"path": str(source), "segments": [{"start": 0, "end": 1}]},
            "output": {"width": 160, "height": 280, "fps": 10},
            "shots": [{"start": 0, "end": 1, "layout": "presenter"}],
        }
        if music is not None:
            spec["music"] = music
        if policy is not None:
            spec["audio_policy"] = policy
        path = root / "timeline.json"
        path.write_text(json.dumps(spec))
        return path

    def tone(self, root):
        path = root / "tone.wav"
        command(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y",
                 "-f", "lavfi", "-i", "sine=frequency=440:sample_rate=48000",
                 "-t", "1", str(path)])
        return path

    def test_required_music_gate_and_invalid_envelope(self):
        from edit import build
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            missing = self.write_fixture(root, policy={"music_required": True})
            with self.assertRaisesRegex(ValueError, "music is missing"):
                build(str(missing), str(root / "missing-composition"))
            tone = self.tone(root)
            invalid = self.write_fixture(root, music=[{
                "path": str(tone), "start": 0, "end": 1,
                "envelope": [{"t": 0.5, "v": 0.2}, {"t": 0.4, "v": 0.3}]
            }])
            with self.assertRaisesRegex(ValueError, "envelope times must increase"):
                build(str(invalid), str(root / "invalid-composition"))

    @unittest.skipUnless(os.environ.get("RUN_HYPERFRAMES_INTEGRATION") == "1",
                         "Set RUN_HYPERFRAMES_INTEGRATION=1 for the native music render")
    def test_one_second_render_contains_audible_automated_music(self):
        from edit import build
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            tone = self.tone(root)
            spec = self.write_fixture(root, music=[{
                "path": str(tone), "start": 0, "end": 1, "gain": 0.35,
                "envelope": [{"t": 0, "v": 0.2}, {"t": 0.4, "v": 0.2},
                             {"t": 0.6, "v": 0.8}, {"t": 1, "v": 0.8}]
            }], policy={"music_required": True})
            composition = root / "composition"
            receipt = build(str(spec), str(composition))
            self.assertEqual(receipt["music_count"], 1)
            self.assertTrue(receipt["music_required"])
            html = (composition / "index.html").read_text()
            self.assertIn('data-track-index="11"', html)
            self.assertIn('data-automation=', html)
            self.assertIn('&quot;target&quot;:&quot;volume&quot;', html)
            output = root / "render.mp4"
            command([sys.executable, str(HERE / "edit.py"), "render",
                     "--project", str(composition), "--output", str(output),
                     "--quality", "standard", "--workers", "1"])
            probe = json.loads(command(["ffprobe", "-v", "error", "-show_streams",
                                        "-show_format", "-of", "json", str(output)]))
            self.assertAlmostEqual(float(probe["format"]["duration"]), 1, delta=.12)
            self.assertTrue(any(s["codec_type"] == "audio" for s in probe["streams"]))
            measured = subprocess.run(
                ["ffmpeg", "-hide_banner", "-i", str(output),
                 "-af", "volumedetect", "-f", "null", "-"],
                cwd=root, capture_output=True, text=True)
            self.assertEqual(measured.returncode, 0, measured.stderr[-3000:])
            analysis = measured.stderr
            self.assertNotIn("max_volume: -inf", analysis)
            self.assertRegex(analysis, r"mean_volume: -[0-9.]+ dB")
            quiet_rms = decoded_rms(output, 0.2, 0.15)
            loud_rms = decoded_rms(output, 0.7, 0.15)
            source_quiet_rms = decoded_rms(tone, 0.2, 0.15)
            source_loud_rms = decoded_rms(tone, 0.7, 0.15)
            quiet_ratio = quiet_rms / source_quiet_rms
            loud_ratio = loud_rms / source_loud_rms
            print(f"music envelope ratios quiet={quiet_ratio:.3f} loud={loud_ratio:.3f}")
            # Browser/FFmpeg resampling and AAC add a stable level offset; the
            # broad bands retain the absolute-gain check while rejecting the
            # .35 fallback multiplied by .2/.8 envelope values.
            self.assertGreater(quiet_ratio, 0.12)
            self.assertLess(quiet_ratio, 0.4)
            self.assertGreater(loud_ratio, 0.5)
            self.assertLess(loud_ratio, 1.35)
            self.assertGreater(loud_ratio, quiet_ratio * 2.5,
                               f"absolute envelope did not raise the later window: quiet={quiet_ratio} loud={loud_ratio}")


if __name__ == "__main__":
    unittest.main()
