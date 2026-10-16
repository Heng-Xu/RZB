"""引文重排及对应关系的正反例。"""
import unittest
from report_citations import arrange, validate, stream


class CitationChecks(unittest.TestCase):
    def test_first_appearance_repeat_and_cluster_sort(self):
        text, refs, rows = arrange('甲[9]。乙[4][9]。丙[2—4]。丁[9,2,9]。',
                                  {2:'乙文',3:'丙文',4:'丁文',9:'甲文'})
        self.assertEqual(stream(text), [[1],[1,2],[2,3,4],[1,3]])
        self.assertEqual([r['原编号'] for r in rows], [9,4,2,3])
        self.assertIn('[1] 甲文', refs)

    def test_missing_and_duplicate_sources(self):
        for body, registry in [('正文[7]', {1:'文献'}), ('正文[1,2]', {1:'同文',2:'同文'})]:
            with self.assertRaises(AssertionError): arrange(body, registry)

    def test_reject_misordered_or_unmatched_final(self):
        for body, entries in [('甲[2]乙[1]', ['一','二']), ('甲[1,1]', ['一']),
                              ('甲[1]乙[3]', ['一','二']), ('甲[1]', ['一','二']),
                              ('甲[1]乙[2,1]', ['一','二'])]:
            with self.assertRaises(AssertionError): validate(body, entries)


if __name__ == '__main__': unittest.main()
