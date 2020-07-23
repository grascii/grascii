
import sys
import string
import argparse
import pathlib
import os
import time
from configparser import ConfigParser

# import defaults
from grascii import defaults

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

description = "Build a Grascii Dictionary"

def build_argparser(argparser):
    argparser.add_argument("infiles", nargs="+", type=argparse.FileType("r"), 
            help="the files to package")
    argparser.add_argument("-o", "--output", type=os.path.abspath,
            help="path to a directory to output dictionary files")
    argparser.add_argument("-c", "--clean", action="store_true",
            help="clean the output directory before building")
    argparser.add_argument("-p", "--parse", action="store_true",
            help="enable syntax checking on grascii strings")
    argparser.add_argument("-s", "--spell", action="store_true",
            help="enable spell checking on english words")
    argparser.add_argument("-k", "--check-only", action="store_true",
            help="only check input; no output is generated")


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

def build(args):

    conf = ConfigParser()
    conf.read("grascii.conf")

    if args.output is None:
        args.output = conf.get('Build', 'BuildDirectory', 
                fallback=defaults.BUILD["BuildDirectory"])

    args.output = os.path.abspath(args.output)

    start_time = time.perf_counter()

    warnings = 0
    errors = 0

    def log_warning(file_name, line, line_number, *message):
        print("W:", file_name + ":" + str(line_number), *message)
        print(line.strip())
        nonlocal warnings
        warnings += 1

    def log_error(file_name, line, line_number, *message):
        print("E:", file_name + ":" + str(line_number), *message)
        print(line.strip())
        nonlocal errors
        errors += 1

    out_dir = pathlib.Path(args.output)
    out_dir.mkdir(parents=True, exist_ok=True)

    main_words_path = conf.get("Build", "MainWordList",
            fallback=defaults.BUILD["MainWordList"])

    supp_words_path = conf.get("Build", "SupplementaryWordList",
            fallback=defaults.BUILD["SupplementaryWordList"])

    en_dict = set()
    if args.spell:
        try:
            with open(main_words_path, "r") as words:
                en_dict |= set(line.strip().capitalize() for line in words)
        except FileNotFoundError:
            print("Could not find", main_words_path)
        try:
            with open(supp_words_path, "r") as words:
                en_dict |= set(line.strip().capitalize() for line in words)
        except FileNotFoundError:
            print("Could not find", supp_words_path)

    if args.parse:
        from lark import Lark, UnexpectedInput
        from grascii.utils import get_grammar
        p = Lark(get_grammar("grascii"), parser="earley")

    if args.clean:
        for entry in out_dir.iterdir():
            entry.unlink()

    try:
        for src_file in args.infiles:
            for i, line in enumerate(src_file):
                pair = line.split()
                if pair:
                    if pair[0][0] == "#":
                        continue
                    if pair[0] == "?":
                        log_warning(src_file.name, line, i + 1, "uncertainty")
                        pair.pop(0)
                    if len(pair) < 2:
                        log_error(src_file.name, line, i + 1, 
                                "Too few words")
                        continue
                    if len(pair) > 2:
                        log_warning(src_file.name, line, i + 1, 
                                "Wrong number of words")
                        continue
                    grascii = pair[0].upper()
                    # strip '-'
                    grascii = "".join(grascii.split("-"))
                    word = pair[1].capitalize()

                    if args.parse:
                        try:
                            p.parse(grascii)
                        except UnexpectedInput:
                            log_error(src_file.name, line, i + 1,
                                    "failed to parse", grascii)
                            continue

                    if args.spell:
                        if word not in en_dict:
                            log_warning(src_file.name, line, i + 1,
                                    word, "not in dictionary")

                    if not args.check_only:
                        out = get_output_file(args.output, grascii)
                        out.write(grascii + " ")
                        out.write(word + "\n")
    finally:
        for f in out_files.values():
            f.close()

    end_time = time.perf_counter();

    if warnings or errors:
        print()

    total = 0
    for key, val in entry_counts.items():
        total += val
        print("Wrote", val, "entries to", pathlib.PurePath(args.output, key))

    print()
    total_time = "{:.5f}".format(end_time - start_time)
    print("Finished Build in", total_time, "seconds")
    if total > 0:
        print(total, "entries")
    print(warnings, "warnings")
    print(errors, "errors")

def main(sys_args):
    argparser = argparse.ArgumentParser(description)
    build_argparser(argparser)
    args = argparser.parse_args(sys_args)
    build(args)

if __name__ == "__main__":
    main(sys.argv[1:])

