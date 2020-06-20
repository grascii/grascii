
import argparse
import alphabet as tokenizer, transformer, compiler

def grascii2regex(grascii, match_level):
    tokens = tokenizer.make_tokens(grascii)
    tokens = transformer.transform(tokens, match_level)
    return compiler.generate_regex(tokens, match_level)

parser = argparse.ArgumentParser(description='Search a Grascii dictionary')
parser.add_argument('grascii', help='a grascii string to search for')
parser.add_argument('-m', '--match-level', help='how close the search should be',
        default=2, type=int, choices=range(1,5))

args = parser.parse_args()

print(grascii2regex(args.grascii, args.match_level))
