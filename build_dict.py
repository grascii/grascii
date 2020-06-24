
import sys
import string
import argparse


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
entry_counts = {}
# path = "./dict_test.txt"
# path = "./dsrc/grascii_dict1916.txt"
path = "./dsrc/z.txt"
dest = "./dict/"

def get_output_file(grascii):
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
        entry_counts[char] = 1
        return out_files[char]

def main(arguments):

    aparse = argparse.ArgumentParser(description="Build the grascii dictionary")
    aparse.add_argument("infiles", nargs="+", type=argparse.FileType("r"),
            help="the files to package")

    args = aparse.parse_args(arguments)

    warnings = 0
    errors = 0

    try:
        for file_name in args.infiles:
            with file_name as src:
            # with open(path, "r") as src:
                for i, line in enumerate(src):
                    pair = line.split()
                    if pair:
                        if pair[0][0] == "#":
                            continue
                        if pair[0] == "?":
                            print("W: Line", i, "uncertainty")
                            print(line.strip())
                            pair.pop(0)
                            warnings += 1
                        if len(pair) != 2:
                            print("W: Line", i, "Wrong number of words")
                            print(line.strip())
                            warnings += 1
                            continue
                        grascii = pair[0]
                        word = pair[1]
                        grascii = grascii.upper()
                        word = word.capitalize()
                        out = get_output_file(grascii)
                        out.write(grascii + " ")
                        out.write(word + "\n")
    finally:
        for f in out_files.values():
            f.close()

    if warnings or errors:
        print()
    print("Finished Build")
    print(warnings, "warnings")
    print(errors, "errors")
    print()
    for key, val in entry_counts.items():
        print("Wrote", val, "entries to", dest + key)

if __name__ == "__main__":
    main(sys.argv[1:])
