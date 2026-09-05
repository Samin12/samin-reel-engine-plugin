import unittest
from retime_timeline import retime


class RetimeTests(unittest.TestCase):
    def setUp(self):
        self.spec = {'source': {'segments': [{'start': 0, 'end': 5}]},
                     'shots': [{'start': 0, 'end': 3}, {'start': 3, 'end': 5}],
                     'labels': [{'start': 2, 'end': 4}],
                     'sfx': [{'at': 3.5, 'duration': .4}],
                     'zooms': [{'at': 1.5, 'duration': 2, 'scale': 1.1}]}
        self.cuts = {'source_duration': 5, 'cuts': [{'start': 2, 'end': 3}]}

    def test_retimes_all_boundaries_without_chopping_sound(self):
        result = retime(self.spec, self.cuts, 'new.mp4', 'words.json')
        self.assertEqual(result['shots'], [{'start': 0, 'end': 2}, {'start': 2, 'end': 4}])
        self.assertEqual(result['labels'], [{'start': 2, 'end': 3}])
        self.assertEqual(result['sfx'], [{'at': 2.5, 'duration': .4}])
        self.assertEqual(result['zooms'][0]['duration'], 1)
        self.assertEqual(self.spec['shots'][0]['end'], 3)

    def test_rejects_stale_clock_and_preexisting_music(self):
        with self.assertRaisesRegex(ValueError, 'clock'):
            retime(self.spec, {**self.cuts, 'source_duration': 6}, 'x', 'y')
        with self.assertRaisesRegex(ValueError, 'music'):
            retime({**self.spec, 'music': [{}]}, self.cuts, 'x', 'y')


if __name__ == '__main__':
    unittest.main()
