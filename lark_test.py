from functools import reduce

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

test = "PNT"
# test = "ABAK"
tree = p.parse(test)
# print(tree.pretty())

def interpretationToString(interp):
    def reducer(string, token):
        if isinstance(token, set):
            for char in token:
                string += char
        else:
            string += "-" + token 
        return string

    return reduce(reducer, interp, "")[1:]

trees = CollapseAmbiguities().transform(tree)
trans = MyTrans()
interpretations = [trans.transform(x) for x in trees]

print("Interpretations: ", len(interpretations))
print("0: all")
for i, interp in enumerate(interpretations):
    print(i + 1, ":", interpretationToString(interp))
    

# for x in CollapseAmbiguities().transform(tree):
    # tokens = MyTrans().transform(x)
    # print(tokens)
    # print()
    # print("".join(tokens))


# ShowTraversal().visit(tree)




# print(p.parse("NTN").pretty())
