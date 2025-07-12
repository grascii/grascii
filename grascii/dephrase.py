from __future__ import annotations

import argparse
import sys
from functools import lru_cache
from typing import Iterable, Set

from lark import Lark, Token, Transformer, UnexpectedInput
from lark.visitors import VisitError, v_args

from grascii.interpreter import interpretation_to_string
from grascii.lark_ambig_tools import Disambiguator
from grascii.parser import GrasciiFlattener
from grascii.searchers import GrasciiSearcher

description = "Decipher shorthand phrases"


def build_argparser(argparser: argparse.ArgumentParser) -> None:
    """Configure an ArgumentParser parser to parse the dephrase command-line
    options.

    :param argparser: A fresh ArgumentParser to configure.
    """
    argparser.add_argument(
        "phrase", action="store", help="A Grascii phrase to decipher"
    )
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
    """Exception thrown by PhraseFlattener when a Grascii search produces no results"""

    pass


class StripNameSpace(Transformer):
    """A Lark transformer that removes a namespace prefix from rules"""

    def __init__(self, namespace):
        self.namespace = namespace + "__"

    def __default__(self, data, children, meta):
        if data.startswith(self.namespace):
            data = data[len(self.namespace) :]
        return super().__default__(data, children, meta)


class PhraseFlattener(Transformer):
    """A Lark transformer that converts a tree from a phrase grammar into a
    possible translation of the phrase."""

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

    def DONT(self, token):
        return self.create_token("DON'T", token.value)

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


def dephrase(**kwargs) -> Iterable[str]:
    """Decipher a shorthand phrase.

    :param phrase: A Grascii string to dephrase. (Required)
    :param aggressive: A flag enabling a more intense dephrasing strategy.
    :type phrase: str
    :type aggressive: bool

    :returns: A generator of possible dephrasings
    """
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
    try:
        tree = parser.parse(kwargs["phrase"].upper())
    except UnexpectedInput:
        return

    parses: Set[str] = set()
    trees = Disambiguator().visit(tree)
    for t in trees:
        try:
            tokens = (token.type for token in trans.transform(t))
        except VisitError as e:
            if isinstance(e.orig_exc, NoWordFound):
                continue
            raise e  # no cov
        else:
            parse = " ".join(tokens)
            if parse not in parses:
                yield parse
            parses.add(parse)


def cli_dephrase(args: argparse.Namespace) -> None:
    """Run dephrase using arguments parsed from the command line.

    :param args: A namespace of parsed arguments.
    """
    if len(args.phrase) > 8 and args.aggressive and not args.ignore_limit:
        print(
            "Phrases more than 8 characters in length may take",
            "an excessively long time to process and produce many",
            "irrelevant results.",
        )
        print("To ignore this warning use '--ignore-limit'.")
        return

    results = dephrase(**{k: v for k, v in vars(args).items() if v is not None})
    has_result = False
    for result in results:
        has_result = True
        print(result)

    if not has_result:
        print("No results")
        if not args.aggressive:
            print("You may try again with --aggressive to consider more possibilities.")


def main() -> None:
    """Run dephrase using arguments retrieved from sys.argv."""

    argparser = argparse.ArgumentParser(description)
    build_argparser(argparser)
    args = argparser.parse_args(sys.argv[1:])
    cli_dephrase(args)


if __name__ == "__main__":
    main()
