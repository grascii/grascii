from __future__ import annotations

import unittest

import pexpect

SUPPORTS_INTERACTIVE = False
try:
    import grascii.interactive  # noqa: F401

    SUPPORTS_INTERACTIVE = True
except ImportError:
    pass

DOWN = "j"
UP = "k"


@unittest.skipUnless(SUPPORTS_INTERACTIVE, "interactive extra is not installed")
class InteractiveTester(unittest.TestCase):
    def setUp(self):
        self.c = pexpect.spawn("grascii search --interactive")

    def tearDown(self):
        self.c.close(force=True)

    def expect(self, patterns):
        return self.c.expect([pexpect.TIMEOUT] + patterns, timeout=3)

    def new_search(self):
        self.c.sendline()

    def navigate_to_settings(self):
        self.c.send(UP)
        self.c.send(UP)
        self.c.sendline()

    def assert_on_main_menu(self):
        self.assertGreater(self.expect(["What would you like to do?"]), 0)


class TestMenus(InteractiveTester):
    def test_main_menu(self):
        self.assertGreater(self.expect(["What would you like to do?"]), 0)
        self.assertGreater(self.expect(["New Search"]), 0)
        self.assertGreater(self.expect(["- Modify Search"]), 0)
        self.assertGreater(self.expect(["Edit Settings"]), 0)
        self.assertGreater(self.expect(["Exit"]), 0)

    def test_new_search(self):
        self.c.sendline()
        self.assertGreater(self.expect(["Enter Search:"]), 0)

    def test_settings(self):
        self.navigate_to_settings()
        self.assertGreater(self.expect(["Search Settings"]), 0)
        self.assertGreater(self.expect(["Uncertainty"]), 0)
        self.assertGreater(self.expect(["Search Mode"]), 0)
        self.assertGreater(self.expect(["Annotation Mode"]), 0)
        self.assertGreater(self.expect(["Aspirate Mode"]), 0)
        self.assertGreater(self.expect(["Disjoiner Mode"]), 0)
        self.assertGreater(self.expect(["Fix First"]), 0)
        self.assertGreater(self.expect(["Dictionaries"]), 0)
        self.assertGreater(self.expect(["Back"]), 0)

    def test_uncertainty(self):
        self.navigate_to_settings()
        self.c.sendline()
        self.assertGreater(self.expect(["Uncertainty"]), 0)
        self.assertGreater(self.expect(["0"]), 0)
        self.assertGreater(self.expect(["1"]), 0)
        self.assertGreater(self.expect(["2"]), 0)

    def test_search_mode(self):
        self.navigate_to_settings()
        self.c.send(DOWN)
        self.c.sendline()
        self.assertGreater(self.expect(["Search Mode"]), 0)
        self.assertGreater(self.expect(["match"]), 0)
        self.assertGreater(self.expect(["start"]), 0)
        self.assertGreater(self.expect(["contain"]), 0)

    def test_annotation_mode(self):
        self.navigate_to_settings()
        for i in range(2):
            self.c.send(DOWN)
        self.c.sendline()
        self.assertGreater(self.expect(["Annotation Mode"]), 0)
        self.assertGreater(self.expect(["discard"]), 0)
        self.assertGreater(self.expect(["retain"]), 0)
        self.assertGreater(self.expect(["strict"]), 0)

    def test_aspirate_mode(self):
        self.navigate_to_settings()
        for i in range(3):
            self.c.send(DOWN)
        self.c.sendline()
        self.assertGreater(self.expect(["Aspirate Mode"]), 0)
        self.assertGreater(self.expect(["discard"]), 0)
        self.assertGreater(self.expect(["retain"]), 0)
        self.assertGreater(self.expect(["strict"]), 0)

    def test_disjoiner_mode(self):
        self.navigate_to_settings()
        for i in range(4):
            self.c.send(DOWN)
        self.c.sendline()
        self.assertGreater(self.expect(["Disjoiner Mode"]), 0)
        self.assertGreater(self.expect(["discard"]), 0)
        self.assertGreater(self.expect(["retain"]), 0)
        self.assertGreater(self.expect(["strict"]), 0)

    def test_fix_first(self):
        self.navigate_to_settings()
        for i in range(5):
            self.c.send(DOWN)
        self.c.sendline()
        self.assertGreater(self.expect(["Fix First"]), 0)
        self.assertGreater(self.expect(["True"]), 0)
        self.assertGreater(self.expect(["False"]), 0)

    def test_dictionaries(self):
        self.navigate_to_settings()
        for i in range(6):
            self.c.send(DOWN)
        self.c.sendline()
        self.assertGreater(self.expect(["Choose Dictionaries"]), 0)
        self.assertGreater(self.expect([":preanniversary"]), 0)


class TestSearch(InteractiveTester):
    def test_no_search_input(self):
        self.new_search()
        for i in range(4):
            self.c.sendline()
            self.assertGreater(self.expect(["Enter Search:"]), 0)

    def test_search(self):
        self.new_search()
        self.c.sendline("a")
        self.assertGreater(self.expect(["Search Results"]), 0)
        self.assertGreater(self.expect(["Next"]), 0)
        self.assertGreater(self.expect(["Display All"]), 0)
        self.assertGreater(self.expect(["End Search"]), 0)
        i = 2
        while i == 2:
            self.c.sendline()
            i = self.expect(["Results: \\d+", "Next"])
        self.assertEqual(i, 1)
        self.assert_on_main_menu()

    def test_display_all(self):
        self.new_search()
        self.c.sendline("a")
        self.assertGreater(self.expect(["Search Results"]), 0)
        self.c.send(DOWN)
        self.c.sendline()
        self.assertGreater(self.expect(["Results: \\d+"]), 0)
        self.assert_on_main_menu()

    def test_end_search_immediately(self):
        self.new_search()
        self.c.sendline("a")
        self.assertGreater(self.expect(["Search Results"]), 0)
        self.c.send(DOWN)
        self.c.send(DOWN)
        self.c.sendline()
        self.assertGreater(self.expect(["Results: 0"]), 0)
        self.assert_on_main_menu()

    def test_end_search_later(self):
        self.new_search()
        self.c.sendline("a")
        self.assertGreater(self.expect(["Search Results"]), 0)
        self.c.sendline()
        self.assertGreater(self.expect(["Search Results"]), 0)
        self.c.sendline()
        self.assertGreater(self.expect(["Search Results"]), 0)
        self.c.send(DOWN)
        self.c.send(DOWN)
        self.c.sendline()
        self.assertGreater(self.expect(["Results: 2"]), 0)
        self.assert_on_main_menu()

    def test_interpretation(self):
        self.new_search()
        self.c.sendline("tn")
        self.assertGreater(self.expect(["all"]), 0)
        self.assertGreater(self.expect(["TN"]), 0)
        self.assertGreater(self.expect(["T-N"]), 0)
        self.c.sendline()
        self.assertGreater(self.expect(["Search Results"]), 0)
