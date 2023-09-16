from __future__ import annotations

import unittest

from grascii.outline import Outline
from grascii.parser import GrasciiParser, interpretation_to_string


class TestInferredDirections(unittest.TestCase):
    parser = GrasciiParser()

    def run_tests(self, tests):
        for test in tests:
            with self.subTest(word=test[0], expected=test[1]):
                interpretation = next(
                    self.parser.interpret(test[0], preserve_boundaries=True)
                )
                outline = Outline(interpretation)
                self.assertEqual(str(outline), test[1])

    def test_no_directed_consonants(self):
        tests = [
            ("DREM", "DREM"),
            ("JENERK", "JENERK"),
            ("GAT", "GAT"),
            ("LASH", "LASH"),
            ("TRELN", "TRELN"),
        ]
        self.run_tests(tests)

    def test_lone_s(self):
        tests = [("S", "S)"), ("S)", "S)"), ("S(", "S(")]
        self.run_tests(tests)

    def test_s_joined_to_curves(self):
        tests = [
            ("SPRA", "S(PRA"),
            ("REPS", "REPS("),
            ("PAS", "PAS("),
            ("SFER", "S)FER"),
            ("SAF", "S)AF"),
            ("FAS", "FAS)"),
            ("SKAT", "S)KAT"),
            ("SEK", "S)EK"),
            ("MAKS", "MAKS)"),
            ("KAS", "KAS)"),
            ("SLA", "S(LA"),
            ("SALS", "S(ALS("),
        ]
        self.run_tests(tests)

    def test_s_joined_to_forward_lines(self):
        tests = [
            ("STA", "S)TA"),
            ("SET", "S)ET"),
            ("NETS", "NETS("),
            ("SED", "S)ED"),
            ("ODS", "ODS("),
            ("DAS", "DAS("),
            ("SNO", "S)NO"),
            ("SEN", "S)EN"),
            ("SMAK", "S)MAK"),
            ("SAM", "S)AM"),
            ("LENS", "LENS("),
            ("NES", "NES("),
        ]
        self.run_tests(tests)

    def test_s_joined_to_downward_lines(self):
        tests = [("SASH", "S)ASH"), ("SAJ", "S)AJ"), ("CHES", "CHES)")]
        self.run_tests(tests)

    def test_s_o(self):
        tests = [
            ("SO", "S)O"),
            ("SORO", "S)ORO"),
            ("SOL", "S)OL"),
            ("SOFA", "S)OFA"),
            ("SOP", "S)OP"),
            ("SOD", "S)OD"),
        ]
        self.run_tests(tests)

    def test_s_u(self):
        tests = [
            ("US", "US)"),
            ("BUS", "BUS)"),
            ("FUS", "FUS)"),
            ("GUST", "GUS)T"),
            ("GRASHUS", "GRASHUS)"),
            ("VESHUS", "VESHUS)"),
        ]
        self.run_tests(tests)

    def test_sandwiched_s(self):
        tests = [
            ("UOSP", "UOS(P"),
            ("PAST", "PAS(T"),
            ("UESP", "UES(P"),
            ("UESTF", "UES)TF"),
            ("GOSEP", "GOS(EP"),
            ("TRESPAS", "TRES(PAS("),
            ("TRESL", "TRES(L"),
            ("VEST", "VES)T"),
            ("KASK", "KAS)K"),
            ("KASM", "KAS)M"),
            ("RESK", "RES(K"),
            ("ASAL", "AS(AL"),
            ("DOSEL", "DOS(EL"),
            ("FLASK", "FLAS(K"),
            ("KLASP", "KLAS(P"),
        ]
        self.run_tests(tests)

    def test_sandwiched_s2(self):
        tests = [
            ("VESTRE", "VES)TRE"),
            ("OFSET", "OFS)ET"),
            ("BOST", "BOS(T"),
            ("TAST", "TAS(T"),
            ("DESK", "DES(K"),
            ("MASK", "MAS(K"),
        ]
        self.run_tests(tests)

    def test_s_after_i(self):
        tests = [
            ("ISI", "IS(I"),
            ("I-SI", "I-S)I"),
            ("ISBERG", "IS(BERG"),
            ("ISKREM", "IS(KREM"),
            ("IS^K", "IS(^K"),
            ("ISOLA", "IS(OLA"),
            ("I-SOLASH", "I-S)OLASH"),
            ("NIS", "NIS("),
            ("VIS", "VIS)"),
            ("UIS", "UIS)"),
            ("U-IS", "U-IS("),
        ]
        self.run_tests(tests)

    def test_z(self):
        tests = [
            ("GAZ,", "GAZ),"),
            ("FAZ,", "FAZ),"),
            ("ZELUS", "Z(ELUS)"),
            ("ZERO", "Z(ERO"),
            ("MAZ", "MAZ("),
            ("RAZ", "RAZ("),
            ("DOZ", "DOZ("),
            ("LAZE", "LAZ(E"),
        ]
        self.run_tests(tests)

    def test_lone_th(self):
        tests = [("TH", "TH("), ("TH)", "TH)"), ("TH(", "TH(")]
        self.run_tests(tests)

    def test_th_joinings(self):
        tests = [
            ("THEK", "TH(EK"),
            ("THEM", "TH(EM"),
            ("DUTH", "DUTH("),
            ("THO", "TH)O"),
            ("THRO", "TH)RO"),
            ("ATHLET", "ATH)LET"),
            ("MOTH", "MOTH)"),
            ("ERTH", "ERTH)"),
            ("'ELTH", "'ELTH)"),
        ]
        self.run_tests(tests)

    def test_s_th_words(self):
        tests = [
            ("AS", "AS)"),
            ("SE", "S)E"),
            ("ESA", "ES)A"),
            ("'ETH", "'ETH("),
            ("'ATH", "'ATH("),
            ("THE", "TH(E"),
            ("THES", "TH(ES)"),
            ("SES", "S)ES)"),
            ("SETH", "S)ETH("),
        ]
        self.run_tests(tests)

    def test_lone_o(self):
        tests = [("O", "O"), ("O(", "O(")]
        self.run_tests(tests)

    def test_o_joinings(self):
        tests = [
            ("ON", "O(N"),
            ("OR", "O(R"),
            ("MON", "MO(N"),
            ("'OL", "'O(L"),
            ("DOM", "DO(M"),
            ("NOM", "NO(M"),
            ("MOD", "MOD"),
            ("SHOL", "SHOL"),
            ("FOM", "FOM"),
            ("BOCH", "BOCH"),
            ("ROG", "ROG"),
            ("PO,L", "PO,L"),
        ]
        self.run_tests(tests)

    def test_lone_u(self):
        tests = [
            ("U", "U"),
            ("U)", "U)"),
        ]
        self.run_tests(tests)

    def test_u_joinings(self):
        tests = [
            ("NUN", "NU)N"),
            ("MUD", "MU)D"),
            ("MUF", "MU)F"),
            ("MUN", "MU)N"),
            ("MUG", "MU)G"),
            ("MUD", "MU)D"),
            ("KUL", "KU)L"),
            ("GUL", "GU)L"),
            ("FUT", "FUT"),
            ("'UK", "'UK"),
            ("PUF", "PUF"),
            ("JUG", "JUG"),
            ("TUF", "TUF"),
            ("KUF", "KUF"),
            ("GUSH", "GUSH"),
        ]
        self.run_tests(tests)

    def test_s_boundaries(self):
        tests = [
            ("LSN", "LS(N"),
            ("L-SN", "L-S)N"),
            ("LOBSTE~", "LOBS(TE~"),
            ("LOB-STE~", "LOB-S)TE~"),
            ("LONSM", "LO(NS(M"),
            ("LON-SM", "LO(N-S)M"),
            ("LESR", "LES(R"),
            ("LESN", "LES(N"),
            ("LE-SN", "LE-S)N"),
            ("RSN", "RS(N"),
            ("R-SN", "R-S)N"),
            ("RSED", "RS(ED"),
            ("R-SED", "R-S)ED"),
            ("DSET", "DS(ET"),
            ("D-SET", "D-S)ET"),
            ("OS", "OS("),
            ("O-S", "O-S)"),
        ]
        self.run_tests(tests)

    def test_o_boundaries(self):
        tests = [
            ("NOR", "NO(R"),
            ("NO-R", "NO-R"),
            ("TOL", "TO(L"),
            ("TO-L", "TO-L"),
            ("CHOR", "CHOR"),
            ("CHO-R", "CHO-R"),
            ("CH-OR", "CH-O(R"),
            ("GON", "GO(N"),
            ("GO-N", "GO-N"),
            ("JON", "JON"),
            ("JO-N", "JO-N"),
            ("J-ON", "J-O(N"),
            ("DOM", "DO(M"),
            ("DO-M", "DO-M"),
        ]
        self.run_tests(tests)

    def test_u_boundaries(self):
        tests = [
            ("NUN", "NU)N"),
            ("N-UN", "N-UN"),
            ("MUT", "MU)T"),
            ("M-UT", "M-UT"),
            ("MNU", "MNU)"),
            ("MN-U", "MN-U"),
            ("KUT", "KUT"),
            ("KUR", "KU)R"),
            ("KU-R", "KU-R"),
            ("GUL", "GU)L"),
            ("G-UL", "G-UL"),
            ("GU-L", "GU-L"),
        ]
        self.run_tests(tests)

    def test_th_boundaries(self):
        tests = [
            ("THR", "TH)R"),
            ("TH-R", "TH(-R"),
            ("OTH", "OTH)"),
            ("O-TH", "O-TH("),
            ("THL", "TH)L"),
            ("TH-L", "TH(-L"),
            ("RTHO", "RTH)O"),
            ("R-THO", "R-TH)O"),
            ("RTH-O", "RTH)-O"),
            ("R-TH-O", "R-TH(-O"),
        ]
        self.run_tests(tests)

    def test_th_circle_vowel(self):
        tests = [
            ("THER", "TH)ER"),
            ("THE-R", "TH(E-R"),
            ("THIROE", "TH)IROE"),
            ("TH-IROE", "TH(-IROE"),
            ("LATH", "LATH)"),
            ("LA-TH", "LA-TH("),
            ("RATH", "RATH)"),
            ("R-ATH", "R-ATH("),
            ("THA&ER", "TH)A&ER"),
            ("LA&'TH", "LA&'TH)"),
        ]
        self.run_tests(tests)


class TestToInterpretation(unittest.TestCase):
    parser = GrasciiParser()

    def test_to_interpretation(self):
        tests = [
            ("JENERK", "J-E-N-E-R-K"),
            ("GAT", "G-A-T"),
            ("LASH", "L-A-SH"),
            ("MON", "M-O(-N"),
            ("'OL", "'-O(-L"),
            ("L-SN", "L-S)-N"),
            ("LOBSTE~", "L-O-B-S(-T-E~"),
            ("ESA", "E-S)-A"),
            ("'ETH", "'-E-TH("),
            ("TRESPAS", "T-R-E-S(-P-A-S("),
        ]
        for test in tests:
            with self.subTest(word=test[0], expected=test[1]):
                interpretation = next(
                    self.parser.interpret(test[0], preserve_boundaries=True)
                )
                outline = Outline(interpretation)
                self.assertEqual(
                    interpretation_to_string(outline.to_interpretation()), test[1]
                )
