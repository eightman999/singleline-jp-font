"""Local tests for honest kanji coverage (no network or third-party geometry)."""
import copy
import json
from collections import defaultdict
import unittest
from unittest.mock import patch

from family import kanji


class KanjiCoverageTests(unittest.TestCase):
    def test_canonical_is_preserved(self):
        generated,report=kanji.build_kanji(kanji.CANONICAL)
        self.assertEqual(set(generated),set(kanji.CANONICAL))
        for char,glyph in kanji.CANONICAL.items():
            self.assertEqual(generated[char],[list(path) for path in glyph])
            self.assertEqual(report[char]['status'],'canonical')

    def test_missing_has_no_placeholder(self):
        glyphs,report=kanji.build_kanji(['\U0003134a'])
        self.assertFalse(glyphs)
        self.assertEqual(report['\U0003134a']['status'],'missing')
        self.assertTrue(report['\U0003134a']['reasons'])

    def test_numbered_ids_placeholder_never_rendered(self):
        components,sources,trees=kanji._sources()
        trees={**trees,'\U0003134a':[{'tree':['⿱','一','⑧'],'sequence':'⿱一⑧','regions':''}]}
        with patch.object(kanji,'_sources',return_value=(components,sources,trees)):
            glyphs,report=kanji.build_kanji(['\U0003134a'])
        self.assertFalse(glyphs)
        self.assertIn('ambiguous_ids_placeholder:⑧',report['\U0003134a']['reasons'])

    def test_blank_does_not_count_as_coverage(self):
        components,sources,trees=kanji._sources()
        components={**components,'\U0003134a':[]}
        sources={**sources,'\U0003134a':'test_blank'}
        with patch.object(kanji,'_sources',return_value=(components,sources,trees)):
            glyphs,report=kanji.build_kanji(['\U0003134a'])
        self.assertFalse(glyphs)
        self.assertIn('blank_geometry',report['\U0003134a']['reasons'])

    def test_duplicate_does_not_count_as_new_coverage(self):
        components,sources,trees=kanji._sources()
        components={**components,'\U0003134a':copy.deepcopy(kanji.CANONICAL['田'])}
        sources={**sources,'\U0003134a':'test_duplicate'}
        with patch.object(kanji,'_sources',return_value=(components,sources,trees)):
            glyphs,report=kanji.build_kanji(['田','\U0003134a'])
        self.assertEqual(set(glyphs),{'田'})
        self.assertEqual(report['\U0003134a']['status'],'missing')
        self.assertIn('duplicate_geometry:田',report['\U0003134a']['reasons'])

    def test_compatibility_scalar_is_not_normalized(self):
        glyphs,report=kanji.build_kanji(['者','者'])
        self.assertEqual(set(glyphs),{'者','者'})
        self.assertNotEqual(glyphs['者'],glyphs['者'])
        self.assertFalse(report['者']['visually_reviewed'])

    def test_complete_target_has_real_distinct_geometry(self):
        entries=json.loads((kanji.DATA/'jisx0213-2004.json').read_text())['entries']
        targets={e['text'] for e in entries if e['level']>0}
        glyphs,report=kanji.build_kanji(targets)
        self.assertEqual(len(targets),10050)
        self.assertEqual(set(glyphs),targets)
        groups=defaultdict(list)
        for char,glyph in glyphs.items():
            kanji.validate_glyph(glyph)
            self.assertFalse(report[char]['visually_reviewed'])
            groups[kanji.geometry_fingerprint(glyph)].append(char)
        for group in groups.values():
            if len(group)>1:
                self.assertTrue(set(group)<=kanji.CANONICAL.keys(),group)
        names={e['text'] for e in json.loads((kanji.DATA/'unicode-jinmeiyo.json').read_text())['entries']}
        self.assertEqual(len(names),864)
        self.assertFalse(names-glyphs.keys())

    def test_reviewed_error_sites_use_explicit_structure_drafts(self):
        corrected=set('戾魃兩歷癧藶魎㒼鬮籤爨')
        glyphs,report=kanji.build_kanji(corrected)
        self.assertEqual(set(glyphs),corrected)
        for char in corrected:
            self.assertNotIn(char,kanji.CANONICAL)
            self.assertEqual(report[char]['geometry_source'],'new_project_authored_structure_correction')
            self.assertEqual(report[char]['status'],'component_draft')
            self.assertFalse(report[char]['visually_reviewed'])
        # Regression: top bar/stem must meet the broad two-person frame.
        self.assertEqual(glyphs['兩'][0],[(1.0,2.0),(23.0,2.0)])
        self.assertEqual(glyphs['兩'][1],[(3.0,23.0),(3.0,6.0),(21.0,6.0),(21.0,23.0),(18.0,23.0)])
        self.assertEqual(glyphs['兩'][2],[(12.0,2.0),(12.0,23.0)])

    def test_history_foot_is_a_separate_bottom_band(self):
        glyphs,_=kanji.build_kanji('歷癧藶')
        expected=kanji.fit(kanji.CANONICAL['止'],6,15,18,9)
        self.assertEqual(glyphs['歷'][-4:],expected)
        self.assertLessEqual(max(y for path in glyphs['歷'][1:-4] for _,y in path),14)
        for char in '癧藶':
            self.assertGreater(min(y for path in glyphs[char][-4:] for _,y in path),17)
            self.assertGreater(max(y for path in glyphs[char][-4:] for _,y in path),22)

    def test_target_validation(self):
        with self.assertRaises(ValueError):kanji.build_kanji(['日本'])

    def test_surname_extras_are_real_and_distinct(self):
        glyphs,report=kanji.build_kanji('高髙吉𠮷')
        self.assertEqual(len(glyphs),4)
        self.assertNotEqual(glyphs['高'],glyphs['髙'])
        self.assertNotEqual(glyphs['吉'],glyphs['𠮷'])

if __name__=='__main__':unittest.main()
