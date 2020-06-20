from functools import reduce
import re

from lark import Lark, Visitor, Transformer, Discard, Token, UnexpectedInput
from lark.visitors import CollapseAmbiguities

from graph_test import *

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
# test = "ABAK"
test = ""
while True:
    test = input("Enter search: ").upper()
    if test == "":
        continue
    try:
        tree = p.parse(test)
        break
    except UnexpectedInput as e:
        print("Syntax Error")
        print(e.get_context(test))

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

index = -1
if len(interpretations) == 1:
    print()
    print("Found 1 possible interpretation")
    print("Beginning search")
    index = 0
else:
    print("Interpretations: ", len(interpretations))
    print()
    print("0: all")
    for i, interp in enumerate(interpretations):
        print(str(i + 1) + ":", interpretationToString(interp))

    while True:
        try:
          index = int(input("Choose an interpretation to use in the search:"))
          if index < 0 or index > len(interpretations):
              continue
          break
        except ValueError:
            continue


def makeRegex(interp):
    def reducer(builder, token):
        if isinstance(token, set):
            builder.append("[")
            for char in token:
                builder.append(char)
            builder.append("]*")
        else:
            builder.append(getAltsRegex(token, 1))
        return builder

    regex = reduce(reducer, interp, ["^"])
    regex.append("\\s")

    return "".join(regex)

# first = makeRegex(interpretations[0])
first = makeRegex(interpretations[index - 1])

# first = "A*"
print(first)

results = 0
pattern = re.compile(first);
dictionary = open("./grascii_dict1916.txt", "r")
for line in dictionary:
    if pattern.search(line):
        results += 1
        input(line)

print("Results:", results)
