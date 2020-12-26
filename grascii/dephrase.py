
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

    optionals = {
        "opt_to": "TO",
        "opt_in": "IN",
        "opt_of": "OF",
        "opt_your": "YOUR",
    }

    def __init__(self):
        for key, value in self.optionals.items():
            setattr(self, key, self.make_opt(value))

    def make_opt(self, name):
        def opt(children):
            if len(children):
                return self.__default__(None, children, None)
            return [self.create_token("(" + name + ")")]
        return opt

    def start(self, children):
        result = list()
        for child in children:
            for token in child:
                result.append(token)
        return result

    def create_token(self, name: str, value: str=""):
        return Token(name, value)

    def short_to(self, children):
        return [self.create_token("TO")]

    def __default__(self, data, children, meta):
        result = list()
        for child in children:
            if isinstance(child, Token):
                # strip namespace
                i = child.type.rfind("_")
                new_type = child.type[i + 1:]
                result.append(self.create_token(new_type, child.value))
            else:
                for token in child:
                    result.append(token)
        return result

def dephrase(phrase: str) -> Set[str]:
    g = get_grammar("phrases")
    parser = Lark.open(g, parser="earley", ambiguity="explicit", lexer='dynamic_complete')
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
    results = dephrase(args.phrase)
    for result in results:
        print(result)

def main() -> None:
    argparser = argparse.ArgumentParser(description)
    build_argparser(argparser)
    args = argparser.parse_args(sys.argv[1:])
    cli_dephrase(args)

if __name__ == "__main__":
    main()
