import re
from enum import Enum

from similarities import get_alt_regex, get_similar

class SearchMode(Enum):
    MATCH = "match"
    START = "start"
    CONTAIN = "contain"

class RegexBuilder():

    hard_characters = {char for char in "ABCDEFGIJKLMNOPRSTUVZ"}
    annotations = {char for char in "'_,.()~|"}

    def __init__(self, uncertainty=0, search_mode=SearchMode.MATCH, fix_first=False):
        self.uncertainty = distance
        self.search_mode = search_mode
        self.fix_first = fix_first

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
                    builder.append(get_alt_regex(token, 0))
                else:
                    builder.append(get_alt_regex(token, self.uncertainty))

        if self.search_mode is SearchMode.CONTAIN:
            builder.append(".*")

        if self.search_mode is SearchMode.MATCH or \
                self.search_mode is SearchMode.CONTAIN:
            builder.append("\\s")

        return "".join(builder)

    def get_starting_letters(self, interpretations):

        if self.search_mode is SearchMode.CONTAIN:
            return hard_characters

        letters = set()
        for interp in interpretations:
            for token in interp:
                if token[0] in hard_characters:
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
            regex = self.build_regex(self, interp)
            patterns.append(re.compile(regex))
        return patterns




def makeRegex(interp, uncertainty, search_mode, fix_first):

    found_first = False

    def reducer(builder, token):
        nonlocal found_first
        if isinstance(token, set):
            if token and uncertainty == 0:
                builder.append("[")
                for char in token:
                    builder.append(char)
                builder.append("]*")
        else:
            if fix_first and not found_first:
                found_first = True
                builder.append(get_alt_regex(token, 0))
            else:
                builder.append(get_alt_regex(token, uncertainty))
        return builder

    base = list()
    if search_mode == "word" or search_mode == "start":
        base.append("^")

    if search_mode == "contains":
        base.append(".*")
    
    regex = reduce(reducer, interp, base)

    if search_mode == "contains":
        regex.append(".*")

    if search_mode == "word" or search_mode == "contains":
        regex.append("\\s")

    return "".join(regex)

def generate_patterns(interpretations, index = 1, uncertainty = 0, search_mode="word", fix_first=False):

    def get_starting_letters(interp):
        if search_mode == "contains":
            # include X?
            return set([char for char in "ABCDEFGIJKLMNOPRSTUVZ"])

        result = set()
        for token in interp:
            if not isinstance(token, set):
                if fix_first:
                    strokes = get_similar(token, 0)
                else:
                    strokes = get_similar(token, uncertainty)
                flattened_strokes = list()
                for tup in strokes:
                    flattened_strokes += [s for s in tup]
                result = set(string[0] for string in flattened_strokes)
                break
        return result

    patterns = list()
    starting_letters = set()
    if index > 0:
        interp = interpretations[index - 1]
        regex = makeRegex(interp, uncertainty, search_mode, fix_first)
        vprint(regex)
        patterns.append(re.compile(regex))
        starting_letters |= get_starting_letters(interp)
    else:
        for interp in interpretations:
            patterns.append(re.compile(makeRegex(interp, uncertainty, search_mode, fix_first)))
            starting_letters |= get_starting_letters(interp)
    return patterns, starting_letters

