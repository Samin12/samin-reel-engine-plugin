"""Opt-in regression for the actual native HyperFrames video compositor.

Run from the repository root:
    RUN_HYPERFRAMES_INTEGRATION=1 python3 production/editor/test_media_background.py -v

Requires the pinned local Node dependencies, working HyperFrames render runtime,
and FFmpeg/FFprobe. Uses only synthetic video in a temporary directory. This
checks decoded pixels, not HTML/CSS or browser snapshots.
"""
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


HERE = Path(__file__).resolve().parent
WIDTH, HEIGHT = 320, 568


@unittest.skipUnless(os.environ.get('RUN_HYPERFRAMES_INTEGRATION') == '1',
                     'Set RUN_HYPERFRAMES_INTEGRATION=1 to render the integration fixture')
class NativeMediaBackgroundTests(unittest.TestCase):
    def command(self, args, timeout=180):
        try:
            result = subprocess.run(args, capture_output=True, timeout=timeout)
        except subprocess.TimeoutExpired as exc:
            self.fail(f'Runtime timeout after {timeout}s: {args[0]} {args[1:3]}: {exc}')
        self.assertEqual(result.returncode, 0,
                         f'Command failed: {args}\n{result.stderr.decode(errors="replace")[-4000:]}\n'
                         f'{result.stdout.decode(errors="replace")[-2000:]}')
        return result.stdout

    def frame_rgb(self, video, seconds):
        data = self.command([
            'ffmpeg', '-hide_banner', '-loglevel', 'error', '-ss', str(seconds),
            '-i', str(video), '-frames:v', '1', '-an', '-f', 'rawvideo',
            '-pix_fmt', 'rgb24', 'pipe:1'])
        self.assertEqual(len(data), WIDTH * HEIGHT * 3)
        return data

    @staticmethod
    def patch_mean(frame, x, y):
        # Several interior pixels avoid codec/block-edge noise without hiding an
        # entire colored presenter strip or an incorrectly persistent layer.
        values = [frame[((py * WIDTH + px) * 3):((py * WIDTH + px) * 3 + 3)]
                  for py in range(y - 2, y + 3) for px in range(x - 2, x + 3)]
        return tuple(round(sum(pixel[channel] for pixel in values) / len(values), 2)
                     for channel in range(3))

    def test_contain_background_hides_presenter_and_expires_with_broll(self):
        for executable in ('ffmpeg', 'ffprobe'):
            self.assertIsNotNone(shutil.which(executable), f'Required dependency missing: {executable}')
        cli = HERE / 'node_modules/.bin/hyperframes'
        self.assertTrue(cli.is_file(), 'Pinned HyperFrames CLI missing; run npm ci in production/editor')
        declared = json.loads((HERE / 'package.json').read_text())['dependencies']['hyperframes']
        installed = json.loads((HERE / 'node_modules/hyperframes/package.json').read_text())['version']
        self.assertEqual(installed, declared, 'Installed HyperFrames differs from the pinned project version')
        with tempfile.TemporaryDirectory(prefix='reel-native-background-') as folder:
            root = Path(folder)
            red, blue = root / 'red-aroll.mp4', root / 'blue-broll.mp4'
            for path, color, width, duration in ((red, 'red', WIDTH, 1), (blue, 'blue', 160, .5)):
                self.command([
                    'ffmpeg', '-hide_banner', '-loglevel', 'error', '-y',
                    '-f', 'lavfi', '-i', f'color=c={color}:size={width}x{HEIGHT}:rate=10',
                    '-t', str(duration), '-an', '-c:v', 'libx264', '-preset', 'ultrafast',
                    '-pix_fmt', 'yuv420p', str(path)])
            spec = {
                'title': 'Native contain background regression',
                'source': {'path': str(red), 'segments': [{'start': 0, 'end': 1}]},
                'output': {'width': WIDTH, 'height': HEIGHT, 'fps': 10},
                'shots': [
                    {'id': 'blue-contained', 'start': 0, 'end': .5, 'layout': 'full_broll',
                     'media': str(blue), 'fit': 'contain', 'background': '#ffffff'},
                    {'id': 'red-presenter', 'start': .5, 'end': 1, 'layout': 'presenter'}
                ]
            }
            spec_path = root / 'timeline.json'
            spec_path.write_text(json.dumps(spec))
            project, output = root / 'composition', root / 'render.mp4'
            self.command([sys.executable, str(HERE / 'edit.py'), 'build',
                          '--spec', str(spec_path), '--project', str(project)])
            self.command([sys.executable, str(HERE / 'edit.py'), 'render',
                          '--project', str(project), '--output', str(output),
                          '--quality', 'standard', '--workers', '1'])
            probe = json.loads(self.command(['ffprobe', '-v', 'error', '-show_streams',
                                             '-show_format', '-of', 'json', str(output)]))
            self.assertFalse(any(s['codec_type'] == 'audio' for s in probe['streams']))
            self.assertAlmostEqual(float(probe['format']['duration']), 1, delta=.11)
            before, after = self.frame_rgb(output, .25), self.frame_rgb(output, .75)
            points = {'left': (20, HEIGHT // 2), 'center': (WIDTH // 2, HEIGHT // 2),
                      'right': (WIDTH - 20, HEIGHT // 2)}
            observed = {
                'at_0.25s': {name: self.patch_mean(before, *xy) for name, xy in points.items()},
                'at_0.75s': {name: self.patch_mean(after, *xy) for name, xy in points.items()}
            }
            for side in ('left', 'right'):
                self.assertTrue(all(c >= 235 for c in observed['at_0.25s'][side]),
                                f'Contain-fit side must be white, not leaked red presenter: {observed}')
            r, g, b = observed['at_0.25s']['center']
            self.assertTrue(b >= 200 and r <= 45 and g <= 45,
                            f'B-roll center must be blue: {observed}')
            for name, (r, g, b) in observed['at_0.75s'].items():
                self.assertTrue(r >= 200 and g <= 45 and b <= 45,
                                f'Presenter must return at {name}; B-roll/fill must both expire: {observed}')
            print(json.dumps({'hyperframes': installed, 'decoded_pixels': observed,
                              'duration': probe['format']['duration'],
                              'scope': 'Actual native compositor render and decoded pixels; no markup assertions'}))


if __name__ == '__main__':
    unittest.main()
