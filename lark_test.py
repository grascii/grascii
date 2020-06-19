from functools import reduce
import re

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
    
    # def distinguishable_consonant(self, children):
        # return children[0], set(children[1:])

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

# test = "PNTS)`"
test = "ABAK"
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
print("Choose an interpretation")
print("0: all")
for i, interp in enumerate(interpretations):
    print(str(i + 1) + ":", interpretationToString(interp))

def makeRegex(interp):
    def reducer(string, token):
        if isinstance(token, set):
            for char in token:
                string += char
        else:
            string += token 
        return string

    return reduce(reducer, interp, "")

first = makeRegex(interpretations[0])

# first = "A*"
print(first)

pattern = re.compile(first);
dictionary = open("./grascii_dict1916.txt", "r")
for line in dictionary:
    if pattern.search(line):
        input(line)
    



    

# for x in CollapseAmbiguities().transform(tree):
    # tokens = MyTrans().transform(x)
    # print(tokens)
    # print()
    # print("".join(tokens))


# ShowTraversal().visit(tree)




# print(p.parse("NTN").pretty())
