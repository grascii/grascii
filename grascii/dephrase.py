from __future__ import annotations

import argparse
import sys
from functools import lru_cache
from typing import Set

from lark import Lark, Token, Transformer, UnexpectedInput
from lark.visitors import VisitError, v_args

from grascii.lark_ambig_tools import Disambiguator
from grascii.parser import GrasciiFlattener, interpretation_to_string
from grascii.searchers import GrasciiSearcher

description = "Decipher a shorthand phrase."


def build_argparser(argparser: argparse.ArgumentParser) -> None:
    argparser.add_argument("phrase", action="store", help="The phrase to decipher")
    argparser.add_argument(
        "-a",
        "--aggressive",
        action="store_true",
        default=False,
        help="perform a more intense dephrasing",
    )
    argparser.add_argument(
        "--ignore-limit",
        action="store_true",
        default=False,
        help="ignore the 8-character phrase limit",
    )


class NoWordFound(Exception):
    pass


class StripNameSpace(Transformer):
    def __init__(self, namespace):
        self.namespace = namespace + "__"

    def __default__(self, data, children, meta):
        if data.startswith(self.namespace):
            data = data[len(self.namespace) :]
        return super().__default__(data, children, meta)


class PhraseFlattener(Transformer):
    optionals = {
        "opt_to": "TO",
        "opt_in": "IN",
        "opt_of": "OF",
        "opt_your": "YOUR",
    }

    _grascii_flattener = GrasciiFlattener(start_rule="word")

    _grascii_searcher = GrasciiSearcher()

    def __init__(self):
        for key, value in self.optionals.items():
            setattr(self, key, self.make_opt(value))

    def make_opt(self, name):
        def opt(children):
            if len(children):
                return self.__default__(None, children, None)
            return [self.create_token("[" + name + "]")]

        return opt

    def start(self, children):
        result = []
        for child in children:
            for token in child:
                result.append(token)
        return result

    def create_token(self, name: str, value: str = ""):
        return Token(name, value)

    def short_to(self, children):
        return [self.create_token("TO")]

    @lru_cache(maxsize=32)
    def _search_grascii(self, grascii_str):
        results = self._grascii_searcher.sorted_search(grascii=grascii_str)
        if not results:
            raise NoWordFound()
        words = (result.entry.translation.upper() for result in results)
        string = "(" + "|".join(words) + ")"
        return self.create_token(string)

    @v_args(tree=True)
    def word(self, tree):
        interp = self._grascii_flattener.transform(tree)
        return self._search_grascii(interpretation_to_string(interp))

    def __default__(self, data, children, meta):
        result = []
        for child in children:
            if isinstance(child, Token):
                # strip namespace
                i = child.type.rfind("_")
                new_type = child.type[i + 1 :]
                result.append(self.create_token(new_type, child.value))
            else:
                for token in child:
                    result.append(token)
        return result


def dephrase(**kwargs) -> Set[str]:
    aggressive = kwargs.get("aggressive", False)
    grammar_name = "phrases_extended.lark" if aggressive else "phrases.lark"
    parser = Lark.open_from_package(
        "grascii.grammars",
        grammar_name,
        parser="earley",
        ambiguity="explicit",
        lexer="dynamic_complete",
    )
    trans = PhraseFlattener()
    if aggressive:
        trans = StripNameSpace("phrases") * trans
    parses: Set[str] = set()
    try:
        tree = parser.parse(kwargs["phrase"].upper())
    except UnexpectedInput:
        return parses

    trees = Disambiguator().visit(tree)
    for t in trees:
        try:
            tokens = (token.type for token in trans.transform(t))
        except VisitError as e:
            if isinstance(e.orig_exc, NoWordFound):
                continue
            raise e  # no cov
        else:
            parses.add(" ".join(tokens))
    return parses


def cli_dephrase(args: argparse.Namespace) -> None:
    if len(args.phrase) > 8 and args.aggressive and not args.ignore_limit:
        print(
            "Phrases more than 8 characters in length may take",
            "an excessively long time to process and produce many",
            "irrelevant results.",
        )
        print("To ignore this warning use '--ignore-limit'.")
        return
    results = dephrase(**{k: v for k, v in vars(args).items() if v is not None})
    if results:
        for result in results:
            print(result)
    else:
        print("No results")
        if not args.aggressive:
            print("You may try again with --aggressive to consider more possibilities.")


def main() -> None:
    argparser = argparse.ArgumentParser(description)
    build_argparser(argparser)
    args = argparser.parse_args(sys.argv[1:])
    cli_dephrase(args)


if __name__ == "__main__":
    main()
