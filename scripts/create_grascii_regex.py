from __future__ import annotations

from pathlib import Path

from lark import Lark, Token, Transformer, Tree
from lark.reconstruct import Reconstructor


class GrasciiProcessor(Transformer):
    def __init__(self, parser):
        super().__init__(visit_tokens=True)
        self.parser = parser

    def start(self, children):
        # insert a new start rule
        new_start = self.parser.parse("start: GRASCII", start="rule")
        return Tree(
            "start", [new_start, Token("_NL", "\n"), Token("_NL", "\n")] + children
        )

    def rule(self, children):
        if children[0] == "_STRING":
            # insert a nonrecursive definition of _string
            new_string = self.parser.parse(
                "_STRING: _LETTER (ASPIRATE? (BOUNDARY | INTERSECTION)? _LETTER)*",
                start="token",
            )
            return new_string
        return Tree("token", children)

    def rule_params(self, children):
        return Tree("token_params", children)

    def RULE(self, token):
        if token == "start":
            # rename the start rule to a token
            return Token("TOKEN", "GRASCII")
        # change all rules to tokens
        return Token("TOKEN", token.upper())


def postproc(strings):
    """Insert necessary spaces back into the lark grammar"""
    prev = ""
    for item in strings:
        if getattr(prev, "type", "") == "OP" and getattr(item, "type", "") in {
            "RULE",
            "TOKEN",
        }:
            yield " "
        yield item
        prev = item


def create_grascii_regex():
    parser = Lark.open_from_package(
        "lark",
        "grammars/lark.lark",
        maybe_placeholders=False,
        parser="lalr",
        start=["start", "token", "rule"],
        keep_all_tokens=True,
    )

    tree = parser.parse(
        Path("grascii/grammars/grascii.lark").read_text(), start="start"
    )
    tree = GrasciiProcessor(parser).transform(tree)

    reconstructor = Reconstructor(parser)
    grammar = reconstructor.reconstruct(tree, postproc)
    Path("grascii/grammars/grascii_regex.lark").write_text(grammar)
    print("Created grascii/grammars/grascii_regex.lark")
    print(grammar)


if __name__ == "__main__":
    create_grascii_regex()
