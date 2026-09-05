"""Regression checks for real frame joins and identity-speed audio preservation."""
import array
import json
import math
import shutil
import subprocess
import sys
import tempfile
import unittest
import wave
from pathlib import Path


HELPER = Path(__file__).with_name('prepare_take.py')


def pcm(path):
    with wave.open(str(path), 'rb') as reader:
        assert reader.getnchannels() == 1 and reader.getsampwidth() == 2
        return array.array('h', reader.readframes(reader.getnframes()))


def correlation(a, b):
    ma, mb = math.fsum(a) / len(a), math.fsum(b) / len(b)
    numerator = math.fsum((x - ma) * (y - mb) for x, y in zip(a, b))
    denominator = math.sqrt(math.fsum((x - ma) ** 2 for x in a) *
                            math.fsum((y - mb) ** 2 for y in b))
    return numerator / denominator


class PrepareTakeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if not shutil.which('ffmpeg') or not shutil.which('ffprobe'):
            raise unittest.SkipTest('FFmpeg and FFprobe are required')
        encoders = subprocess.check_output(['ffmpeg', '-hide_banner', '-encoders'], text=True)
        if 'h264_videotoolbox' not in encoders:
            raise unittest.SkipTest('Current production helper requires macOS h264_videotoolbox')
        cls.temp = tempfile.TemporaryDirectory()
        cls.root = Path(cls.temp.name)
        cls.source = cls.root / 'source.mov'
        # A changing waveform exposes tiny atempo=1 phase/timing changes that a
        # duration-only check misses. This is synthetic test audio, not a voice.
        subprocess.run([
            'ffmpeg', '-hide_banner', '-loglevel', 'error', '-y',
            '-f', 'lavfi', '-i', 'testsrc2=size=160x288:rate=30',
            '-f', 'lavfi', '-i', 'aevalsrc=0.3*sin(2*PI*(200*t+80*t*t)):s=48000',
            '-t', '4.5', '-c:v', 'libx264', '-preset', 'ultrafast',
            '-pix_fmt', 'yuv420p', '-c:a', 'pcm_s16le', str(cls.source)
        ], check=True)
        cls.transcript = cls.root / 'transcript.json'
        cls.transcript.write_text(json.dumps({'words': [
            {'word': 'alpha', 'start': .62, 'end': .8},
            {'word': 'beta', 'start': 1.72, 'end': 1.9},
            {'word': 'gamma', 'start': 3.35, 'end': 3.6}
        ]}))

    @classmethod
    def tearDownClass(cls):
        if hasattr(cls, 'temp'):
            cls.temp.cleanup()

    def run_edit(self, name, spec):
        edl = self.root / f'{name}.json'
        edl.write_text(json.dumps(spec))
        output = self.root / f'{name}.mp4'
        words = self.root / f'{name}-words.json'
        result = subprocess.run([
            sys.executable, str(HELPER), '--source', str(self.source),
            '--transcript', str(self.transcript), '--edit', str(edl),
            '--output', str(output), '--words-output', str(words)
        ], capture_output=True, text=True)
        return result, output, words

    def test_frame_aligned_joins_preserve_audio_and_word_timebase(self):
        frame_ranges = [(17, 39), (50, 77), (99, 123)]
        spec = {'frame_rate': 30, 'speed': 1, 'segments': [
            {'start': a / 30, 'end': b / 30} for a, b in frame_ranges]}
        result, output, word_file = self.run_edit('aligned', spec)
        self.assertEqual(result.returncode, 0, result.stderr)
        data = json.loads(word_file.read_text())
        probe = json.loads(subprocess.check_output([
            'ffprobe', '-v', 'error', '-show_entries', 'format=duration:stream=nb_frames',
            '-of', 'json', str(output)]))
        self.assertAlmostEqual(float(probe['format']['duration']), 73 / 30, places=5)
        self.assertAlmostEqual(data['duration'], 73 / 30, places=9)
        self.assertEqual(probe['streams'][0]['nb_frames'], '73')
        self.assertEqual([w['word'] for w in data['words']], ['alpha', 'beta', 'gamma'])
        cursor = 0
        for index, (first, last) in enumerate(frame_ranges):
            expected = cursor + [.62, 1.72, 3.35][index] - first / 30
            self.assertAlmostEqual(data['words'][index]['start'], expected, places=4)
            cursor += (last - first) / 30
        decoded = {}
        for name, path in [('source', self.source), ('edited', output)]:
            target = self.root / f'{name}-decoded.wav'
            subprocess.run(['ffmpeg', '-hide_banner', '-loglevel', 'error', '-y',
                            '-xerror', '-i', str(path), '-vn', '-ac', '1',
                            '-ar', '48000', '-c:a', 'pcm_s16le', str(target)], check=True)
            decoded[name] = pcm(target)
        # Independent oracle: concatenate the original PCM frame ranges in Python.
        # Compare each join at its exact expected sample offset, without lag search.
        cursor = 0
        for first, last in frame_ranges:
            count = (last - first) * 1600
            margin = 1920  # Excludes only the deliberate cut fades and AAC edges.
            original = decoded['source'][first * 1600 + margin:last * 1600 - margin]
            actual = decoded['edited'][cursor + margin:cursor + count - margin]
            self.assertEqual(len(original), len(actual))
            self.assertGreater(correlation(original, actual), .98)
            cursor += count

    def test_declared_grid_rejects_off_frame_cuts_without_silently_moving_them(self):
        result, output, _ = self.run_edit('off-grid', {
            'frame_rate': 30, 'segments': [{'start': .56, 'end': 1.3}]})
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('not on the declared frame grid', result.stderr)
        self.assertFalse(output.exists())

    def test_declared_rate_rejects_wrong_source_rate(self):
        result, output, _ = self.run_edit('wrong-rate', {
            'frame_rate': 25, 'segments': [{'start': .4, 'end': 1.2}]})
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('does not match declared frame_rate', result.stderr)
        self.assertFalse(output.exists())

    def test_legacy_edl_and_nonidentity_speed_keep_existing_contract(self):
        result, output, word_file = self.run_edit('legacy-speed', {
            'speed': 1.1, 'segments': [{'start': .56, 'end': 1.3}],
            'source_video_offset': 1208.9})
        self.assertEqual(result.returncode, 0, result.stderr)
        data = json.loads(word_file.read_text())
        self.assertNotIn('frame_rate', data)
        self.assertEqual(data['source_video_offset'], 1208.9)
        self.assertEqual(data['speed'], 1.1)
        self.assertAlmostEqual(data['duration'], (.74 / 1.1), places=9)
        self.assertAlmostEqual(data['words'][0]['start'], (.62 - .56) / 1.1, places=4)
        self.assertTrue(output.is_file())


if __name__ == '__main__':
    unittest.main()
