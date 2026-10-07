"""Focused repertoire/source tests for original non-Kanji additions."""
import math
import unittest
import unicodedata as ud

from family import jis_symbols as symbols
from family.data_loader import load_glyphs
from family.repertoire import standards


class JISSymbolTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.glyphs,_ = load_glyphs(expand_kanji=False)
        cls.jis,_ = standards()

    def test_all_jis_nonkanji_identities(self):
        wanted={e['text'] for e in self.jis['entries'] if e['level']==0}
        self.assertEqual(len(wanted),1183)
        self.assertFalse(wanted-self.glyphs.keys())

    def test_all_jis_multiscalar_identities(self):
        wanted={e['text'] for e in self.jis['entries'] if len(e['text'])>1}
        self.assertEqual(len(wanted),25)
        self.assertFalse(wanted-self.glyphs.keys())
        self.assertEqual(self.glyphs['˩˥'].paths,symbols.GLYPHS['˩˥'])
        self.assertEqual(self.glyphs['˥˩'].paths,symbols.GLYPHS['˥˩'])

    def test_source_bounds_and_nonblank_geometry(self):
        for char,paths in symbols.GLYPHS.items():
            with self.subTest(char=char):
                self.assertTrue(paths)
                for path in paths:
                    self.assertGreaterEqual(len(path),2)
                    for x,y in path:
                        self.assertTrue(math.isfinite(x) and math.isfinite(y))
                        self.assertTrue(0<=x<=24)
                        self.assertTrue(0<=y<=(25 if char in symbols.MARKS else 24))
                self.assertTrue(any(a!=b for p in paths for a,b in zip(p,p[1:])))

    def test_marks_are_zero_width(self):
        self.assertEqual(len(symbols.MARKS),23)
        for char in symbols.MARKS:
            self.assertTrue(ud.category(char).startswith('M'))
            self.assertEqual(symbols.ADVANCES[char],0)
            self.assertEqual(self.glyphs[char].advance,0)
            self.assertEqual(self.glyphs[char].category,'mark')

    def test_negative_enclosure_protocol(self):
        self.assertEqual(len(symbols.NEGATIVE),20)
        self.assertFalse(symbols.NEGATIVE & symbols.FILLED)
        for char in symbols.NEGATIVE:
            paths=symbols.GLYPHS[char]
            self.assertEqual(paths[0][0],paths[0][-1])
            self.assertGreater(len(paths),1)
            self.assertTrue(self.glyphs[char].notes['negative'])

    def test_box_weight_identities_are_distinct(self):
        self.assertEqual(len(symbols.BOXES),32)
        self.assertNotEqual(symbols.GLYPHS['─'],symbols.GLYPHS['━'])
        self.assertNotEqual(symbols.GLYPHS['┠'],symbols.GLYPHS['┝'])
        self.assertTrue(set(symbols.BOXES)<=symbols.FILLED)

    def test_black_and_white_shapes_keep_different_fill_semantics(self):
        for white,black in [('◇','◆'),('▷','▶'),('♤','♠'),('♧','♣'),('☖','☗')]:
            self.assertNotIn(white,symbols.FILLED)
            self.assertIn(black,symbols.FILLED)
            self.assertEqual(symbols.GLYPHS[white],symbols.GLYPHS[black])

    def test_math_equality_has_two_bars(self):
        for char in '⋚⋛':
            horizontal=[p for p in symbols.GLYPHS[char] if len(p)==2 and p[0][1]==p[1][1]]
            self.assertEqual(len(horizontal),2)


if __name__=='__main__':
    unittest.main()
