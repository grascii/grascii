
import alphabet as tokenizer, transformer, compiler

def grascii2regex(grascii, match_level):
    tokens = tokenizer.make_tokens(grascii)
    tokens = transformer.transform(tokens, match_level)
    return compiler.generate_regex(tokens, match_level)


