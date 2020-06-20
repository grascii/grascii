
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

warnings = 0
errors = 0

out_files = {}
entry_counts = {}
def getOutputfile(grascii):
    index = 0
    while index < len(grascii) and grascii[index] not in string.ascii_uppercase:
        index += 1
    if index == len(grascii):
        raise Exception()

    char = grascii[index]
    try:
        result = out_files[char]
        entry_counts[char] += 1
        return result
    except KeyError:
        out_files[char] = open(dest + char, "w")
        entry_counts[char] = 0
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
                    warnings += 1
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

print("Finished Build")
print(warnings, "warnings")
print(errors, "errors")
print()
for key, val in entry_counts.items():
    print("Wrote", val, "entries to", dest + key)

