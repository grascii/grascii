
import string

# path = "./dict_test.txt"
path = "./grascii_dict1916.txt"
dest = "./dict/"

"""
add option to use parser for syntax check
add werror: treat warnings as errors
warnings still add line, errors skip them
allow continue for line with more than 2 tokens
spell check?
add file to warnings

add dest options
add file input options

track entry count by letter
clear dest dir before writing
sort alphabetically?

"""


out_files = {}
def getOutputfile(grascii):
    index = 0
    while index < len(grascii) and grascii[index] not in string.ascii_uppercase:
        index += 1
    if index == len(grascii):
        raise Exception()

    char = grascii[index]
    try:
        return out_files[char]
    except KeyError:
        out_files[char] = open(dest + char, "w")
        return out_files[char]

try:
    with open(path, "r") as src:
        for i, line in enumerate(src):
            pair = line.split()
            if pair:
                if pair[0][0] == "#":
                    continue
                if len(pair) != 2:
                    print("W: Line", i, "Wrong number of words")
                    print(line.strip())
                    continue
                grascii = pair[0]
                word = pair[1]
                grascii = grascii.upper()
                word = word.capitalize()
                out = getOutputfile(grascii)
                out.write(grascii + " ")
                out.write(word + "\n")
finally:
    for f in out_files.values():
        f.close()

