
import unittest

from grascii.parser import GrasciiParser
from grascii.outline import Outline

class TestInferredDirections(unittest.TestCase):

    parser = GrasciiParser()

    def run_tests(self, tests):
        for test in tests:
            with self.subTest(word=test[0], expected=test[1]):
                interpretation = self.parser.interpret(test[0])[0]
                outline = Outline(interpretation)
                self.assertEqual(str(outline), test[1])

    def test_no_directed_consonants(self):
        tests = [("DREM", "DREM"),
                ("JENERK", "JENERK"),
                ("GAT", "GAT"),
                ("LASH", "LASH"),
                ("TRELN", "TRELN")]
        self.run_tests(tests)

    def test_lone_s(self):
        tests = [("S", "S)"),
                ("S)", "S)"),
                ("S(", "S(")]
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
                ("SALS", "S(ALS(")
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
                ("NES", "NES(")
                ]
        self.run_tests(tests)

    def test_s_joined_to_downward_lines(self):
        tests = [
                ("SASH", "S)ASH"),
                ("SAJ", "S)AJ"),
                ("CHES", "CHES)")
                ]
        self.run_tests(tests)

    def test_s_o(self):
        tests = [
                ("SO", "S)O"),
                ("SORO", "S)ORO"),
                ("SOL", "S)OL"),
                ("SOFA", "S)OFA"),
                ("SOP", "S)OP"),
                ("SOD", "S)OD")
                ]
        self.run_tests(tests)

    def test_s_u(self):
        tests = [
                ("US", "US)"),
                ("BUS", "BUS)"),
                ("FUS", "FUS)"),
                ("GUST", "GUS)T"),
                ("GRASHUS", "GRASHUS)"),
                ("VESHUS", "VESHUS)")
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
                ("KLASP", "KLAS(P")
                ]
        self.run_tests(tests)

    def test_sandwiched_s2(self):
        tests = [
                ("VESTRE", "VES)TRE"),
                ("OFSET", "OFS)ET"),
                ("BOST", "BOS(T"),
                ("TAST", "TAS(T"),
                ("DESK", "DES(K"),
                ("MASK", "MAS(K")
                ]
        self.run_tests(tests)

    def test_z(self):
        tests = [
                ("GAZ,", "GAZ),"),
                ("FAZ,", "FAZ),"),
                ("ZELUS", "Z(ELUS"),
                ("ZERO", "Z(ERO"),
                ("MAZ", "MAZ("),
                ("RAZ", "RAZ("),
                ("DOZ", "DOZ("),
                ("LAZE", "LAZ(E")
                ]

    def test_lone_th(self):
        tests = [("TH", "TH("),
                ("TH)", "TH)"),
                ("TH(", "TH(")]
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
                ("'ELTH", "'ELTH)")
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
                ("SETH", "S)ETH(")
                ]
        self.run_tests(tests)

    def test_lone_o(self):
        tests = [
                ("O", "O"),
                ("O(", "O(")
                ]
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
                ("PO,L", "PO,L")
                ]
        self.run_tests(tests)
