
from functools import reduce
import re
import sys
import argparse
import os
from configparser import ConfigParser
import readline

from lark import Lark, Visitor, Transformer, Discard, Token, UnexpectedInput
from lark.visitors import CollapseAmbiguities

import questionary
from questionary.prompts.common import Choice

# import regen
# import grammar
# import defaults

from grascii import regen, grammar, defaults, interactive

vprint = lambda *a, **k: None

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
            choices=[mode.value for mode in regen.SearchMode],
            help="the kind of search to perform")
    argparser.add_argument("-a", "--annotation-mode",
            choices=[mode.value for mode in regen.Strictness],
            help="how to handle annotations in grascii")
    argparser.add_argument("-p", "--aspirate-mode",
            choices=[mode.value for mode in regen.Strictness],
            help="how to handle aspirates in grascii")
    argparser.add_argument("-j", "--disjoiner-mode",
            choices=[mode.value for mode in regen.Strictness],
            help="how to handle disjoiners in grascii")
    argparser.add_argument("-n", "--interpretation", 
            choices=["best", "all"],
            help="how to handle ambiguous grascii strings")
    argparser.add_argument("-f", "--fix-first", action="store_true",
            help="apply an uncertainty of 0 to the first token")
    argparser.add_argument("-v", "--verbose", action="store_true",
            help="turn on verbose output")

class GrasciiFlattener(Transformer):

    # def __init__(self):
        # self.circle_vowel = self.group_modifiers
        # self.hook_vowel = self.group_modifiers
        # self.diphthong = self.group_modifiers
        # self.directed_consonant = self.group_modifiers
        # self.sh = self.group_modifiers

    def start(self, children):
        result = list()
        for child in children:
            for token in child:
                if token in grammar.ANNOTATION_CHARACTERS:
                    if isinstance(result[-1], list):
                        result[-1].append(token)
                    else:
                        result.append([token])
                else:
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

def create_parser(ambiguity=True):
    if ambiguity:
        return Lark.open("../grammars/grascii.lark",
                  parser="earley",
                  ambiguity="explicit")
    return Lark.open("../grammars/grascii.lark",
              parser="earley",
              ambiguity="resolve")

def run_interactive(parser, args):
    previous_search = interactive_search(parser, args)

    # action = interactive.get_choice("", ["exit", 
        # "edit search",
        # "perform another search"])

    # if action == 1:
        # pass
    # elif action == 2:
        # interactive_search(parser, args)

def interactive_search(parser, args):
    search, tree = get_grascii_search(parser)
    parses = flatten_tree(tree)
    vprint(parses)
    display_interpretations = get_unique_interpretations(parses)
    interpretations = list(display_interpretations.values())
    index = choose_interpretation(interpretations)
    builder = regen.RegexBuilder(args.uncertainty, args.search_mode, args.fix_first, args.annotation_mode, args.aspirate_mode, args.disjoiner_mode)
    if index == 0:
        interps = interpretations
    else:
        interps = interpretations[index - 1: index]
    patterns = builder.generate_patterns(interps)
    starting_letters = builder.get_starting_letters(interps)
    results = perform_search(patterns, starting_letters, args.dict_path)
    count = 0
    display_all = False
    for result in results:
        count += 1
        print(result.strip())
        if not display_all:
            # action = input(result + "e(x)it, (d)isplay all, (e)nd search: ")
            action = questionary.select(" ",
                    ["next",
                     "display all",
                     "end search",
                     "exit"]
                    ).ask()
        if action == "end search":
            break
        elif action == "exit":
            exit()
        elif action == "display all":
            display_all = True
        
    print("Results:", count)
    return search
        
def get_grascii_search(parser):
    while True:
        # search = input("Enter search: ").upper()
        search = questionary.text("Enter Search:").ask().upper()
        if search == "":
            continue
        result = parse_grascii(parser, search)
        if not result:
            continue
        return search, result

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
        if isinstance(token, list):
            builder += token
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
        # print("0: all")
        choices = [Choice(title="all", value=0)]
        i = 1
        for interp in interpretations:
            choices.append(Choice(title=interpretationToString(interp), value=i))
            i += 1
        return questionary.select("Choose an interpretation to use in the search:", choices).ask()
        # return interactive.get_choice("Choose an interpretation to use in the search:", 
                # ["all"] + [interpretationToString(interp) for interp in interpretations])
        # for i, interp in enumerate(interpretations):
            # print(str(i + 1) + ":", interpretationToString(interp))

        # while True:
            # try:
              # index = int(input("Choose an interpretation to use in the search:"))
              # if index >= 0 and index <= len(interpretations):
                  # return index
            # except ValueError:
                # continue

def get_unique_interpretations(flattened_parses):
    return {interpretationToString(interp): interp for interp in flattened_parses}

def perform_search(patterns, starting_letters, dict_path):
    for item in sorted(starting_letters):
        try:
            with open(dict_path + item, "r") as dictionary:
                for line in dictionary:
                    for pattern in patterns:
                        if pattern.search(line):
                            yield line
                            break
        except FileNotFoundError:
            print("Error: Could not find", dict_path + item)

def process_args(args):
    conf = ConfigParser()
    conf.read("grascii.conf")
    uncertainty = conf.getint('Search', 'Uncertainty', 
            fallback=defaults.SEARCH["Uncertainty"])
    uncertainty = max(0, min(uncertainty, 2))
    search_mode = conf.get('Search', "SearchMode", 
            fallback=defaults.SEARCH["SearchMode"])
    annotation_mode = conf.get('Search', "AnnotationMode", 
            fallback=defaults.SEARCH["AnnotationMode"])
    aspirate_mode = conf.get('Search', "AspirateMode", 
            fallback=defaults.SEARCH["AspirateMode"])
    disjoiner_mode = conf.get('Search', "DisjoinerMode", 
            fallback=defaults.SEARCH["DisjoinerMode"])
    interpretation = conf.get('Search', "Interpretation",
            fallback=defaults.SEARCH["Interpretation"])

    if args.uncertainty is None:
        args.uncertainty = uncertainty
    if args.search_mode is None:
        args.search_mode = search_mode
    if args.annotation_mode is None:
        args.annotation_mode = annotation_mode
    if args.aspirate_mode is None:
        args.aspirate_mode = aspirate_mode
    if args.disjoiner_mode is None:
        args.disjoiner_mode = disjoiner_mode
    if args.interpretation is None:
        args.interpretation = interpretation

    args.search_mode = regen.SearchMode(args.search_mode)
    args.annotation_mode = regen.Strictness(args.annotation_mode)
    args.aspirate_mode = regen.Strictness(args.aspirate_mode)
    args.disjoiner_mode = regen.Strictness(args.disjoiner_mode)

    args.dict_path = conf.get("Search", "DictionaryPath", 
            fallback=defaults.SEARCH["DictionaryPath"])

def main(args):

    process_args(args)

    global vprint
    vprint = print if args.verbose else lambda *a, **k: None



    if args.interactive:
        vprint("Running in interactive mode")
        p = create_parser(ambiguity=True)
        run_interactive(p, args)
        exit(0)
    elif args.grascii is None:
        vprint("searching with custom regular expression:", args.regex.upper())
        patterns = [re.compile(args.regex.upper())]
        starting_letters = grammar.HARD_CHARACTERS
    else:
        p = create_parser(ambiguity=args.interpretation == "all")
        vprint("parsing grascii", args.grascii.upper())
        tree = parse_grascii(p, args.grascii.upper())
        if not tree:
            vprint("parsing failed")
            vprint("exiting")
            exit()

        parses = flatten_tree(tree)
        vprint(tree.pretty())
        vprint(parses)
        display_interpretations = get_unique_interpretations(parses)
        interpretations = list(display_interpretations.values())
        vprint(interpretations)

        if args.interpretation == "best":
            assert len(interpretations) == 1

        builder = regen.RegexBuilder(args.uncertainty, args.search_mode, args.fix_first, args.annotation_mode, args.aspirate_mode, args.disjoiner_mode)
        interps = interpretations[0:1] if args.interpretation == "best" else interpretations
        patterns = builder.generate_patterns(interps)
        starting_letters = builder.get_starting_letters(interps)

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
