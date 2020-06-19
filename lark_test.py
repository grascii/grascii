
from lark import Lark
from lark.visitors import CollapseAmbiguities

p = Lark.open("grascii.lark",
              parser="earley",
              ambiguity="explicit")

test = "NTN"
tree = p.parse(test)
for x in CollapseAmbiguities().transform(tree):
    print(x.pretty())

# print(p.parse("NTN").pretty())
