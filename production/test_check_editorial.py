"""Counterexamples for mechanical checks; fixture reviews are not real approvals."""
import copy
import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from check_editorial import check


class EditorialChecks(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.words = {'words': [
            {'word': "Don't", 'start': 0, 'end': .4},
            {'word': 'skip', 'start': .5, 'end': .8},
            {'word': 'context.', 'start': 1, 'end': 1.4}]}
        self.timeline = {'output': {'width': 1080, 'height': 1920, 'fps': 30},
                         'shots': [{'id': 'shot1', 'start': 0, 'end': 2}]}
        self.assets = {'assets': [{'id': 'diagram', 'shot_ids': ['shot1']}]}
        beat = {
            'beat_id': 'beat1', 'spoken_text': 'DON’T skip context!', 'word_range': [0, 3],
            'output_interval': {'start': 0, 'end': 2}, 'viewer_question': 'What matters?',
            'primary_job': 'explanation',
            'visual': {'asset_ids': ['diagram'], 'shot_ids': ['shot1'],
                       'representation': 'original_diagram', 'truth_status': 'illustrative',
                       'visible_content': 'A context diagram', 'fit_reason': 'Explains context',
                       'expected_takeaway': 'Context matters', 'proof_scope': None,
                       'evidence_refs': [], 'limitations': ['Concept only'],
                       'on_screen_label': 'CONCEPT', 'rejected_alternatives': []},
            'timing': {'anchor_text': "Don't", 'anchor_word_index': 0, 'anchor_time': 0,
                       'reveal_time': 0, 'timing_reason': 'With the word',
                       'stable_hold': {'start': .1, 'end': 1.9}, 'required_read_text': '',
                       'readability_reason': 'No text must be read'},
            'placement': {'layout': 'full_screen',
                          'focal_rect': {'x': .1, 'y': .1, 'width': .8, 'height': .4},
                          'caption_rect': None, 'presenter_face_rect': None,
                          'must_remain_visible': [], 'safe_area_check': 'not_checked',
                          'focus_reason': 'One concept'},
            'assessment': {'status': 'planned', 'viewed_render_span': None,
                           'observed_takeaway': None, 'hard_failures': [], 'revision': None}}
        self.data = {
            'schema_version': 1, 'reel_id': 'fixture', 'revision': 'test',
            'words_path': 'words.json', 'timeline_path': 'timeline.json',
            'asset_index_path': 'assets.json', 'reference_refs': [],
            'canvas': {'width': 1080, 'height': 1920, 'fps': 30, 'duration': 2,
                       'platform': 'instagram', 'reserved_regions': []}, 'beats': [beat],
            'review': {'status': 'not_reviewed', 'reviewer': None, 'reviewed_at': None,
                       'render_path': None, 'render_sha256': None,
                       'whole_render_watched_with_sound': False, 'phone_size_motion_checked': False,
                       'checked_spans': [], 'unmapped_beat_ids': [], 'unresolved_hard_failures': [],
                       'scores': None, 'total_score': None,
                       'reference_comparison': 'Pending', 'conclusion': 'Pending'}}

    def run_check(self):
        for name, data in [('words', self.words), ('timeline', self.timeline),
                           ('assets', self.assets), ('map', self.data)]:
            (self.root / (name + '.json')).write_text(json.dumps(data))
        return check(self.root / 'map.json')

    def assert_error(self, substring):
        result = self.run_check()
        self.assertFalse(result['mechanical_ready'], result)
        self.assertTrue(any(substring in e for e in result['errors']), result)

    def test_planned_map_can_be_mechanically_ready_without_semantic_approval(self):
        result = self.run_check()
        self.assertTrue(result['mechanical_ready'], result)
        self.assertTrue(result['requires_semantic_review'])
        self.assertEqual(result['recorded_review_status'], 'not_reviewed')

    def test_unknown_and_wrong_joined_assets(self):
        self.data['beats'][0]['visual']['asset_ids'] = ['missing']
        self.assert_error('unknown asset')
        self.data['beats'][0]['visual']['asset_ids'] = ['diagram']
        self.assets['assets'][0]['shot_ids'] = ['other-shot']
        self.assert_error('not joined')

    def test_missing_middle_word_is_detected(self):
        first = self.data['beats'][0]
        second = copy.deepcopy(first)
        first.update(word_range=[0, 1], spoken_text="Don't")
        second.update(beat_id='beat2', word_range=[2, 3], spoken_text='context')
        second['timing'].update(anchor_word_index=2, anchor_time=1, anchor_text='context')
        self.data['beats'].append(second)
        self.assert_error('cover every word')

    def test_spoken_claim_cannot_change_with_same_word_range(self):
        self.data['beats'][0]['spoken_text'] = 'Always skip context'
        self.assert_error('spoken_text differs')

    def test_anchor_tolerance_and_stable_hold(self):
        self.data['beats'][0]['timing']['anchor_time'] = .15
        self.assertTrue(self.run_check()['mechanical_ready'])
        self.data['beats'][0]['timing']['anchor_time'] = .151
        self.assert_error('anchor time differs')
        self.data['beats'][0]['timing']['anchor_time'] = 0
        self.data['beats'][0]['timing']['stable_hold']['end'] = 2.1
        self.assert_error('stable_hold')

    def test_out_of_canvas_rect_and_nonoverlapping_shot(self):
        self.data['beats'][0]['placement']['focal_rect']['x'] = .3
        self.assert_error('rectangle exceeds')
        self.data['beats'][0]['placement']['focal_rect']['x'] = .1
        self.timeline['shots'][0].update(start=2, end=3)
        self.assert_error('does not overlap')

    def test_score_sum_is_checked(self):
        names = ('semantic_fit', 'evidence_honesty', 'timing_readability',
                 'composition_focus', 'reference_voice_coherence')
        self.data['review']['scores'] = {n: {'score': 4, 'evidence': 'Fixture', 'revision': None} for n in names}
        self.data['review']['total_score'] = 19
        self.assert_error('total_score')

    def test_changed_render_invalidates_recorded_pass(self):
        render = self.root / 'render.mp4'
        render.write_bytes(b'fixture render, not real media')
        self.test_score_sum_is_checked()
        self.data['review'].update(status='passed', reviewer='Fixture reviewer',
            reviewed_at='2026-09-04T12:00:00Z', render_path='render.mp4',
            render_sha256=hashlib.sha256(render.read_bytes()).hexdigest(),
            whole_render_watched_with_sound=True, phone_size_motion_checked=True,
            checked_spans=[{'interval': {'start': 0, 'end': 2}, 'observation': 'Fixture'}],
            total_score=20)
        self.data['beats'][0]['assessment'].update(status='passed',
            viewed_render_span={'start': 0, 'end': 2}, observed_takeaway='Fixture')
        self.data['beats'][0]['placement']['safe_area_check'] = 'clear'
        result = self.run_check()
        self.assertTrue(result['mechanical_ready'], result)
        self.assertTrue(result['requires_semantic_review'])
        render.write_bytes(b'changed picture after review')
        self.assert_error('stale approval')

    def test_schema_rejects_fake_product_proof(self):
        self.data['beats'][0]['primary_job'] = 'proof'
        self.assert_error('schema:')


if __name__ == '__main__':
    unittest.main()
