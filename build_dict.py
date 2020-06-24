
import sys
import string
import argparse
import pathlib
import time

from lark import Lark, UnexpectedInput


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
# dest = "./dict/"

def get_output_file(dest, grascii):
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
        out_files[char] = pathlib.Path(dest, char).open("w")
        entry_counts[char] = 1
        return out_files[char]

def main(arguments):

    aparse = argparse.ArgumentParser(description="Build the grascii dictionary")
    aparse.add_argument("infiles", nargs="+", type=argparse.FileType("r"),
            help="the files to package")

    aparse.add_argument("-o", "--output", help="path to a directory to output\
            dictionary files", default="./dict")

    aparse.add_argument("-c", "--clean", action="store_true",
            help="clean the output directory before building")

    args = aparse.parse_args(arguments)

    start_time = time.perf_counter()

    warnings = 0
    errors = 0

    out_dir = pathlib.Path(args.output)
    out_dir.mkdir(parents=True, exist_ok=True)

    p = Lark.open("grascii.lark", parser="earley")

    if args.clean:
        for entry in out_dir.iterdir():
            entry.unlink()

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
                        grascii = pair[0].upper()
                        word = pair[1].capitalize()
                        try:
                            p.parse(grascii)
                        except UnexpectedInput:
                            print("E: Line", i, "failed to parse", grascii)
                            print(line.strip())
                            errors += 1
                            continue
                        out = get_output_file(args.output, grascii)
                        out.write(grascii + " ")
                        out.write(word + "\n")
    finally:
        for f in out_files.values():
            f.close()

    end_time = time.perf_counter();

    if warnings or errors:
        print()
    print("Finished Build in", end_time - start_time, "seconds")
    print(warnings, "warnings")
    print(errors, "errors")
    print()
    for key, val in entry_counts.items():
        print("Wrote", val, "entries to", pathlib.PurePath(args.output, key))

if __name__ == "__main__":
    main(sys.argv[1:])
