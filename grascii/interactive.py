"""
Contains an implementation of an Interactive Searcher for an
interactive cli experience.
"""

from __future__ import annotations

try:
    import questionary
    from questionary.prompts.common import Choice
except ImportError:
    raise ImportError("Grascii: interactive extra dependencies are not installed")

import sys
from typing import Callable, Iterable, List, Optional, Sequence, Tuple, TypeVar

from grascii import metrics, regen
from grascii.dictionary import Dictionary
from grascii.dictionary.list import get_built_ins, get_installed
from grascii.parser import Interpretation, InvalidGrascii, interpretation_to_string
from grascii.searchers import GrasciiSearcher

T = TypeVar("T")


class InteractiveSearcher(GrasciiSearcher):
    """This subclass of GrasciiSearcher runs an interactive search
    experience for performing grascii searches with support for changing
    search parameters.
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.available_dicts = set(self.dictionaries)
        installed = map(lambda s: Dictionary.new(s), get_installed())
        built_ins = map(lambda s: Dictionary.new(s), get_built_ins())
        self.available_dicts.update(installed, built_ins)

    def search(self, **kwargs):
        """
        :param grascii: [Required] The grascii string to use in the search.
        :param uncertainty: The uncertainty of the grascii string.
        :param search_mode: The search mode to use.
        :param annotation_mode: How to handle annotations in the search.
        :param aspirate_mode: How to handle annotations in the search.
        :param disjoiner_mode: How to handle annotations in the search.
        :param fix_first: Apply an uncertainty of 0 to the first token.
        :type grascii: str
        :type uncertainty: int: 0, 1, or 2
        :type search_mode: str: one of regen.SearchMode values
        :type annotation_mode: one of regen.Strictness values
        :type aspirate_mode: one of regen.Strictness values
        :type disjoiner_mode: one of regen.Strictness values
        :type fix_first: bool
        :returns: None
        :rtype: None
        """

        self.extract_search_args(**kwargs)
        self.sort = not kwargs.get("no_sort")
        self._run_interactive()

    def _choose_interpretation(
        self, interpretations: Sequence[Interpretation]
    ) -> Optional[int]:
        """Prompt the user to choose an interpretation(s).

        :param interpretations: A collection of Interpretations to present
            to the user
        :returns: The index of the selected item in interpretations.
        """

        if len(interpretations) == 1:
            return 0
        prompt = "Choose an interpretation to use in the search:"
        choices = [Choice(title="all", value=0)]
        for i, interp in enumerate(interpretations):
            choices.append(Choice(title=interpretation_to_string(interp), value=i + 1))
        return questionary.select(prompt, choices).ask()

    def _run_interactive(self) -> None:
        """Run an interactive search loop."""

        previous_search = None
        while True:
            action = questionary.select(
                "What would you like to do?",
                [
                    "New Search",
                    Choice("Modify Search", disabled=not previous_search),
                    "Edit Settings",
                    "Exit",
                ],
            ).ask()

            if action is None or action == "Exit":
                exit()
            elif action == "New Search":
                previous_search = self._interactive_search()
            elif action == "Modify Search":
                previous_search = self._interactive_search(previous_search)
            elif action == "Edit Settings":
                while True:
                    action = questionary.select(
                        "Search Settings",
                        [
                            Choice(
                                title="Uncertainty [{}]".format(self.uncertainty),
                                value=1,
                            ),
                            Choice(
                                title="Search Mode [{}]".format(self.search_mode.value),
                                value=2,
                            ),
                            Choice(
                                title="Annotation Mode [{}]".format(
                                    self.annotation_mode.value
                                ),
                                value=3,
                            ),
                            Choice(
                                title="Aspirate Mode [{}]".format(
                                    self.aspirate_mode.value
                                ),
                                value=4,
                            ),
                            Choice(
                                title="Disjoiner Mode [{}]".format(
                                    self.disjoiner_mode.value
                                ),
                                value=5,
                            ),
                            Choice(
                                title="Fix First [{}]".format(self.fix_first), value=6
                            ),
                            Choice(
                                title="Dictionaries [{} selected]".format(
                                    len(self.dictionaries)
                                ),
                                value=7,
                            ),
                            "Back",
                        ],
                    ).ask()

                    if action is None or action == "Back":
                        break
                    elif action == 1:
                        self._change_arg(
                            "uncertainty", range(3), display_name="Uncertainty"
                        )
                    elif action == 2:
                        self._change_arg(
                            "search_mode",
                            list(regen.SearchMode),
                            convert=self._get_enum_value,
                            display_name="Search mode",
                        )
                    elif action == 3:
                        self._change_arg(
                            "annotation_mode",
                            list(regen.Strictness),
                            convert=self._get_enum_value,
                            display_name="Annotation mode",
                        )
                    elif action == 4:
                        self._change_arg(
                            "aspirate_mode",
                            list(regen.Strictness),
                            convert=self._get_enum_value,
                            display_name="Aspirate mode",
                        )
                    elif action == 5:
                        self._change_arg(
                            "disjoiner_mode",
                            list(regen.Strictness),
                            convert=self._get_enum_value,
                            display_name="Disjoiner mode",
                        )
                    elif action == 6:
                        self._change_arg(
                            "fix_first", [True, False], display_name="Fix First"
                        )
                    elif action == 7:
                        self._select_dictionaries()

    def _get_enum_value(self, enum):
        return enum.value

    def _change_arg(
        self,
        arg_name,
        options: Iterable[T],
        display_name: str = None,
        convert: Callable[[T], str] = str,
    ) -> None:
        """Prompt the user to select the value of a search parameter and set
            the new value.

        :param arg_name: The name of the argument to change.
        :param options: A collection of choices to present to the user.
        :param display_name: The title of the prompt.
        :param convert: A function that returns a string given an object of
            type T.
        """

        choices = []
        for option in options:
            selected = getattr(self, arg_name) == option
            choices.append(
                Choice(title=convert(option), value=option, checked=selected)
            )
        title = display_name if display_name else "Set " + arg_name
        setting = questionary.select(title, choices).ask()
        if setting is not None:
            setattr(self, arg_name, setting)

    def _select_dictionaries(self) -> None:
        choices = []
        for dictionary in self.available_dicts:
            selected = dictionary in self.dictionaries
            choices.append(
                Choice(title=dictionary.name, value=dictionary, checked=selected)
            )
        title = "Choose Dictionaries"
        dictionaries = questionary.checkbox(
            title,
            choices,
            validate=lambda d: True if len(d) > 0 else "Select at least one dictionary",
        ).ask()
        if dictionaries:
            self.dictionaries = dictionaries

    def _interactive_search(self, previous: str = None) -> Optional[str]:
        """Run an interactive search.

        :param previous: The previous search performed in this interactive
            session.
        :returns: The search string used.
        """

        search, interpretations = self._get_grascii_search(previous)
        if search is None:
            return previous
        index = self._choose_interpretation(interpretations)
        if index is None:
            return search
        builder = regen.RegexBuilder(
            uncertainty=self.uncertainty,
            search_mode=self.search_mode,
            fix_first=self.fix_first,
            annotation_mode=self.annotation_mode,
            aspirate_mode=self.aspirate_mode,
            disjoiner_mode=self.disjoiner_mode,
        )
        if index == 0:
            interps = interpretations
        else:
            interps = interpretations[index - 1 : index]
        patterns = builder.generate_patterns_map(interps)
        starting_letters = builder.get_starting_letters(interps)
        results = self.perform_search(patterns, starting_letters)
        if self.sort:
            results = sorted(results, key=lambda r: metrics.grascii_standard(r))
        count = 0
        display_all = False
        for result in results:
            action = "Next"
            if not display_all:
                action = questionary.select(
                    "Search Results", ["Next", "Display All", "End Search"]
                ).ask()
            if action is None or action == "End Search":
                break
            elif action == "Display All":
                display_all = True
            print(result.entry.grascii, result.entry.translation)
            count += 1

        print("Results:", count)
        print()
        return search

    def _get_grascii_search(
        self, previous: Optional[str] = None
    ) -> Tuple[Optional[str], Optional[List[Interpretation]]]:
        """Prompt the user for a grascii string.

        :param previous: The previous grascii string used in a search.
        :returns: A grascii string and associated interpretations
        """

        while True:
            if previous:
                search = questionary.text("Enter Search:", default=previous).ask()
            else:
                search = questionary.text("Enter Search:").ask()

            if search is None:
                return search, None
            if search == "":
                continue
            search = search.upper()
            try:
                interpretations = list(self._parser.interpret(search))
            except InvalidGrascii as e:
                print("Invalid Grascii String", file=sys.stderr)
                print(e.context, file=sys.stderr)
                previous = search
                continue
            return search, interpretations
