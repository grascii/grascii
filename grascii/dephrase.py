
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

    def create_token(self, name: str):
        return Token(name, name)

    def short_to(self, children):
        return [self.create_token("TO")]

    def omitted_to_noun(self, children):
        results = self.__default__(None, children, None)
        results.append(self.create_token("(TO)"))
        results.append(self.create_token("(THE)"))
        return results

    def omitted_to_verb(self, children):
        results = self.__default__(None, children, None)
        results.append(self.create_token("(TO)"))
        return results

    def receipt_phrase(self, children):
        i = len(children) - 1
        while i >= 0 and not isinstance(children[i], Token):
            i -= 1
        children.insert(i, self.create_token("(IN)"))
        print(i)
        if i < len(children) - 2:
            children.insert(i + 2, self.create_token("(OF)"))
            children.insert(i + 3, self.create_token("(YOUR)"))
        return self.__default__(None, children, None)

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
    parser = Lark(g, parser="earley", ambiguity="resolve")
    aparser = Lark(g, parser="earley", ambiguity="explicit")
    # parser = Lark.open("./test.lark", parser="earley", ambiguity="explicit")
    trans = PhraseFlattener()
    parses: Set[str] = set()
    try:
        tree = parser.parse(phrase.upper())
        atree = aparser.parse(phrase.upper())
    except UnexpectedInput:
        print("exception")
        return parses

    # print(tree.pretty())
    trees = CollapseAmbiguities().transform(tree)
    trees += CollapseAmbiguities().transform(atree)
    for t in trees:
        print(t.pretty())
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
