

def generate_regex(tokens, match_level):
    if match_level == 1:
        return '^' + ''.join(tokens) + '\\s'
