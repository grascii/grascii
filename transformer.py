

annotatable = {
        'A',
        'E',
        'I',
        'O',
        'U',
        'S',
        'SH',
        'TH'
        }

def transform(tokens, match_level):
    if match_level == 1:
        return tokens
    elif match_level == 2:
        new_tokens = []
        for token in tokens:
            new_tokens.append(token)
            if token in annotatable:
                new_tokens.append('**')
        return new_tokens
