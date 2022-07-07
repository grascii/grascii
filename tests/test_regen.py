from __future__ import annotations

import re
import unittest
from typing import List, Tuple

from grascii import grammar, regen


class TestAnnotationRegex(unittest.TestCase):
    def check_strictness_low(
        self, annotations: List[str], texts: List[Tuple[str, str]]
    ):
        builder = regen.RegexBuilder(annotation_mode=regen.Strictness.LOW)
        for a in annotations:
            for t in texts:
                regex = builder.make_annotation_regex(t[0], a)
                self.assertRegex(t[0] + t[1], regex)

    def test_strictness_low_circle_vowel(self):
        annotations = [[], [","], ["~", ","]]
        texts = [
            ("A", ""),
            ("A", "~"),
            ("A", "|."),
            ("A", "~|,_"),
            ("E", ""),
            ("E", "~"),
            ("E", "|."),
            ("E", "~|,_"),
        ]
        self.check_strictness_low(annotations, texts)

    def test_strictness_low_hook_vowel(self):
        annotations_o = [[], [","], ["(", ","], ["(", "_"]]
        texts_o = [("O", ""), ("O", "("), ("O", "(,"), ("O", "(._")]
        annotations_u = [[], [","], [")", ","], [")", "_"]]
        texts_u = [("U", ""), ("U", ")"), ("U", "),"), ("U", ")._")]
        self.check_strictness_low(annotations_o, texts_o)
        self.check_strictness_low(annotations_u, texts_u)

    def test_strictness_low_circle_diphthong(self):
        annotations = [
            [],
            ["~"],
            ["~", "|"],
            ["_"],
        ]
        texts = [
            ("I", ""),
            ("I", "~"),
            ("I", "_"),
            ("I~|_"),
            ("A&E", ""),
            ("A&E", "~"),
            ("A&E", "_"),
            ("A&E~|_"),
            ("A'E", ""),
            ("A'E", "~"),
            ("A'E", "_"),
            ("A'E~|_"),
        ]
        self.check_strictness_low(annotations, texts)

    def test_strictness_low_hook_diphthong(self):
        annotations = [
            [],
            ["_"],
        ]
        texts = [
            ("AU", ""),
            ("AU", "_"),
            ("OE", ""),
            ("OE", "_"),
            ("EU", ""),
            ("EU", "_"),
        ]
        self.check_strictness_low(annotations, texts)

    def test_strictness_low_directed_consonant(self):
        annotations = [[], ["("], [")"], [","], ["(,"]]
        texts = [
            ("S", ""),
            ("S", "("),
            ("S", "),"),
            ("Z", ""),
            ("Z", "("),
            ("Z", "),"),
            ("TH", ""),
            ("TH", "("),
            ("TH", "),"),
        ]
        self.check_strictness_low(annotations, texts)

    def test_strictness_low_oblique_consonant(self):
        annotations = [[], [","]]
        texts = [("SH", ""), ("SH", ",")]
        self.check_strictness_low(annotations, texts)

    def check_strictness_medium(self, strokes, tests):
        builder = regen.RegexBuilder(annotation_mode=regen.Strictness.MEDIUM)
        for stroke in strokes:
            for test in tests:
                annotations = test[0]
                for text, expected in test[1]:
                    regex = builder.make_annotation_regex(stroke, annotations)
                    with self.subTest(annotations=annotations, text=stroke + text):
                        if expected:
                            self.assertRegex(stroke + text, regex)
                        else:
                            self.assertNotRegex(stroke + text, regex)

    def test_strictness_medium_circle_vowel(self):
        circle_vowels = ["A", "E"]
        tests = [
            ([], [("", True), (",", True), ("~|._", True)]),
            ([","], [("", False), (".", False), (",", True), ("~|,_", True)]),
            (["~"], [("", False), ("~", True), (".", False), ("~|._", True)]),
            (
                ["~", "|", ".", "_"],
                [
                    ("~", False),
                    ("|", False),
                    (".", False),
                    ("_", False),
                    ("~|._", True),
                ],
            ),
        ]
        self.check_strictness_medium(circle_vowels, tests)

    def test_strictness_medium_hook_vowel(self):
        tests1 = [
            ([], [("", True), (",", True), ("(,_", True)]),
            ([","], [("", False), (".", False), (",", True), ("(,_", True)]),
            (["("], [("", False), (".", False), ("(,_", True)]),
            (["(", ".", "_"], [(".", False), ("_", False), ("(._", True)]),
        ]
        tests2 = [
            ([], [("", True), (",", True), ("),_", True)]),
            ([","], [("", False), (".", False), (",", True), ("),_", True)]),
            ([")"], [("", False), (".", False), ("),_", True)]),
            ([")", ".", "_"], [(".", False), ("_", False), (")._", True)]),
        ]
        self.check_strictness_medium(["O"], tests1)
        self.check_strictness_medium(["U"], tests2)

    def test_strictness_medium_circle_diphthong(self):
        strokes = ["I", "A&E", "A&'"]
        tests = [
            ([], [("", True), ("~", True), ("|", True), ("_", True), ("~|_", True)]),
            (
                ["~"],
                [("", False), ("~", True), ("|", False), ("_", False), ("~|_", True)],
            ),
            (
                ["|"],
                [("", False), ("~", False), ("|", True), ("_", False), ("~|_", True)],
            ),
            (
                ["_"],
                [("", False), ("~", False), ("|", False), ("_", True), ("~|_", True)],
            ),
            (
                ["~", "|", "_"],
                [("", False), ("~", False), ("|", False), ("_", False), ("~|_", True)],
            ),
        ]
        self.check_strictness_medium(strokes, tests)

    def test_strictness_medium_hook_diphthong(self):
        strokes = ["AU", "OE", "EU"]
        tests = [
            ([], [("", True), ("_", True)]),
            (["_"], [("", False), ("_", True)]),
        ]
        self.check_strictness_medium(strokes, tests)

    def test_strictness_medium_directed_consonant(self):
        strokes = ["S", "Z", "TH"]
        tests = [
            (
                [],
                [
                    ("", True),
                    ("(", True),
                    (")", True),
                    (",", True),
                    ("(,", True),
                    ("),", True),
                ],
            ),
            (
                ["("],
                [
                    ("", False),
                    ("(", True),
                    (")", False),
                    (",", False),
                    ("(,", True),
                    ("),", False),
                ],
            ),
            (
                [")"],
                [
                    ("", False),
                    ("(", False),
                    (")", True),
                    (",", False),
                    ("(,", False),
                    ("),", True),
                ],
            ),
            (
                ["(", ","],
                [
                    ("", False),
                    ("(", False),
                    (")", False),
                    (",", False),
                    ("(,", True),
                    ("),", False),
                ],
            ),
            (
                [")", ","],
                [
                    ("", False),
                    ("(", False),
                    (")", False),
                    (",", False),
                    ("(,", False),
                    ("),", True),
                ],
            ),
        ]
        self.check_strictness_medium(strokes, tests)

    def test_strictness_medium_oblique_consonant(self):
        tests = [
            ([], [("", True), (",", True)]),
            ([","], [("", False), (",", True)]),
        ]
        self.check_strictness_medium(["SH"], tests)

    def check_strictness_high(self, strokes, tests):
        builder = regen.RegexBuilder(annotation_mode=regen.Strictness.HIGH)
        for stroke in strokes:
            for test in tests:
                annotations = test[0]
                for text, expected in test[1]:
                    regex = builder.make_annotation_regex(stroke, annotations)
                    with self.subTest(annotations=annotations, text=stroke + text):
                        if expected:
                            self.assertTrue(re.fullmatch(regex, stroke + text))
                        else:
                            self.assertFalse(re.fullmatch(regex, stroke + text))

    def test_strictness_high_circle_vowel(self):
        circle_vowels = ["A", "E"]
        tests = [
            ([], [("", True), (",", False), ("~|._", False)]),
            ([","], [("", False), (".", False), (",", True), ("~|,_", False)]),
            (["~"], [("", False), ("~", True), (".", False), ("~|._", False)]),
            (
                ["~", "|", ".", "_"],
                [
                    ("~", False),
                    ("|", False),
                    (".", False),
                    ("_", False),
                    ("~|._", True),
                ],
            ),
        ]
        self.check_strictness_high(circle_vowels, tests)

    def test_strictness_high_hook_vowel(self):
        tests1 = [
            ([], [("", True), (",", False), ("(,_", False)]),
            ([","], [("", False), (".", False), (",", True), ("(,_", False)]),
            (["("], [("", False), (".", False), ("(,_", False)]),
            (["(", ".", "_"], [(".", False), ("_", False), ("(._", True)]),
        ]
        tests2 = [
            ([], [("", True), (",", False), ("),_", False)]),
            ([","], [("", False), (".", False), (",", True), ("),_", False)]),
            ([")"], [("", False), (".", False), ("),_", False)]),
            ([")", ".", "_"], [(".", False), ("_", False), (")._", True)]),
        ]
        self.check_strictness_high(["O"], tests1)
        self.check_strictness_high(["U"], tests2)

    def test_strictness_high_circle_diphthong(self):
        strokes = ["I", "A&E", "A&'"]
        tests = [
            (
                [],
                [("", True), ("~", False), ("|", False), ("_", False), ("~|_", False)],
            ),
            (
                ["~"],
                [("", False), ("~", True), ("|", False), ("_", False), ("~|_", False)],
            ),
            (
                ["|"],
                [("", False), ("~", False), ("|", True), ("_", False), ("~|_", False)],
            ),
            (
                ["_"],
                [("", False), ("~", False), ("|", False), ("_", True), ("~|_", False)],
            ),
            (
                ["~", "|", "_"],
                [("", False), ("~", False), ("|", False), ("_", False), ("~|_", True)],
            ),
        ]
        self.check_strictness_high(strokes, tests)

    def test_strictness_high_hook_diphthong(self):
        strokes = ["AU", "OE", "EU"]
        tests = [
            ([], [("", True), ("_", False)]),
            (["_"], [("", False), ("_", True)]),
        ]
        self.check_strictness_high(strokes, tests)

    def test_strictness_high_directed_consonant(self):
        strokes = ["S", "Z", "TH"]
        tests = [
            (
                [],
                [
                    ("", True),
                    ("(", False),
                    (")", False),
                    (",", False),
                    ("(,", False),
                    ("),", False),
                ],
            ),
            (
                ["("],
                [
                    ("", False),
                    ("(", True),
                    (")", False),
                    (",", False),
                    ("(,", False),
                    ("),", False),
                ],
            ),
            (
                [")"],
                [
                    ("", False),
                    ("(", False),
                    (")", True),
                    (",", False),
                    ("(,", False),
                    ("),", False),
                ],
            ),
            (
                ["(", ","],
                [
                    ("", False),
                    ("(", False),
                    (")", False),
                    (",", False),
                    ("(,", True),
                    ("),", False),
                ],
            ),
            (
                [")", ","],
                [
                    ("", False),
                    ("(", False),
                    (")", False),
                    (",", False),
                    ("(,", False),
                    ("),", True),
                ],
            ),
        ]
        self.check_strictness_high(strokes, tests)

    def test_strictness_high_oblique_consonant(self):
        tests = [
            ([], [("", True), (",", False)]),
            ([","], [("", False), (",", True)]),
        ]
        self.check_strictness_high(["SH"], tests)

    def test_out_of_order_annotations(self):
        pass

    def test_invalid_annotations(self):
        pass

    def test_mutually_exclusive_annotations(self):
        pass


class RegexBuilderTester(unittest.TestCase):
    def run_tests(self, builder, tests):
        for test in tests:
            interp = test[0]
            for text, expected in test[1]:
                regex = builder.build_regex(interp)
                with self.subTest(interpretation=interp, text=text):
                    if expected:
                        self.assertRegex(text, regex)
                    else:
                        self.assertNotRegex(text, regex)


class TestDisjoiners(RegexBuilderTester):
    def test_strictness_low(self):
        builder = regen.RegexBuilder(disjoiner_mode=regen.Strictness.LOW)
        tests = [
            (["A", "B"], [("AB", True), ("A^B", True)]),
            (["A", "^", "B"], [("AB", True), ("A^B", True), ("A^^B", False)]),
            (
                ["A", "B", "D"],
                [
                    ("ABD", True),
                    ("A^BD", True),
                    ("AB^D", True),
                    ("A^B^D", True),
                    ("A^B^D^", True),
                ],
            ),
            (
                ["A", "^", "B", "D"],
                [
                    ("ABD", True),
                    ("A^BD", True),
                    ("AB^D", True),
                    ("A^B^D", True),
                    ("A^B^D^", True),
                ],
            ),
            (
                ["A", "B", "^", "D"],
                [
                    ("ABD", True),
                    ("A^BD", True),
                    ("AB^D", True),
                    ("A^B^D", True),
                    ("A^B^D^", True),
                ],
            ),
            (
                ["A", "^", "B", "^", "D"],
                [
                    ("ABD", True),
                    ("A^BD", True),
                    ("AB^D", True),
                    ("A^B^D", True),
                    ("A^B^D^", True),
                ],
            ),
            (
                ["A", "^", "B", "^", "D", "^"],
                [
                    ("ABD", True),
                    ("A^BD", True),
                    ("AB^D", True),
                    ("A^B^D", True),
                    ("A^B^D^", True),
                ],
            ),
        ]
        self.run_tests(builder, tests)

    def test_strictness_medium(self):
        builder = regen.RegexBuilder(disjoiner_mode=regen.Strictness.MEDIUM)
        tests = [
            (["A", "B"], [("AB", True), ("A^B", True)]),
            (["A", "^", "B"], [("AB", False), ("A^B", True), ("A^^B", False)]),
            (
                ["A", "B", "D"],
                [
                    ("ABD", True),
                    ("A^BD", True),
                    ("AB^D", True),
                    ("A^B^D", True),
                    ("A^B^D^", True),
                ],
            ),
            (
                ["A", "^", "B", "D"],
                [
                    ("ABD", False),
                    ("A^BD", True),
                    ("AB^D", False),
                    ("A^B^D", True),
                    ("A^B^D^", True),
                ],
            ),
            (
                ["A", "B", "^", "D"],
                [
                    ("ABD", False),
                    ("A^BD", False),
                    ("AB^D", True),
                    ("A^B^D", True),
                    ("A^B^D^", True),
                ],
            ),
            (
                ["A", "^", "B", "^", "D"],
                [
                    ("ABD", False),
                    ("A^BD", False),
                    ("AB^D", False),
                    ("A^B^D", True),
                    ("A^B^D^", True),
                ],
            ),
            (
                ["A", "^", "B", "^", "D", "^"],
                [
                    ("ABD", False),
                    ("A^BD", False),
                    ("AB^D", False),
                    ("A^B^D", False),
                    ("A^B^D^", True),
                ],
            ),
        ]
        self.run_tests(builder, tests)

    def test_strictness_high(self):
        builder = regen.RegexBuilder(disjoiner_mode=regen.Strictness.HIGH)
        tests = [
            (["A", "B"], [("AB", True), ("A^B", False)]),
            (["A", "^", "B"], [("AB", False), ("A^B", True), ("A^^B", False)]),
            (
                ["A", "B", "D"],
                [("ABD", True), ("A^BD", False), ("AB^D", False), ("A^B^D", False)],
                ("A^B^D^", False),
            ),
            (
                ["A", "^", "B", "D"],
                [
                    ("ABD", False),
                    ("A^BD", True),
                    ("AB^D", False),
                    ("A^B^D", False),
                    ("A^B^D^", False),
                ],
            ),
            (
                ["A", "B", "^", "D"],
                [
                    ("ABD", False),
                    ("A^BD", False),
                    ("AB^D", True),
                    ("A^B^D", False),
                    ("A^B^D^", False),
                ],
            ),
            (
                ["A", "^", "B", "^", "D"],
                [
                    ("ABD", False),
                    ("A^BD", False),
                    ("AB^D", False),
                    ("A^B^D", True),
                    ("A^B^D^", False),
                ],
            ),
            (
                ["A", "^", "B", "^", "D", "^"],
                [
                    ("ABD", False),
                    ("A^BD", False),
                    ("AB^D", False),
                    ("A^B^D", False),
                    ("A^B^D^", True),
                ],
            ),
        ]
        self.run_tests(builder, tests)

    def test_prefixes_strictness_low(self):
        builder = regen.RegexBuilder(disjoiner_mode=regen.Strictness.LOW)
        tests = [
            (["U"], [("U^", True), ("U", True)]),
            (["U", "^"], [("U^", True), ("U", True), ("U^^", False)]),
        ]
        self.run_tests(builder, tests)

    def test_prefixes_strictness_medium(self):
        builder = regen.RegexBuilder(disjoiner_mode=regen.Strictness.MEDIUM)
        tests = [
            (["U"], [("U^", True), ("U", True)]),
            (["U", "^"], [("U^", True), ("U", False), ("U^^", False)]),
        ]
        self.run_tests(builder, tests)

    def test_prefixes_strictness_high(self):
        builder = regen.RegexBuilder(disjoiner_mode=regen.Strictness.HIGH)
        tests = [
            (["U"], [("U^", False), ("U", True)]),
            (["U", "^"], [("U^", True), ("U", False), ("U^^", False)]),
        ]
        self.run_tests(builder, tests)


class TestAspirates(RegexBuilderTester):
    def test_strictness_low(self):
        builder = regen.RegexBuilder(aspirate_mode=regen.Strictness.LOW)
        tests = [
            (["A"], [("A", True), ("'A", True)]),
            (["'", "A"], [("A", True), ("'A", True)]),
            (
                ["A", "D", "E"],
                [
                    ("ADE", True),
                    ("'ADE", True),
                    ("A'DE", True),
                    ("AD'E", True),
                    ("'A'DE", True),
                    ("'AD'E", True),
                    ("A'D'E", True),
                    ("'A'D'E", True),
                ],
            ),
            (
                ["'", "A", "D", "E"],
                [
                    ("ADE", True),
                    ("'ADE", True),
                    ("A'DE", True),
                    ("AD'E", True),
                    ("'A'DE", True),
                    ("'AD'E", True),
                    ("A'D'E", True),
                    ("'A'D'E", True),
                ],
            ),
            (
                ["'", "A", "'", "D", "E"],
                [
                    ("ADE", True),
                    ("'ADE", True),
                    ("A'DE", True),
                    ("AD'E", True),
                    ("'A'DE", True),
                    ("'AD'E", True),
                    ("A'D'E", True),
                    ("'A'D'E", True),
                ],
            ),
            (
                ["'", "A", "'", "D", "'", "E"],
                [
                    ("ADE", True),
                    ("'ADE", True),
                    ("A'DE", True),
                    ("AD'E", True),
                    ("'A'DE", True),
                    ("'AD'E", True),
                    ("A'D'E", True),
                    ("'A'D'E", True),
                ],
            ),
            (
                ["A", "'", "D", "'", "E"],
                [
                    ("ADE", True),
                    ("'ADE", True),
                    ("A'DE", True),
                    ("AD'E", True),
                    ("'A'DE", True),
                    ("'AD'E", True),
                    ("A'D'E", True),
                    ("'A'D'E", True),
                ],
            ),
            (
                ["'", "A", "D", "'", "E"],
                [
                    ("ADE", True),
                    ("'ADE", True),
                    ("A'DE", True),
                    ("AD'E", True),
                    ("'A'DE", True),
                    ("'AD'E", True),
                    ("A'D'E", True),
                    ("'A'D'E", True),
                ],
            ),
            (
                ["A", "'", "D", "E"],
                [
                    ("ADE", True),
                    ("'ADE", True),
                    ("A'DE", True),
                    ("AD'E", True),
                    ("'A'DE", True),
                    ("'AD'E", True),
                    ("A'D'E", True),
                    ("'A'D'E", True),
                ],
            ),
            (
                ["A", "D", "'", "E"],
                [
                    ("ADE", True),
                    ("'ADE", True),
                    ("A'DE", True),
                    ("AD'E", True),
                    ("'A'DE", True),
                    ("'AD'E", True),
                    ("A'D'E", True),
                    ("'A'D'E", True),
                    ("AD''E", False),
                ],
            ),
        ]
        self.run_tests(builder, tests)

    def test_strictness_medium(self):
        builder = regen.RegexBuilder(aspirate_mode=regen.Strictness.MEDIUM)
        tests = [
            (["A"], [("A", True), ("'A", True)]),
            (["'", "A"], [("A", False), ("'A", True)]),
            (
                ["A", "D", "E"],
                [
                    ("ADE", True),
                    ("'ADE", True),
                    ("A'DE", True),
                    ("AD'E", True),
                    ("'A'DE", True),
                    ("'AD'E", True),
                    ("A'D'E", True),
                    ("'A'D'E", True),
                ],
            ),
            (
                ["'", "A", "D", "E"],
                [
                    ("ADE", False),
                    ("'ADE", True),
                    ("A'DE", False),
                    ("AD'E", False),
                    ("'A'DE", True),
                    ("'AD'E", True),
                    ("A'D'E", False),
                    ("'A'D'E", True),
                ],
            ),
            (
                ["'", "A", "'", "D", "E"],
                [
                    ("ADE", False),
                    ("'ADE", False),
                    ("A'DE", False),
                    ("AD'E", False),
                    ("'A'DE", True),
                    ("'AD'E", False),
                    ("A'D'E", False),
                    ("'A'D'E", True),
                ],
            ),
            (
                ["'", "A", "'", "D", "'", "E"],
                [
                    ("ADE", False),
                    ("'ADE", False),
                    ("A'DE", False),
                    ("AD'E", False),
                    ("'A'DE", False),
                    ("'AD'E", False),
                    ("A'D'E", False),
                    ("'A'D'E", True),
                ],
            ),
            (
                ["A", "'", "D", "'", "E"],
                [
                    ("ADE", False),
                    ("'ADE", False),
                    ("A'DE", False),
                    ("AD'E", False),
                    ("'A'DE", False),
                    ("'AD'E", False),
                    ("A'D'E", True),
                    ("'A'D'E", True),
                ],
            ),
            (
                ["'", "A", "D", "'", "E"],
                [
                    ("ADE", False),
                    ("'ADE", False),
                    ("A'DE", False),
                    ("AD'E", False),
                    ("'A'DE", False),
                    ("'AD'E", True),
                    ("A'D'E", False),
                    ("'A'D'E", True),
                ],
            ),
            (
                ["A", "'", "D", "E"],
                [
                    ("ADE", False),
                    ("'ADE", False),
                    ("A'DE", True),
                    ("AD'E", False),
                    ("'A'DE", True),
                    ("'AD'E", False),
                    ("A'D'E", True),
                    ("'A'D'E", True),
                ],
            ),
            (
                ["A", "D", "'", "E"],
                [
                    ("ADE", False),
                    ("'ADE", False),
                    ("A'DE", False),
                    ("AD'E", True),
                    ("'A'DE", False),
                    ("'AD'E", True),
                    ("A'D'E", True),
                    ("'A'D'E", True),
                    ("AD''E", False),
                ],
            ),
        ]
        self.run_tests(builder, tests)

    def test_strictness_high(self):
        builder = regen.RegexBuilder(aspirate_mode=regen.Strictness.HIGH)
        tests = [
            (["A"], [("A", True), ("'A", False)]),
            (["'", "A"], [("A", False), ("'A", True)]),
            (
                ["A", "D", "E"],
                [
                    ("ADE", True),
                    ("'ADE", False),
                    ("A'DE", False),
                    ("AD'E", False),
                    ("'A'DE", False),
                    ("'AD'E", False),
                    ("A'D'E", False),
                    ("'A'D'E", False),
                ],
            ),
            (
                ["'", "A", "D", "E"],
                [
                    ("ADE", False),
                    ("'ADE", True),
                    ("A'DE", False),
                    ("AD'E", False),
                    ("'A'DE", False),
                    ("'AD'E", False),
                    ("A'D'E", False),
                    ("'A'D'E", False),
                ],
            ),
            (
                ["'", "A", "'", "D", "E"],
                [
                    ("ADE", False),
                    ("'ADE", False),
                    ("A'DE", False),
                    ("AD'E", False),
                    ("'A'DE", True),
                    ("'AD'E", False),
                    ("A'D'E", False),
                    ("'A'D'E", False),
                ],
            ),
            (
                ["'", "A", "'", "D", "'", "E"],
                [
                    ("ADE", False),
                    ("'ADE", False),
                    ("A'DE", False),
                    ("AD'E", False),
                    ("'A'DE", False),
                    ("'AD'E", False),
                    ("A'D'E", False),
                    ("'A'D'E", True),
                ],
            ),
            (
                ["A", "'", "D", "'", "E"],
                [
                    ("ADE", False),
                    ("'ADE", False),
                    ("A'DE", False),
                    ("AD'E", False),
                    ("'A'DE", False),
                    ("'AD'E", False),
                    ("A'D'E", True),
                    ("'A'D'E", False),
                ],
            ),
            (
                ["'", "A", "D", "'", "E"],
                [
                    ("ADE", False),
                    ("'ADE", False),
                    ("A'DE", False),
                    ("AD'E", False),
                    ("'A'DE", False),
                    ("'AD'E", True),
                    ("A'D'E", False),
                    ("'A'D'E", False),
                ],
            ),
            (
                ["A", "'", "D", "E"],
                [
                    ("ADE", False),
                    ("'ADE", False),
                    ("A'DE", True),
                    ("AD'E", False),
                    ("'A'DE", False),
                    ("'AD'E", False),
                    ("A'D'E", False),
                    ("'A'D'E", False),
                ],
            ),
            (
                ["A", "D", "'", "E"],
                [
                    ("ADE", False),
                    ("'ADE", False),
                    ("A'DE", False),
                    ("AD'E", True),
                    ("'A'DE", False),
                    ("'AD'E", False),
                    ("A'D'E", False),
                    ("'A'D'E", False),
                    ("AD''E", False),
                ],
            ),
        ]
        self.run_tests(builder, tests)

    def test_ing_strictness_low(self):
        builder = regen.RegexBuilder(aspirate_mode=regen.Strictness.LOW)
        tests = [
            (
                ["TH"],
                [
                    ("TH", True),
                    ("TH'", True),
                    ("TH''", True),
                    ("'TH'", True),
                    ("THE'", False),
                    ("TH'''", False),
                ],
            ),
            (
                ["TH", "'"],
                [
                    ("TH", True),
                    ("TH'", True),
                    ("TH''", True),
                    ("'TH'", True),
                    ("THE'", False),
                    ("TH'''", False),
                ],
            ),
            (
                ["TH", "'", "'"],
                [
                    ("TH", True),
                    ("TH'", True),
                    ("TH''", True),
                    ("'TH'", True),
                    ("THE'", False),
                    ("TH'''", False),
                ],
            ),
        ]
        self.run_tests(builder, tests)

    def test_ing_strictness_medium(self):
        builder = regen.RegexBuilder(aspirate_mode=regen.Strictness.MEDIUM)
        tests = [
            (
                ["TH"],
                [
                    ("TH", True),
                    ("TH'", True),
                    ("TH''", True),
                    ("'TH'", True),
                    ("THE'", False),
                    ("TH'''", False),
                ],
            ),
            (
                ["TH", "'"],
                [
                    ("TH", False),
                    ("TH'", True),
                    ("TH''", True),
                    ("'TH'", True),
                    ("THE'", False),
                    ("TH'''", False),
                ],
            ),
            (
                ["TH", "'", "'"],
                [
                    ("TH", False),
                    ("TH'", False),
                    ("TH''", True),
                    ("'TH'", False),
                    ("THE'", False),
                    ("TH'''", False),
                ],
            ),
        ]
        self.run_tests(builder, tests)

    def test_ing_strictness_high(self):
        builder = regen.RegexBuilder(aspirate_mode=regen.Strictness.HIGH)
        tests = [
            (
                ["TH"],
                [
                    ("TH", True),
                    ("TH'", False),
                    ("TH''", False),
                    ("'TH'", False),
                    ("THE'", False),
                    ("TH'''", False),
                ],
            ),
            (
                ["TH", "'"],
                [
                    ("TH", False),
                    ("TH'", True),
                    ("TH''", False),
                    ("'TH'", False),
                    ("THE'", False),
                    ("TH'''", False),
                ],
            ),
            (
                ["TH", "'", "'"],
                [
                    ("TH", False),
                    ("TH'", False),
                    ("TH''", True),
                    ("'TH'", False),
                    ("THE'", False),
                    ("TH'''", False),
                ],
            ),
        ]
        self.run_tests(builder, tests)

    def test_double_aspirate_strictness_low(self):
        builder = regen.RegexBuilder(aspirate_mode=regen.Strictness.LOW)
        tests = [
            (
                ["E", "D"],
                [("ED", True), ("'ED", True), ("''ED", True), ("'''ED", False)],
            ),
            (
                ["'", "E", "D"],
                [("ED", True), ("'ED", True), ("''ED", True), ("'''ED", False)],
            ),
            (
                ["'", "'", "E", "D"],
                [("ED", True), ("'ED", True), ("''ED", True), ("'''ED", False)],
            ),
        ]
        self.run_tests(builder, tests)

    def test_double_aspirate_strictness_medium(self):
        builder = regen.RegexBuilder(aspirate_mode=regen.Strictness.MEDIUM)
        tests = [
            (
                ["E", "D"],
                [("ED", True), ("'ED", True), ("''ED", True), ("'''ED", False)],
            ),
            (
                ["'", "E", "D"],
                [("ED", False), ("'ED", True), ("''ED", True), ("'''ED", False)],
            ),
            (
                ["'", "'", "E", "D"],
                [("ED", False), ("'ED", False), ("''ED", True), ("'''ED", False)],
            ),
        ]
        self.run_tests(builder, tests)

    def test_double_aspirate_strictness_high(self):
        builder = regen.RegexBuilder(aspirate_mode=regen.Strictness.HIGH)
        tests = [
            (
                ["E", "D"],
                [("ED", True), ("'ED", False), ("''ED", False), ("'''ED", False)],
            ),
            (
                ["'", "E", "D"],
                [("ED", False), ("'ED", True), ("''ED", False), ("'''ED", False)],
            ),
            (
                ["'", "'", "E", "D"],
                [("ED", False), ("'ED", False), ("''ED", True), ("'''ED", False)],
            ),
        ]
        self.run_tests(builder, tests)


class TestUncertaintyRegex(unittest.TestCase):
    def run_tests(self, uncertainty, tests):
        builder = regen.RegexBuilder()
        for test in tests:
            stroke = test[0]
            for text, expected in test[1]:
                regex = builder.make_uncertainty_regex(stroke, uncertainty)
                with self.subTest():
                    if expected:
                        self.assertTrue(re.fullmatch(regex, text))
                    else:
                        self.assertFalse(re.fullmatch(regex, text))

    # def test_uncertainty_zero(self):
    # # this should go under sim tests
    # for stroke in grammar.STROKES:
    # similars = similarities.get_similar(stroke, 0)
    # self.assertEqual(len(similars), 1)
    # self.assertIn(stroke, list(similars)[0])

    def test_uncertainty_zero(self):
        tests = [
            ("A", [("A", True), ("E", False), ("I", False)]),
            (
                "NT",
                [
                    ("NT", True),
                    ("ND", True),
                    ("TH", False),
                    ("MT", False),
                    ("MD", False),
                ],
            ),
            (
                "F",
                [
                    ("F", True),
                    ("V", False),
                    ("CH", False),
                    ("S", False),
                    ("Z", False),
                    ("SH", False),
                    ("P", False),
                    ("J", False),
                    ("X", False),
                    ("XS", False),
                    ("SS", False),
                    ("B", False),
                ],
            ),
        ]
        self.run_tests(0, tests)

    def test_uncertainty_one(self):
        tests = [
            ("A", [("A", True), ("E", True), ("I", True)]),
            (
                "NT",
                [("NT", True), ("ND", True), ("TH", True), ("MT", True), ("MD", True)],
            ),
            (
                "F",
                [
                    ("F", True),
                    ("V", True),
                    ("CH", True),
                    ("S", True),
                    ("Z", True),
                    ("SH", False),
                    ("P", False),
                    ("J", False),
                    ("X", False),
                    ("XS", False),
                    ("SS", False),
                    ("B", False),
                ],
            ),
        ]
        self.run_tests(1, tests)

    def test_uncertainty_two(self):
        tests = [
            ("A", [("A", True), ("E", True), ("I", True)]),
            (
                "NT",
                [("NT", True), ("ND", True), ("TH", True), ("MT", True), ("MD", True)],
            ),
            (
                "F",
                [
                    ("F", True),
                    ("V", True),
                    ("CH", True),
                    ("S", True),
                    ("Z", True),
                    ("SH", True),
                    ("P", True),
                    ("J", True),
                    ("X", True),
                    ("XS", True),
                    ("SS", True),
                    ("B", False),
                ],
            ),
        ]
        self.run_tests(2, tests)


class TestSearchMode(RegexBuilderTester):
    def test_match(self):
        builder = regen.RegexBuilder(search_mode=regen.SearchMode.MATCH)
        tests = [(["A", "B"], [("AB", True), ("ABU", False), ("DAB", False)])]
        self.run_tests(builder, tests)

    def test_start(self):
        builder = regen.RegexBuilder(search_mode=regen.SearchMode.START)
        tests = [(["A", "B"], [("AB", True), ("ABU", True), ("DAB", False)])]
        self.run_tests(builder, tests)

    def test_contain(self):
        builder = regen.RegexBuilder(search_mode=regen.SearchMode.CONTAIN)
        tests = [
            (["A", "B"], [("AB", True), ("ABU", True), ("DAB", True)]),
            (
                ["X"],
                [
                    ("ANEX Annex", True),
                    ("VEXN Vixen", True),
                    ("ZANTHUS Xanthous", False),
                    ("ZEBK Xebec", False),
                    ("ZEBK xebec", False),
                    ("ZEBK eXbec", False),
                    ("ZEBK ebec abXD", False),
                ],
            ),
        ]
        self.run_tests(builder, tests)


class TestFixFirst(RegexBuilderTester):
    def test_fix_first_off(self):
        builder = regen.RegexBuilder(fix_first=False, uncertainty=1)
        tests = [
            (
                ["A", "B", "D"],
                [
                    ("ABD", True),
                    ("EBD", True),
                    ("IBD", True),
                    ("APT", True),
                    ("EPDD", True),
                    ("IBDT", True),
                ],
            )
        ]
        self.run_tests(builder, tests)

    def test_fix_first_on(self):
        builder = regen.RegexBuilder(fix_first=True, uncertainty=1)
        tests = [
            (
                ["A", "B", "D"],
                [
                    ("ABD", True),
                    ("EBD", False),
                    ("IBD", False),
                    ("APT", True),
                    ("EPDD", False),
                    ("IBDT", False),
                ],
            )
        ]
        self.run_tests(builder, tests)


class TestStartingLetters(unittest.TestCase):
    def run_tests(self, builder, tests):
        for test in tests:
            interps = test[0]
            for stroke, expected in test[1]:
                letters = builder.get_starting_letters(interps)
                with self.subTest(interpretations=interps, stroke=stroke):
                    if expected:
                        self.assertIn(stroke, letters)
                    else:
                        self.assertNotIn(stroke, letters)

    def test_starting_letters_search_mode_contains(self):
        builder = regen.RegexBuilder(search_mode=regen.SearchMode.CONTAIN)
        tests = [[["A"]], [["B"]], [["K", "P"]], [["'", "I"]]]
        for test in tests:
            letters = builder.get_starting_letters(test)
            self.assertSetEqual(letters, grammar.HARD_CHARACTERS)

    def test_starting_letters_fix_first_uncertainty_one(self):
        builder = regen.RegexBuilder(
            search_mode=regen.SearchMode.MATCH, uncertainty=1, fix_first=True
        )
        tests = [
            ([["A"]], [("A", True), ("E", False), ("I", False)]),
            ([["'", "I"], [("I", True), ("E", False), ("A", False)]]),
            ([["NT"], ["DN"]], [("N", True), ("T", True), ("D", True), ("M", False)]),
        ]
        self.run_tests(builder, tests)

    def test_starting_letters_no_fix_first_uncertainty_one(self):
        builder = regen.RegexBuilder(
            search_mode=regen.SearchMode.MATCH, uncertainty=1, fix_first=False
        )
        tests = [
            ([["A"]], [("A", True), ("E", True), ("I", True)]),
            ([["'", "I"], [("I", True), ("E", False), ("A", True)]]),
            ([["NT"], ["DN"]], [("N", True), ("T", True), ("D", True), ("M", True)]),
        ]
        self.run_tests(builder, tests)


if __name__ == "__main__":
    unittest.main()
