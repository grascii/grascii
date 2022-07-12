from __future__ import annotations

import unittest

import pytest

try:
    import pexpect
except ImportError:
    pexpect = None

SUPPORTS_INTERACTIVE = False
try:
    import grascii.interactive  # noqa: F401

    SUPPORTS_INTERACTIVE = True
except ImportError:
    pass

DOWN = "j"
UP = "k"


@pytest.mark.slow
@unittest.skipIf(pexpect is None, "pexpect is not installed")
@unittest.skipUnless(SUPPORTS_INTERACTIVE, "interactive extra is not installed")
class InteractiveTester(unittest.TestCase):
    def setUp(self):
        self.c = pexpect.spawn(
            "grascii search --interactive --dictionary :preanniversary"
        )

    def tearDown(self):
        self.c.terminate(force=True)

    def expect(self, patterns):
        return self.c.expect([pexpect.TIMEOUT] + patterns, timeout=5)

    def new_search(self):
        self.c.sendline()

    def navigate_to_settings(self):
        self.c.send(UP)
        self.c.send(UP)
        self.c.sendline()

    def cancel(self):
        self.c.sendcontrol("c")

    def assert_on_main_menu(self):
        self.assertGreater(self.expect(["What would you like to do?"]), 0)

    def assert_on_settings(self):
        self.assertGreater(self.expect(["Search Settings"]), 0)

    def assert_modify_search_enabled(self):
        self.assertGreater(self.expect(["(?<!- )Modify Search"]), 0)

    def assert_modify_search_disabled(self):
        self.assertGreater(self.expect(["- Modify Search"]), 0)


class TestMenus(InteractiveTester):
    def test_main_menu(self):
        self.assertGreater(self.expect(["What would you like to do?"]), 0)
        self.assertGreater(self.expect(["New Search"]), 0)
        self.assertGreater(self.expect(["- Modify Search"]), 0)
        self.assertGreater(self.expect(["Edit Settings"]), 0)
        self.assertGreater(self.expect(["Exit"]), 0)

    def test_exit(self):
        self.c.sendline(UP)
        self.c.sendline()
        self.assertGreater(self.expect([pexpect.EOF]), 0)
        self.assertFalse(self.c.isalive())

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

    def test_settings_back(self):
        self.navigate_to_settings()
        self.assert_on_settings()
        self.c.send(UP)
        self.c.sendline()
        self.assert_on_main_menu()


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

    def test_modify_search(self):
        self.new_search()
        self.assertGreater(self.expect(["Enter Search:"]), 0)
        self.c.sendline("a")
        self.c.send(DOWN)
        self.c.sendline()
        self.assert_on_main_menu()
        self.assert_modify_search_enabled()
        self.c.send(DOWN)
        self.c.sendline()
        self.assertGreater(self.expect(["Enter Search:"]), 0)
        self.c.sendline("b")
        self.assertGreater(self.expect(["Search Results"]), 0)
        self.c.sendline()
        self.assertGreater(self.expect(["AB"]), 0)

    def test_invalid_grascii(self):
        self.new_search()
        self.assertGreater(self.expect(["Enter Search:"]), 0)
        self.c.sendline("rac")
        self.assertGreater(self.expect(["Invalid Grascii"]), 0)


class TestCancel(InteractiveTester):
    def test_main_menu(self):
        self.assert_on_main_menu()
        self.cancel()
        self.assertGreater(self.expect([pexpect.EOF]), 0)
        self.assertFalse(self.c.isalive())

    def test_new_search(self):
        self.new_search()
        self.assertGreater(self.expect(["Enter Search:"]), 0)
        self.cancel()
        self.assert_on_main_menu()
        self.assert_modify_search_disabled()

    def test_input_new_search(self):
        self.new_search()
        self.assertGreater(self.expect(["Enter Search:"]), 0)
        self.c.send("a")
        self.cancel()
        self.assert_on_main_menu()
        self.assert_modify_search_disabled()

    def test_search_results(self):
        self.new_search()
        self.assertGreater(self.expect(["Enter Search:"]), 0)
        self.c.send("a")
        self.c.sendline()
        self.cancel()
        self.assertGreater(self.expect(["Results: 0"]), 0)
        self.assert_on_main_menu()
        self.assert_modify_search_enabled()

    def test_search_results_later(self):
        self.new_search()
        self.assertGreater(self.expect(["Enter Search:"]), 0)
        self.c.send("a")
        self.c.sendline()
        self.c.sendline()
        self.cancel()
        self.assertGreater(self.expect(["Results: 1"]), 0)
        self.assert_on_main_menu()
        self.assert_modify_search_enabled()

    def test_interpretation(self):
        self.new_search()
        self.assertGreater(self.expect(["Enter Search:"]), 0)
        self.c.sendline("tn")
        self.cancel()
        self.assert_on_main_menu()
        self.assert_modify_search_enabled()

    def test_settings(self):
        self.navigate_to_settings()
        self.assert_on_settings()
        self.cancel()
        self.assert_on_main_menu()

    def test_uncertainty(self):
        self.navigate_to_settings()
        self.assert_on_settings()
        self.c.sendline()
        self.cancel()
        self.assert_on_settings()

    def test_search_mode(self):
        self.navigate_to_settings()
        self.assert_on_settings()
        self.c.send(DOWN)
        self.c.sendline()
        self.cancel()
        self.assert_on_settings()

    def test_annotation_mode(self):
        self.navigate_to_settings()
        self.assert_on_settings()
        for i in range(2):
            self.c.send(DOWN)
        self.c.sendline()
        self.cancel()
        self.assert_on_settings()

    def test_aspirate_mode(self):
        self.navigate_to_settings()
        self.assert_on_settings()
        for i in range(3):
            self.c.send(DOWN)
        self.c.sendline()
        self.cancel()
        self.assert_on_settings()

    def test_disjoiner_mode(self):
        self.navigate_to_settings()
        self.assert_on_settings()
        for i in range(4):
            self.c.send(DOWN)
        self.c.sendline()
        self.cancel()
        self.assert_on_settings()

    def test_fix_first(self):
        self.navigate_to_settings()
        self.assert_on_settings()
        for i in range(5):
            self.c.send(DOWN)
        self.c.sendline()
        self.cancel()
        self.assert_on_settings()

    def test_dictionaries(self):
        self.navigate_to_settings()
        self.assert_on_settings()
        for i in range(6):
            self.c.send(DOWN)
        self.c.sendline()
        self.cancel()
        self.assert_on_settings()
