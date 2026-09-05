import unittest
from edit import map_words, caption_groups, phrase_groups, escape


class TimelineTests(unittest.TestCase):
    def test_cut_and_reordered_source_times_preserve_word_sync(self):
        words=[{"word":"first","start":1.1,"end":1.5},{"word":"middle","start":5.2,"end":5.6},{"word":"later","start":6.7,"end":7.1}]
        mapped=map_words(words,[{"start":5,"end":7},{"start":1,"end":2}])
        self.assertEqual([w["word"] for w in mapped],["middle","later","first"])
        self.assertAlmostEqual(mapped[0]["start"],.2)
        self.assertAlmostEqual(mapped[1]["end"],2)
        self.assertAlmostEqual(mapped[2]["start"],2.1)

    def test_removed_words_do_not_leak_into_captions(self):
        words=[{"word":"cut","start":0,"end":1},{"word":"keep","start":2,"end":3}]
        self.assertEqual([w["word"] for w in map_words(words,[{"start":2,"end":3}])],["keep"])

    def test_invalid_times_are_rejected(self):
        with self.assertRaises(ValueError):
            map_words([{"word":"bad","start":2,"end":1}],[{"start":0,"end":3}])

    def test_caption_group_breaks_at_pauses_and_length(self):
        words=[{"word":str(n),"start":n*.2,"end":n*.2+.15} for n in range(6)]
        words[4]["start"],words[4]["end"]=2,2.15
        words[5]["start"],words[5]["end"]=2.2,2.35
        groups=caption_groups(words,max_words=3,max_chars=27)
        self.assertEqual([len(g) for g in groups],[3,1,2])
        self.assertNotIn("<script>",escape("<script>"))

    def test_reviewed_phrases_preserve_every_spoken_word(self):
        words=[{"word":str(i),"start":i,"end":i+.8} for i in range(6)]
        groups=phrase_groups(words,[{"word_range":[0,4],"line_breaks":[2]}, {"word_range":[4,6]}])
        self.assertEqual([w["word"] for group in groups for w in group], [str(i) for i in range(6)])
        for phrases in ([{"word_range":[0,3]}], [{"word_range":[0,4]}, {"word_range":[3,6]}], [{"word_range":[0,6],"line_breaks":[6]}]):
            with self.assertRaises(ValueError):
                phrase_groups(words,phrases)


if __name__=="__main__":
    unittest.main()
