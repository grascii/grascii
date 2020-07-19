import re
from enum import Enum

import grammar
from similarities import get_similar

class SearchMode(Enum):
    MATCH = "match"
    START = "start"
    CONTAIN = "contain"

class RegexBuilder():

    modifiers = {
        "A" : "[.,~|_]*",
        "E" : "[.,~|_]*",
        "I" : "[~|_]*",
        "O" : "[.,_]*",
        "U" : "[.,_]*",
        "EU" : "_?",
        "AU" : "_?",
        "OE" : "_?",
        "A&'" : "_?",
        "A&E" : "_?",
        "S" : "[)(]?,?",
        "TH" : "[)(]?,?",
        "SH" : ",?"
        }

    def __init__(self, uncertainty=0, search_mode=SearchMode.MATCH, fix_first=False):
        self.uncertainty = uncertainty
        self.search_mode = search_mode
        self.fix_first = fix_first

    def make_uncertainty_regex(self, stroke, uncertainty):
        # if get_node(stroke) not in sg.nodes:
            # return re.escape(stroke)
        similars = get_similar(stroke, uncertainty)
        flattened = []
        for group in similars:
            for token in group:
                flattened.append(token)

        if uncertainty > 0:
            for i, symbol in enumerate(flattened):
                flattened[i] += self.modifiers.get(symbol, "")

        if len(flattened) > 1:
            return "(" + "|".join(flattened) + ")"
        return flattened[0]

    def build_regex(self, interpretation):

        builder = list()
        if self.search_mode is SearchMode.MATCH or \
                self.search_mode is SearchMode.START:
            builder.append("^")

        if self.search_mode is SearchMode.CONTAIN:
            builder.append(".*")

        found_first = False
        for token in interpretation:
            if isinstance(token, set):
                if token and self.uncertainty == 0:
                    builder.append("[")
                    for char in token:
                        builder.append(char)
                    builder.append("]*")
            else:
                if self.fix_first and not found_first:
                    found_first = True
                    builder.append(self.make_uncertainty_regex(token, 0))
                else:
                    builder.append(self.make_uncertainty_regex(token, self.uncertainty))

        if self.search_mode is SearchMode.CONTAIN:
            builder.append(".*")

        if self.search_mode is SearchMode.MATCH or \
                self.search_mode is SearchMode.CONTAIN:
            builder.append("\\s")

        return "".join(builder)

    def get_starting_letters(self, interpretations):

        if self.search_mode is SearchMode.CONTAIN:
            return grammar.HARD_CHARACTERS

        letters = set()
        for interp in interpretations:
            for token in interp:
                if token[0] in grammar.HARD_CHARACTERS:
                    if self.fix_first:
                        strokes = get_similar(token, 0)
                    else:
                        strokes = get_similar(token, self.uncertainty)
                    flattened_strokes = list()
                    for tup in strokes:
                        flattened_strokes += [s for s in tup]
                    letters |= set(string[0] for string in flattened_strokes)
                    break

        return letters

    def generate_patterns(self, interpretations):
        patterns = list()
        for interp in interpretations:
            regex = self.build_regex(interp)
            print(regex)
            patterns.append(re.compile(regex))
        return patterns


