



import string


path = "./dict_test.txt"
dest = "./dict/"

# use parser to check syntax

out = open(dest + "A", "w")

out_files = {}
def getOutputfile(grascii):
    index = 0
    while index < len(grascii) and grascii[index] not in string.ascii_uppercase :
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

