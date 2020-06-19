
from lark import Lark, Visitor, Transformer, Discard, Token
from lark.visitors import CollapseAmbiguities

class ShowTraversal(Visitor):
    def __default__(self, tree):
        print(tree)
        return tree

class MyTrans(Transformer):
    def start(self, children):
        result = list()
        for child in children:
            for token in child:
                result.append(token)
        return result

    def circle_vowel(self, children):
        return children[0], set(children[1:])

    def hook_vowel(self, children):
        return children[0], set(children[1:])
    
    def diphthong(self, children):
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


p = Lark.open("grascii.lark",
              parser="earley",
              ambiguity="explicit")

test = "O,,,A"
tree = p.parse(test)
# print(tree.pretty())
for x in CollapseAmbiguities().transform(tree):
    print(x)
    tokens = MyTrans().transform(x)
    print(tokens)
    print()
    # print("".join(tokens))


# ShowTraversal().visit(tree)




# print(p.parse("NTN").pretty())
