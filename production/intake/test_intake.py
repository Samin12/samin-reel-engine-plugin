import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

spec = importlib.util.spec_from_file_location('intake', Path(__file__).with_name('intake.py'))
intake = importlib.util.module_from_spec(spec)
spec.loader.exec_module(intake)


class IntakeTests(unittest.TestCase):
    def setUp(self):
        self.reference = [f'word{i}' for i in range(40)]

    def test_repeated_takes_have_distinct_observed_ranges(self):
        spoken = self.reference + ['silence'] * 15 + self.reference
        result = intake.align(self.reference, spoken)
        self.assertEqual([(x['spoken_start'], x['spoken_end']) for x in result], [(0, 39), (55, 94)])
        self.assertTrue(all(x['confidence'] == 'high' and not x['full_match_verified'] for x in result))

    def test_partial_script_never_claims_full_take(self):
        result = intake.align(self.reference, self.reference[:27])[0]
        self.assertEqual(result['classification'], 'partial_script_overlap')
        self.assertEqual(result['ending_coverage'], 0)
        self.assertFalse(result['full_match_verified'])

    def test_unrelated_speech_has_no_candidates(self):
        self.assertEqual(intake.align(self.reference, ['irrelevant'] * 60), [])

    def test_number_normalization_preserves_word_indices(self):
        tokens, indices = intake.tokenize_words([{'word': 'Four experts'}, {'word': '4 agents'}])
        self.assertEqual(tokens, ['4', 'experts', '4', 'agents'])
        self.assertEqual(indices, [0, 0, 1, 1])

    def test_segment_words_supported_and_bad_timing_rejected(self):
        self.assertEqual(len(intake.read_words({'segments': [{'words': [{'word': 'Hello', 'start': 0, 'end': 1}]}]})), 1)
        for words in [[{'word': 'bad', 'start': 2, 'end': 1}], [{'word': 'bad', 'start': 0, 'end': float('nan')}]]:
            with self.assertRaises(ValueError): intake.read_words(words)
        with self.assertRaises(ValueError): intake.read_words({'segments': [{'text': 'No words'}]})

    def test_no_invented_times_for_unmatched_opening_and_ending(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder); (path / 'video-1.md').write_text(' '.join(self.reference))
            words = [{'word': w, 'start': 100 + i * .3, 'end': 100.2 + i * .3} for i, w in enumerate(self.reference[5:35])]
            candidate = intake.script_index(path, words, 4)[0]['candidates'][0]
            self.assertEqual(candidate['start'], 100)
            self.assertAlmostEqual(candidate['end'], 108.9)
            self.assertTrue(candidate['requires_review'])

    def test_metadata_allowlist_discards_download_urls_and_tokens(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / 'metadata.json'
            path.write_text(json.dumps({'selected': {'id': '123', 'size': 10, 'access_token': 'secret', 'download_url': 'signed'}}))
            self.assertEqual(intake.safe_drive(path), {'id': '123', 'size': 10})

    def test_partial_source_failure_has_nonzero_exit_and_receipt(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder); source = root / 'video.mp4.incomplete'; source.write_bytes(b'partial')
            out = root / 'output'
            result = subprocess.run([sys.executable, str(Path(intake.__file__)), '--source', str(source), '--out', str(out)], capture_output=True, text=True)
            self.assertEqual(result.returncode, 1)
            receipt = json.loads((out / 'intake-manifest.json').read_text())
            self.assertEqual(receipt['status'], 'failed')
            self.assertTrue(receipt['errors'])
            self.assertFalse(receipt['transcription_executed'])


if __name__ == '__main__':
    unittest.main()
