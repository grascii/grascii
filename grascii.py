from functools import reduce
import re

from lark import Lark, Visitor, Transformer, Discard, Token, UnexpectedInput
from lark.visitors import CollapseAmbiguities

from graph_test import *

class GrasciiFlattener(Transformer):

    def __init__(self):
        self.circle_vowel = self.group_modifiers
        self.hook_vowel = self.group_modifiers
        self.diphthong = self.group_modifiers
        self.directed_consonant = self.group_modifiers
        self.sh = self.group_modifiers

    def start(self, children):
        result = list()
        for child in children:
            for token in child:
                result.append(token)
        return result

    def group_modifiers(self, children):
        return children[0], set(children[1:])

    def __default__(self, data, children, meta):
        result = list()
        for child in children:
            if isinstance(child, Token):
                result.append(child)
            else:
                for token in child:
                    result.append(token)
        return result


def create_parser():
    return Lark.open("grascii.lark",
              parser="earley",
              ambiguity="explicit")


def run_interactive(parser):
    tree = get_grascii_search(parser)
    parses = flatten_tree(tree)
    display_interpretations = get_unique_interpretations(parses)
    interpretations = list(display_interpretations.values())
    index = choose_interpretation(interpretations)
    patterns, starting_letters = generate_patterns(interpretations, index)
    results = perform_search(patterns, starting_letters, is_interactive=True)
    print("Results:", results)

def get_grascii_search(parser):
    while True:
        search = input("Enter search: ").upper()
        if search == "":
            continue
        try:
            return parser.parse(search)
        except UnexpectedInput as e:
            print("Syntax Error")
            print(e.get_context(search))

def flatten_tree(parse_tree):
    trees = CollapseAmbiguities().transform(parse_tree)
    trans = GrasciiFlattener()
    return [trans.transform(tree) for tree in trees]

def interpretationToString(interp):
    def reducer(string, token):
        if isinstance(token, set):
            for char in token:
                string += char
        else:
            if string and string[-1] != "^" and token != "^":
                string += "-"

            string += token 
        return string

    return reduce(reducer, interp, "")

def choose_interpretation(interpretations):
    if len(interpretations) == 1:
        print()
        print("Found 1 possible interpretation")
        print("Beginning search")
        return 0
    else:
        print("Interpretations: ", len(interpretations))
        print()
        print("0: all")
        for i, interp in enumerate(interpretations):
            print(str(i + 1) + ":", interpretationToString(interp))

        while True:
            try:
              index = int(input("Choose an interpretation to use in the search:"))
              if index >= 0 and index <= len(interpretations):
                  return index
            except ValueError:
                continue

def get_unique_interpretations(flattened_parses):
    return {interpretationToString(interp): interp for interp in flattened_parses}

def makeRegex(interp, distance):
    def reducer(builder, token):
        if isinstance(token, set):
            if token and distance == 0:
                builder.append("[")
                for char in token:
                    builder.append(char)
                builder.append("]*")
        else:
            builder.append(getAltsRegex(token, distance))
        return builder

    regex = reduce(reducer, interp, ["^"])
    regex.append("\\s")

    return "".join(regex)

def generate_patterns(interpretations, index = 1, distance = 0):
    patterns = list()
    starting_letters = set()
    if index > 0:
        patterns.append(re.compile(makeRegex(interpretations[index - 1], distance)))
        starting_letters.add(interpretationToString(interpretations[index - 1])[0])
    else:
        for interp in interpretations:
            patterns.append(re.compile(makeRegex(interp, distance)))
            starting_letters.add(interpretationToString(interp[0]))
    return patterns, starting_letters

def perform_search(patterns, starting_letters, dict_path="./dict/", is_interactive=False):
    results = 0
    for item in starting_letters:
        with open(dict_path + item, "r") as dictionary:
            for line in dictionary:
                for pattern in patterns:
                    if pattern.search(line):
                        results += 1
                        if is_interactive:
                            input(line)
                        else:
                            print(line.strip())
                        break
    return results

p = create_parser()
run_interactive(p)
