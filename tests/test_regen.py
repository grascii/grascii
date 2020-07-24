
import unittest

from grascii import regen, grammar

class TestAnnotationRegex(unittest.TestCase):

    def test_strictness_low_circle_vowel(self):
        builder = regen.RegexBuilder(annotation_mode=regen.Strictness.LOW)

        annotations = [
            [],
            [","],
            ["~", ","]
        ]

        text = ["A", "A~", "A~|", "A,", "A~|._"]

        for an in annotations:
            regex = builder.make_annotation_regex("A", an)
            for t in text:
                self.assertRegex(t, regex)

    def test_strictness_low_hook_vowel(self):
        builder = regen.RegexBuilder(annotation_mode=regen.Strictness.LOW)

        annotations = [
            [],
            [","],
            ["(", ","]
        ]

        text = ["O", "O(", "O,", "O(._"]

        for an in annotations:
            regex = builder.make_annotation_regex("O", an)
            for t in text:
                self.assertRegex(t, regex)

    def test_strictness_low_circle_diphthong(self):
        builder = regen.RegexBuilder(annotation_mode=regen.Strictness.LOW)

        annotations = [
            [],
            ["~"],
            ["~|"],
            ["_"],
        ]

        text = ["A&E", "A&E~", "A&E~|_"]

        for an in annotations:
            regex = builder.make_annotation_regex("A&E", an)
            for t in text:
                self.assertRegex(t, regex)
                
    def test_strictness_low_hook_diphthong(self):
        builder = regen.RegexBuilder(annotation_mode=regen.Strictness.LOW)

        annotations = [
            [],
            ["_"],
        ]

        text = ["AU", "AU_"]

        for an in annotations:
            regex = builder.make_annotation_regex("AU", an)
            for t in text:
                self.assertRegex(t, regex)

    def test_strictness_low_directed_consonant(self):
        builder = regen.RegexBuilder(annotation_mode=regen.Strictness.LOW)

        annotations = [
            [],
            ["("],
            [")"],
            [","],
            ["(,"]
        ]

        text = ["S", "S)", "S(,"]

        for an in annotations:
            regex = builder.make_annotation_regex("S", an)
            for t in text:
                self.assertRegex(t, regex)

    def test_strictness_low_oblique_consonant(self):
        builder = regen.RegexBuilder(annotation_mode=regen.Strictness.LOW)

        annotations = [
            [],
            [","]
        ]

        text = ["SH", "SH,"]

        for an in annotations:
            regex = builder.make_annotation_regex("SH", an)
            for t in text:
                self.assertRegex(t, regex)


         

    

if __name__ == "__main__":
    unittest.main()
