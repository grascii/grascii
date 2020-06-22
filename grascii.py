from functools import reduce
import re

from lark import Lark, Visitor, Transformer, Discard, Token, UnexpectedInput
from lark.visitors import CollapseAmbiguities

from graph_test import *

class GrasciiFlattener(Transformer):

    def __init__(self):
        self.circle_vowel = self.group_modifiers
        self.hook_vowel = self.group_modifiers
        self.diphthong = self.group_modifiers
        self.directed_consonant = self.group_modifiers
        self.sh = self.group_modifiers

    def start(self, children):
        result = list()
        for child in children:
            for token in child:
                result.append(token)
        return result

    def group_modifiers(self, children):
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


def create_parser():
    return Lark.open("grascii.lark",
              parser="earley",
              ambiguity="explicit")

p = create_parser()

def run_interactive():
    tree = get_grascii_search()
    parses = flatten_tree(tree)
    display_interpretations = get_unique_interpretations(parses)
    interpretations = list(display_interpretations.values())
    index = choose_interpretation(interpretations)

def get_grascii_search():
    while True:
        search = input("Enter search: ").upper()
        if search == "":
            continue
        try:
            return p.parse(search)
        except UnexpectedInput as e:
            print("Syntax Error")
            print(e.get_context(search))

def flatten_tree(parse_tree):
    trees = CollapseAmbiguities().transform(parse_tree)
    trans = GrasciiFlattener()
    return [trans.transform(tree) for tree in trees]


run_interactive()

def interpretationToString(interp):
    def reducer(string, token):
        if isinstance(token, set):
            for char in token:
                string += char
        else:
            if string and string[-1] != "^" and token != "^":
                string += "-"

            string += token 
        return string

    return reduce(reducer, interp, "")

def choose_interpretation(interpretations):
    if len(interpretations) == 1:
        print()
        print("Found 1 possible interpretation")
        print("Beginning search")
        return 0
    else:
        print("Interpretations: ", len(interpretations))
        print()
        print("0: all")
        for i, interp in enumerate(interpretations):
            print(str(i + 1) + ":", interpretationToString(interp))

        while True:
            try:
              index = int(input("Choose an interpretation to use in the search:"))
              if index >= 0 and index <= len(interpretations):
                  return index
            except ValueError:
                continue


# trees = CollapseAmbiguities().transform(tree)
# trans = GrasciiFlattener()
# interpretations = [trans.transform(x) for x in trees]
# print(interpretations)

def get_unique_interpretations(flattened_parses):
    return {interpretationToString(interp): interp for interp in flattened_parses}


# interps = { interpretationToString(interp): interp for interp in interpretations }
# interpretations = list(interps.values())

# index = -1
# if len(interpretations) == 1:
    # print()
    # print("Found 1 possible interpretation")
    # print("Beginning search")
    # index = 0
# else:
    # print("Interpretations: ", len(interpretations))
    # print()
    # print("0: all")
    # for i, interp in enumerate(interpretations):
        # print(str(i + 1) + ":", interpretationToString(interp))

    # while True:
        # try:
          # index = int(input("Choose an interpretation to use in the search:"))
          # if index < 0 or index > len(interpretations):
              # continue
          # break
        # except ValueError:
            # continue


def makeRegex(interp, distance):
    def reducer(builder, token):
        if isinstance(token, set):
            if token and distance == 0:
                builder.append("[")
                for char in token:
                    builder.append(char)
                builder.append("]*")
        else:
            builder.append(getAltsRegex(token, distance))
        return builder

    regex = reduce(reducer, interp, ["^"])
    regex.append("\\s")

    return "".join(regex)


patterns = list()
starting_letters = set()
distance = 0
if index > 0:
    patterns.append(re.compile(makeRegex(interpretations[index - 1], distance)))
    starting_letters.add(interpretationToString(interpretations[index - 1])[0])
else:
    for interp in interpretations:
        patterns.append(re.compile(makeRegex(interp, distance)))
        starting_letters.add(interpretationToString(interp[0]))
    # patterns = [re.compile(makeRegex(interp)) for interp in interpretations]

# first = makeRegex(interpretations[0])
first = makeRegex(interpretations[index - 1], distance)

# first = "A*"
print(first)

results = 0
# pattern = re.compile(first);
# dictionary = open("./grascii_dict1916.txt", "r")

dict_path = "./dict/"
for item in starting_letters:
    with open(dict_path + item, "r") as dictionary:
        for line in dictionary:
            for pattern in patterns:
                if pattern.search(line):
                    results += 1
                    input(line)
                    break


print("Results:", results)
