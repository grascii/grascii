
import argparse
from typing import Set
import sys

from lark import Lark, Transformer, Token, UnexpectedInput
from lark.visitors import CollapseAmbiguities

from grascii.grammars import get_grammar


description = "Decipher a shorthand phrase."

def build_argparser(argparser: argparse.ArgumentParser) -> None:
    argparser.add_argument("phrase", action="store", 
            help="The phrase to decipher")

class PhraseFlattener(Transformer):
    def start(self, children):
        result = list()
        for child in children:
            for token in child:
                result.append(token)
        return result

    def short_to(self, children):
        token = type('',(object,),{"type": "TO"})()
        result = list()
        result.append(token)
        return result

    def omitted_to_noun(self, children):
        results = self.__default__(None, children, None)
        results.append(type("", (object,), {"type": "TO"}))
        return results

    def omitted_to_verb(self, children):
        results = self.__default__(None, children, None)
        results.append(type("", (object,), {"type": "TO"}))
        return results

    def __default__(self, data, children, meta):
        result = list()
        for child in children:
            if isinstance(child, Token):
                result.append(child)
            else:
                for token in child:
                    result.append(token)
        return result

def dephase(phrase: str) -> Set[str]:
    g = get_grammar("phrases")
    parser = Lark(g, parser="earley", ambiguity="explicit")
    trans = PhraseFlattener()
    parses: Set[str] = set()
    try:
        tree = parser.parse(phrase.upper())
    except UnexpectedInput:
        print("exception")
        return parses

    trees = CollapseAmbiguities().transform(tree)
    for t in trees:
        tokens = (token.type for token in trans.transform(t))
        parses.add(" ".join(tokens))
    return parses

def cli_dephrase(args: argparse.Namespace) -> None:
    results = dephase(args.phrase)
    for result in results:
        print(result)

def main() -> None:
    argparser = argparse.ArgumentParser(description)
    build_argparser(argparser)
    args = argparser.parse_args(sys.argv[1:])
    cli_dephrase(args)

if __name__ == "__main__":
    main()
