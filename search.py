
from functools import reduce
import re
import sys
import argparse
from configparser import ConfigParser

from lark import Lark, Visitor, Transformer, Discard, Token, UnexpectedInput
from lark.visitors import CollapseAmbiguities

from similarities import get_alt_regex, get_similar

description = "Search a Grascii Dictionary"

def build_argparser(argparser):
    group = argparser.add_mutually_exclusive_group(required=True)
    group.add_argument("-g", "--grascii", 
            help="the grascii string to search for")
    group.add_argument("-r", "--regex", 
            help="a custom regular expression to use in the search")
    group.add_argument("-i", "--interactive", action="store_true",
            help="run in interactive mode")
    argparser.add_argument("-u", "--uncertainty", type=int, choices=range(3),
            help="the uncertainty of the search term")
    argparser.add_argument("-s", "--search-mode",
            choices=["word", "start", "contains"], default="word",
            help="the kind of search to perform")
    argparser.add_argument("-f", "--fix-first", action="store_true",
            help="apply an uncertainty of 0 to the first token")
    argparser.add_argument("-v", "--verbose", action="store_true",
            help="turn on verbose output")

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

def run_interactive(parser, args, **kwargs):
    tree = get_grascii_search(parser)
    parses = flatten_tree(tree)
    display_interpretations = get_unique_interpretations(parses)
    interpretations = list(display_interpretations.values())
    index = choose_interpretation(interpretations)
    patterns, starting_letters = generate_patterns(interpretations, index, args.uncertainty, args.search_mode, args.fix_first)
    results = perform_search(patterns, starting_letters, args.dict_path)
    count = 0
    for result in results:
        input(result)
        count += 1
    print("Results:", count)

def get_grascii_search(parser):
    while True:
        search = input("Enter search: ").upper()
        if search == "":
            continue
        result = parse_grascii(parser, search)
        if not result:
            continue
        return result

def parse_grascii(parser, grascii):
    try:
        return parser.parse(grascii)
    except UnexpectedInput as e:
        print("Syntax Error")
        print(e.get_context(grascii))
        return False

def flatten_tree(parse_tree):
    trees = CollapseAmbiguities().transform(parse_tree)
    trans = GrasciiFlattener()
    return [trans.transform(tree) for tree in trees]

def interpretationToString(interp):
    def reducer(builder, token):
        if isinstance(token, set):
            for char in token:
                builder.append(char)
        else:
            if builder and builder[-1] != "^" and token != "^":
                builder.append("-")
            builder.append(token)
        return builder

    return "".join(reduce(reducer, interp, []))

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

def makeRegex(interp, distance, search_mode, fix_first):

    found_first = False

    def reducer(builder, token):
        nonlocal found_first
        if isinstance(token, set):
            if token and distance == 0:
                builder.append("[")
                for char in token:
                    builder.append(char)
                builder.append("]*")
        else:
            if fix_first and not found_first:
                found_first = True
                builder.append(get_alt_regex(token, 0))
            else:
                builder.append(get_alt_regex(token, distance))
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

def generate_patterns(interpretations, index = 1, distance = 0, search_mode="word", fix_first=False):

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
                    strokes = get_similar(token, distance)
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
        patterns.append(re.compile(makeRegex(interp, distance, search_mode, fix_first)))
        starting_letters |= get_starting_letters(interp)
    else:
        for interp in interpretations:
            patterns.append(re.compile(makeRegex(interp, distance, search_mode, fix_first)))
            starting_letters |= get_starting_letters(interp)
    return patterns, starting_letters

def perform_search(patterns, starting_letters, dict_path):
    for item in starting_letters:
        try:
            with open(dict_path + item, "r") as dictionary:
                for line in dictionary:
                    for pattern in patterns:
                        if pattern.search(line):
                            yield line
                            break
        except FileNotFoundError:
            print("Error: Could not find", dict_path + item)

def main(args):
    conf = ConfigParser()
    conf.read("grascii.conf")
    uncertainty = conf.getint('Search', 'Uncertainty', fallback=0)
    uncertainty = max(0, min(uncertainty, 2))

    if args.uncertainty is None:
        args.uncertainty = uncertainty

    args.dict_path = conf.get("Search", "DictionaryPath", fallback="./dict/")

    vprint = print if args.verbose else lambda *a, **k: None

    p = create_parser()
    if args.interactive:
        vprint("Running in interactive mode")
        run_interactive(p, args)
        exit(0)
    elif args.grascii is None:
        vprint("searching with custom regular expression:", args.regex.upper())
        patterns = [re.compile(args.regex.upper())]
        starting_letters = {"A"}
    else:
        vprint("parsing grascii", args.grascii.upper())
        tree = parse_grascii(p, args.grascii.upper())
        if not tree:
            vprint("parsing failed")
            vprint("exiting")
            exit()

        parses = flatten_tree(tree)
        display_interpretations = get_unique_interpretations(parses)
        interpretations = list(display_interpretations.values())

        index = 1 #choose_interpretation(interpretations)
        patterns, starting_letters = generate_patterns(interpretations, index, args.uncertainty, args.search_mode, args.fix_first)

    vprint(patterns)
         
    results = perform_search(patterns, starting_letters, args.dict_path)
    count = 0
    for result in results:
        print(result.strip())
        count += 1
    print("Results:", count)

if __name__ == "__main__":
    argparser = argparse.ArgumentParser(description)
    build_argparser(argparser)
    args = argparser.parse_args(sys.argv[1:])
    main(args)

