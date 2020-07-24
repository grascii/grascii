
import unittest

from typing import List, Tuple

from grascii import regen, grammar

class TestAnnotationRegex(unittest.TestCase):

    def check_strictness_low(self, annotations: List[str], texts: List[Tuple[str, str]]):
        builder = regen.RegexBuilder(annotation_mode=regen.Strictness.LOW)
        for a in annotations:
            for t in texts:
                regex = builder.make_annotation_regex(t[0], a)
                self.assertRegex(t[0] + t[1], regex)

    def test_strictness_low_circle_vowel(self):
        annotations = [
            [],
            [","],
            ["~", ","]
        ]
        texts = [("A", ""), ("A", "~"), ("A", "|."), ("A", "~|,_"),
                 ("E", ""), ("E", "~"), ("E", "|."), ("E", "~|,_"),]
        self.check_strictness_low(annotations, texts)

    def test_strictness_low_hook_vowel(self):
        annotations_o = [
            [],
            [","],
            ["(", ","],
            ["(", "_"]
        ]
        texts_o = [("O", ""), ("O", "("), ("O", "(,"), ("O", "(._")]
        annotations_u = [
            [],
            [","],
            [")", ","],
            [")", "_"]
        ]
        texts_u = [("U", ""), ("U", ")"), ("U", "),"), ("U", ")._")]
        self.check_strictness_low(annotations_o, texts_o)
        self.check_strictness_low(annotations_u, texts_u)

    def test_strictness_low_circle_diphthong(self):
        annotations = [
            [],
            ["~"],
            ["~|"],
            ["_"],
        ]
        texts = [("I", ""), ("I", "~"), ("I", "_"), ("I~|_"),
                ("A&E", ""), ("A&E", "~"), ("A&E", "_"), ("A&E~|_"),    
                ("A'E", ""), ("A'E", "~"), ("A'E", "_"), ("A'E~|_")]
        self.check_strictness_low(annotations, texts)
                
    def test_strictness_low_hook_diphthong(self):
        annotations = [
            [],
            ["_"],
        ]
        texts = [("AU", ""), ("AU", "_"),
                 ("OE", ""), ("OE", "_"),
                 ("EU", ""), ("EU", "_")]
        self.check_strictness_low(annotations, texts)

    def test_strictness_low_directed_consonant(self):
        annotations = [
            [],
            ["("],
            [")"],
            [","],
            ["(,"]
        ]
        texts = [("S", ""), ("S", "("), ("S", "),"),
                ("Z", ""), ("Z", "("), ("Z", "),"),
                ("TH", ""), ("TH", "("), ("TH", "),")]
        self.check_strictness_low(annotations, texts)

    def test_strictness_low_oblique_consonant(self):
        annotations = [
            [],
            [","]
        ]
        texts = [("SH", ""), ("SH", ",")]
        self.check_strictness_low(annotations, texts)


         

    

if __name__ == "__main__":
    unittest.main()
