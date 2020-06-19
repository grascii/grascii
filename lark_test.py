
from lark import Lark, Visitor, Transformer, Discard
from lark.visitors import CollapseAmbiguities

class ShowTraversal(Visitor):
    def __default__(self, tree):
        print(tree)
        return tree

class MyTrans(Transformer):
    def start(self, tree):
        result = list()
        for child in tree:
            for token in child:
                result.append(token)
        return result

    def __default__(self, data, children, meta):
        result = list()
        for child in children:
            # for token in child:
            result.append(child)
        return result


p = Lark.open("grascii.lark",
              parser="earley",
              ambiguity="explicit")

test = "A|,NT"
tree = p.parse(test)
# print(tree.pretty())
for x in CollapseAmbiguities().transform(tree):
    # print(x)
    tokens = MyTrans().transform(x)
    print(tokens)
    # print("".join(tokens))


# ShowTraversal().visit(tree)




# print(p.parse("NTN").pretty())
