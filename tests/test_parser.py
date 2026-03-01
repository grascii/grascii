from __future__ import annotations

import pytest

from grascii.parser import GrasciiParser


class TestGrasciiParser:
    @pytest.fixture(scope="class")
    def parser(self):
        return GrasciiParser()

    @pytest.mark.parametrize(
        "grascii,expected",
        [
            ("NTN", [["N", "TN"], ["NT", "N"], ["N", "T", "N"]]),
            ("MTN", [["M", "TN"], ["MT", "N"], ["M", "T", "N"]]),
            ("NTM", [["N", "TM"], ["NT", "M"], ["N", "T", "M"]]),
            ("MTM", [["M", "TM"], ["MT", "M"], ["M", "T", "M"]]),
            ("NDN", [["N", "DN"], ["ND", "N"], ["N", "D", "N"]]),
            ("MDN", [["M", "DN"], ["MD", "N"], ["M", "D", "N"]]),
            ("NDM", [["N", "DM"], ["ND", "M"], ["N", "D", "M"]]),
            ("MDM", [["M", "DM"], ["MD", "M"], ["M", "D", "M"]]),
        ],
    )
    def test_intepretations(self, parser, grascii, expected):
        intepretations = list(parser.interpret(grascii))
        assert intepretations == expected
