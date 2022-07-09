from __future__ import annotations

import unittest

from grascii.metrics import gsequence_distance, interpretation_to_gsequence


class TestStandard(unittest.TestCase):
    def test_order(self):
        base = interpretation_to_gsequence(["A", "B"])
        aspirate = interpretation_to_gsequence(["'", "A", "B"])
        medium_sound = interpretation_to_gsequence(["A", ["."], "B"])
        long_sound = interpretation_to_gsequence(["A", [","], "B"])
        wunderbar = interpretation_to_gsequence(["A", ["_"], "B"])
        loop = interpretation_to_gsequence(["A", ["|"], "B"])
        reverse = interpretation_to_gsequence(["A", ["~"], "B"])
        disjoiner = interpretation_to_gsequence(["A", "^", "B"])
        uncertainty_one = interpretation_to_gsequence(["A", "P"])
        uncertainty_two = interpretation_to_gsequence(["A", "S"])
        insert_one = interpretation_to_gsequence(["A", "K", "B"])
        insert_two = interpretation_to_gsequence(["A", "K", "B", "D"])
        self.assertEqual(gsequence_distance(base, base), 0)
        self.assertGreater(gsequence_distance(aspirate, base), 0)
        self.assertEqual(
            gsequence_distance(medium_sound, base), gsequence_distance(long_sound, base)
        )
        self.assertGreaterEqual(
            gsequence_distance(medium_sound, base), gsequence_distance(aspirate, base)
        )
        self.assertGreaterEqual(
            gsequence_distance(wunderbar, base), gsequence_distance(medium_sound, base)
        )
        self.assertGreaterEqual(
            gsequence_distance(loop, base), gsequence_distance(wunderbar, base)
        )
        self.assertGreaterEqual(
            gsequence_distance(reverse, base), gsequence_distance(loop, base)
        )
        self.assertGreaterEqual(
            gsequence_distance(disjoiner, base), gsequence_distance(reverse, base)
        )
        self.assertGreaterEqual(
            gsequence_distance(uncertainty_one, base),
            gsequence_distance(disjoiner, base),
        )
        self.assertGreater(
            gsequence_distance(uncertainty_two, base),
            gsequence_distance(uncertainty_one, base),
        )
        self.assertGreaterEqual(
            gsequence_distance(insert_one, base), gsequence_distance(disjoiner, base)
        )
        self.assertGreater(
            gsequence_distance(insert_two, base), gsequence_distance(insert_one, base)
        )

    def test_uncertainty(self):
        base = interpretation_to_gsequence(["A", "S"])
        az = interpretation_to_gsequence(["A", "Z"])
        ap = interpretation_to_gsequence(["A", "P"])
        ab = interpretation_to_gsequence(["A", "B"])
        af = interpretation_to_gsequence(["A", "F"])
        av = interpretation_to_gsequence(["A", "V"])
        self.assertEqual(gsequence_distance(base, base), 0)
        self.assertEqual(gsequence_distance(az, base), 0)
        self.assertGreater(gsequence_distance(ap, base), 0)
        self.assertEqual(gsequence_distance(ap, base), gsequence_distance(af, base))
        self.assertEqual(gsequence_distance(ab, base), gsequence_distance(av, base))
        self.assertGreater(gsequence_distance(av, base), gsequence_distance(af, base))

    def test_equality(self):
        aspirate = interpretation_to_gsequence(["'", "A", "B"])
        medium_sound = interpretation_to_gsequence(["A", ["."], "B"])
        long_sound = interpretation_to_gsequence(["A", [","], "B"])
        wunderbar = interpretation_to_gsequence(["A", ["_"], "B"])
        loop = interpretation_to_gsequence(["A", ["|"], "B"])
        reverse = interpretation_to_gsequence(["A", ["~"], "B"])
        disjoiner = interpretation_to_gsequence(["A", "^", "B"])
        uncertainty_one = interpretation_to_gsequence(["A", "P"])
        uncertainty_two = interpretation_to_gsequence(["A", "S"])
        self.assertEqual(gsequence_distance(aspirate, aspirate), 0)
        self.assertEqual(gsequence_distance(medium_sound, medium_sound), 0)
        self.assertEqual(gsequence_distance(long_sound, long_sound), 0)
        self.assertEqual(gsequence_distance(wunderbar, wunderbar), 0)
        self.assertEqual(gsequence_distance(loop, loop), 0)
        self.assertEqual(gsequence_distance(reverse, reverse), 0)
        self.assertEqual(gsequence_distance(disjoiner, disjoiner), 0)
        self.assertEqual(gsequence_distance(uncertainty_one, uncertainty_one), 0)
        self.assertEqual(gsequence_distance(uncertainty_two, uncertainty_two), 0)

    def test_symmetry(self):
        aspirate = interpretation_to_gsequence(["'", "A", "B"])
        medium_sound = interpretation_to_gsequence(["A", ["."], "B"])
        long_sound = interpretation_to_gsequence(["A", [","], "B"])
        wunderbar = interpretation_to_gsequence(["A", ["_"], "B"])
        loop = interpretation_to_gsequence(["A", ["|"], "B"])
        reverse = interpretation_to_gsequence(["A", ["~"], "B"])
        disjoiner = interpretation_to_gsequence(["A", "^", "B"])
        uncertainty_one = interpretation_to_gsequence(["A", "P"])
        uncertainty_two = interpretation_to_gsequence(["A", "S"])
        self.assertEqual(
            gsequence_distance(aspirate, medium_sound),
            gsequence_distance(medium_sound, aspirate),
        )
        self.assertEqual(
            gsequence_distance(long_sound, medium_sound),
            gsequence_distance(medium_sound, long_sound),
        )
        self.assertEqual(
            gsequence_distance(long_sound, wunderbar),
            gsequence_distance(wunderbar, long_sound),
        )
        self.assertEqual(
            gsequence_distance(loop, wunderbar), gsequence_distance(wunderbar, loop)
        )
        self.assertEqual(
            gsequence_distance(loop, uncertainty_one),
            gsequence_distance(uncertainty_one, loop),
        )
        self.assertEqual(
            gsequence_distance(reverse, uncertainty_one),
            gsequence_distance(uncertainty_one, reverse),
        )
        self.assertEqual(
            gsequence_distance(reverse, uncertainty_two),
            gsequence_distance(uncertainty_two, reverse),
        )
        self.assertEqual(
            gsequence_distance(disjoiner, uncertainty_two),
            gsequence_distance(uncertainty_two, disjoiner),
        )

    def test_triangle_inequality(self):
        base = interpretation_to_gsequence(["A", "B"])
        aspirate = interpretation_to_gsequence(["'", "A", "B"])
        medium_sound = interpretation_to_gsequence(["A", ["."], "B"])
        long_sound = interpretation_to_gsequence(["A", [","], "B"])
        wunderbar = interpretation_to_gsequence(["A", ["_"], "B"])
        loop = interpretation_to_gsequence(["A", ["|"], "B"])
        reverse = interpretation_to_gsequence(["A", ["~"], "B"])
        disjoiner = interpretation_to_gsequence(["A", "^", "B"])
        uncertainty_one = interpretation_to_gsequence(["A", "P"])
        uncertainty_two = interpretation_to_gsequence(["A", "S"])
        self.assertGreaterEqual(
            gsequence_distance(base, wunderbar)
            + gsequence_distance(wunderbar, uncertainty_one),
            gsequence_distance(base, uncertainty_one),
        )
        self.assertGreaterEqual(
            gsequence_distance(medium_sound, disjoiner)
            + gsequence_distance(disjoiner, aspirate),
            gsequence_distance(medium_sound, aspirate),
        )
        self.assertGreaterEqual(
            gsequence_distance(loop, reverse) + gsequence_distance(reverse, long_sound),
            gsequence_distance(loop, long_sound),
        )
        self.assertGreaterEqual(
            gsequence_distance(disjoiner, base)
            + gsequence_distance(base, uncertainty_two),
            gsequence_distance(disjoiner, uncertainty_two),
        )

    def test_direction(self):
        base = interpretation_to_gsequence(["A", "S"])
        left = interpretation_to_gsequence(["A", "S", ["("]])
        right = interpretation_to_gsequence(["A", "S", [")"]])
        self.assertGreater(gsequence_distance(left, base), 0)
        self.assertGreater(gsequence_distance(right, base), 0)
        self.assertEqual(
            gsequence_distance(left, base), gsequence_distance(right, base)
        )
