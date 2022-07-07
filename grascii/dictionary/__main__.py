from __future__ import annotations

import argparse
import sys

from grascii.dictionary import build_argparser


def main() -> None:
    argparser = argparse.ArgumentParser(prog="dictionary")
    build_argparser(argparser)
    args = argparser.parse_args(sys.argv[1:])
    args.func(args)


if __name__ == "__main__":
    main()
