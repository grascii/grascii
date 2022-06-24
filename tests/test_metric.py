import unittest

from grascii.metrics import convert_interpretation, match_distance


class TestStandard(unittest.TestCase):
    def test_order(self):
        base = convert_interpretation(["A", "B"])
        aspirate = convert_interpretation(["'", "A", "B"])
        medium_sound = convert_interpretation(["A", ["."], "B"])
        long_sound = convert_interpretation(["A", [","], "B"])
        wunderbar = convert_interpretation(["A", ["_"], "B"])
        loop = convert_interpretation(["A", ["|"], "B"])
        reverse = convert_interpretation(["A", ["~"], "B"])
        disjoiner = convert_interpretation(["A", "^", "B"])
        uncertainty_one = convert_interpretation(["A", "P"])
        uncertainty_two = convert_interpretation(["A", "S"])
        insert_one = convert_interpretation(["A", "K", "B"])
        insert_two = convert_interpretation(["A", "K", "B", "D"])
        self.assertEqual(match_distance(base, base), 0)
        self.assertGreater(match_distance(aspirate, base), 0)
        self.assertEqual(
            match_distance(medium_sound, base), match_distance(long_sound, base)
        )
        self.assertGreaterEqual(
            match_distance(medium_sound, base), match_distance(aspirate, base)
        )
        self.assertGreaterEqual(
            match_distance(wunderbar, base), match_distance(medium_sound, base)
        )
        self.assertGreaterEqual(
            match_distance(loop, base), match_distance(wunderbar, base)
        )
        self.assertGreaterEqual(
            match_distance(reverse, base), match_distance(loop, base)
        )
        self.assertGreaterEqual(
            match_distance(disjoiner, base), match_distance(reverse, base)
        )
        self.assertGreaterEqual(
            match_distance(uncertainty_one, base), match_distance(disjoiner, base)
        )
        self.assertGreater(
            match_distance(uncertainty_two, base), match_distance(uncertainty_one, base)
        )
        self.assertGreaterEqual(
            match_distance(insert_one, base), match_distance(disjoiner, base)
        )
        self.assertGreater(
            match_distance(insert_two, base), match_distance(insert_one, base)
        )

    def test_uncertainty(self):
        base = convert_interpretation(["A", "S"])
        az = convert_interpretation(["A", "Z"])
        ap = convert_interpretation(["A", "P"])
        ab = convert_interpretation(["A", "B"])
        af = convert_interpretation(["A", "F"])
        av = convert_interpretation(["A", "V"])
        self.assertEqual(match_distance(base, base), 0)
        self.assertEqual(match_distance(az, base), 0)
        self.assertGreater(match_distance(ap, base), 0)
        self.assertEqual(match_distance(ap, base), match_distance(af, base))
        self.assertEqual(match_distance(ab, base), match_distance(av, base))
        self.assertGreater(match_distance(av, base), match_distance(af, base))

    def test_equality(self):
        aspirate = convert_interpretation(["'", "A", "B"])
        medium_sound = convert_interpretation(["A", ["."], "B"])
        long_sound = convert_interpretation(["A", [","], "B"])
        wunderbar = convert_interpretation(["A", ["_"], "B"])
        loop = convert_interpretation(["A", ["|"], "B"])
        reverse = convert_interpretation(["A", ["~"], "B"])
        disjoiner = convert_interpretation(["A", "^", "B"])
        uncertainty_one = convert_interpretation(["A", "P"])
        uncertainty_two = convert_interpretation(["A", "S"])
        self.assertEqual(match_distance(aspirate, aspirate), 0)
        self.assertEqual(match_distance(medium_sound, medium_sound), 0)
        self.assertEqual(match_distance(long_sound, long_sound), 0)
        self.assertEqual(match_distance(wunderbar, wunderbar), 0)
        self.assertEqual(match_distance(loop, loop), 0)
        self.assertEqual(match_distance(reverse, reverse), 0)
        self.assertEqual(match_distance(disjoiner, disjoiner), 0)
        self.assertEqual(match_distance(uncertainty_one, uncertainty_one), 0)
        self.assertEqual(match_distance(uncertainty_two, uncertainty_two), 0)

    def test_symmetry(self):
        aspirate = convert_interpretation(["'", "A", "B"])
        medium_sound = convert_interpretation(["A", ["."], "B"])
        long_sound = convert_interpretation(["A", [","], "B"])
        wunderbar = convert_interpretation(["A", ["_"], "B"])
        loop = convert_interpretation(["A", ["|"], "B"])
        reverse = convert_interpretation(["A", ["~"], "B"])
        disjoiner = convert_interpretation(["A", "^", "B"])
        uncertainty_one = convert_interpretation(["A", "P"])
        uncertainty_two = convert_interpretation(["A", "S"])
        self.assertEqual(
            match_distance(aspirate, medium_sound),
            match_distance(medium_sound, aspirate),
        )
        self.assertEqual(
            match_distance(long_sound, medium_sound),
            match_distance(medium_sound, long_sound),
        )
        self.assertEqual(
            match_distance(long_sound, wunderbar), match_distance(wunderbar, long_sound)
        )
        self.assertEqual(
            match_distance(loop, wunderbar), match_distance(wunderbar, loop)
        )
        self.assertEqual(
            match_distance(loop, uncertainty_one), match_distance(uncertainty_one, loop)
        )
        self.assertEqual(
            match_distance(reverse, uncertainty_one),
            match_distance(uncertainty_one, reverse),
        )
        self.assertEqual(
            match_distance(reverse, uncertainty_two),
            match_distance(uncertainty_two, reverse),
        )
        self.assertEqual(
            match_distance(disjoiner, uncertainty_two),
            match_distance(uncertainty_two, disjoiner),
        )

    def test_triangle_inequality(self):
        base = convert_interpretation(["A", "B"])
        aspirate = convert_interpretation(["'", "A", "B"])
        medium_sound = convert_interpretation(["A", ["."], "B"])
        long_sound = convert_interpretation(["A", [","], "B"])
        wunderbar = convert_interpretation(["A", ["_"], "B"])
        loop = convert_interpretation(["A", ["|"], "B"])
        reverse = convert_interpretation(["A", ["~"], "B"])
        disjoiner = convert_interpretation(["A", "^", "B"])
        uncertainty_one = convert_interpretation(["A", "P"])
        uncertainty_two = convert_interpretation(["A", "S"])
        self.assertGreaterEqual(
            match_distance(base, wunderbar)
            + match_distance(wunderbar, uncertainty_one),
            match_distance(base, uncertainty_one),
        )
        self.assertGreaterEqual(
            match_distance(medium_sound, disjoiner)
            + match_distance(disjoiner, aspirate),
            match_distance(medium_sound, aspirate),
        )
        self.assertGreaterEqual(
            match_distance(loop, reverse) + match_distance(reverse, long_sound),
            match_distance(loop, long_sound),
        )
        self.assertGreaterEqual(
            match_distance(disjoiner, base) + match_distance(base, uncertainty_two),
            match_distance(disjoiner, uncertainty_two),
        )

    def test_direction(self):
        base = convert_interpretation(["A", "S"])
        left = convert_interpretation(["A", "S", ["("]])
        right = convert_interpretation(["A", "S", [")"]])
        self.assertGreater(match_distance(left, base), 0)
        self.assertGreater(match_distance(right, base), 0)
        self.assertEqual(match_distance(left, base), match_distance(right, base))
