from __future__ import annotations

import pytest

from grascii.interpreter import GrasciiInterpreter
from grascii.parser import GrasciiParser, InvalidGrascii


class TestGrasciiInterpreter:
    @pytest.fixture(scope="class", autouse=True)
    def interpreter(self):
        return GrasciiInterpreter()

    @pytest.fixture(scope="class")
    def parser(self):
        return GrasciiParser()

    @pytest.mark.parametrize(
        "grascii,expected,preserve_boundaries",
        [
            ("DTN", ["DT", "N"], False),
            ("NDM", ["N", "DM"], False),
            ("ND-M", ["ND", "M"], False),
            ("TMD", ["TM", "D"], False),
            ("SSH", ["S", "SH"], False),
            ("DTH", ["D", "TH"], False),
            ("DDV", ["DD", "V"], False),
            ("S)S", ["S", [")"], "S"], False),
            ("JNTM", ["JNT", "M"], False),
            ("TNK", ["TN", "K"], False),
            ("NDV", ["ND", "V"], False),
            ("OEU", ["OE", "U"], False),
            ("O,EU", ["O", [","], "EU"], False),
            ("MND", ["MN", "D"], False),
            ("M-ND", ["M", "ND"], False),
            ("M-ND", ["M", "-", "ND"], True),
            ("CCH", None, False),
            ("A~|", ["A", ["~", "|"]], False),
            ("A~|E", ["A", ["~", "|"], "E"], False),
            ("A~|E.", ["A", ["~", "|"], "E", ["."]], False),
            ("K^D", ["K", "^", "D"], True),
            ("SS", ["SS"], False),
            ("SS)", ["SS", [")"]], False),
            ("SS,", ["S", "S", [","]], False),
            ("SS),", ["S", "S", [")", ","]], False),
            ("AU)", ["A", "U", [")"]], False),
            ("OE~", ["O", "E", ["~"]], False),
            ("NDT", ["ND", "T"], False),
            ("MMN", ["MM", "N"], False),
            ("LDN", ["LD", "N"], False),
            ("TMN", ["TM", "N"], False),
            ("DDN", ["DD", "N"], False),
            ("NDV", ["ND", "V"], False),
            ("NTDN", ["NT", "DN"], False),
        ],
    )
    def test_interpreter(
        self, interpreter, parser, grascii, expected, preserve_boundaries
    ):
        interpreter_result = interpreter.interpret(grascii, preserve_boundaries)
        assert interpreter_result == expected

        try:
            parser_result = next(parser.interpret(grascii, preserve_boundaries))
        except InvalidGrascii:
            parser_result = None
        assert parser_result == expected

    # def test_dictionary(self, interpreter, parser):
    #     from grascii.dictionary.build import DictionaryBuilder
    #     from pathlib import Path
    #
    #     def inter(grascii, transalation, _):
    #         interpreter_result = interpreter.interpret(grascii, True)
    #
    #         try:
    #             parser_result = next(parser.interpret(grascii, True))
    #         except InvalidGrascii:
    #             parser_result = None
    #
    #         if interpreter_result != parser_result:
    #             failures.append([interpreter_result, parser_result])
    #
    #         return grascii, transalation
    #
    #     failures = []
    #
    #     builder = DictionaryBuilder()
    #     builder = DictionaryBuilder(
    #         pipeline=[inter]
    #     )
    #     inputs = Path("dictionaries/builtins/preanniversary-phrases/").glob("*.txt")
    #     builder.build(inputs, None)
    #
    #     print(failures)
    #     assert not failures
