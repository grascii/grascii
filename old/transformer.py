

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

splitable = {
        'DD',
        'DT',
        'TD',
        'MN',
        'MM',
        'SS',
        'MT',
        'MD',
        'ND',
        'NT',
        'JNT',
        'JND',
        'PND',
        'PNT',
        'DF',
        'DV',
        'TM',
        'TN',
        'DM',
        'DN'
        }

def transform(tokens, match_level):
    if match_level == 1:
        return tokens
    elif match_level == 2:
        new_tokens = []
        for token in tokens:
            new_tokens.append(token)
            if token in annotatable:
                new_tokens.append('*' + token)
        return new_tokens
    elif match_level == 3:
        new_tokens = []
        for token in tokens:
            new_tokens.append(token)
            if token in annotatable:
                new_tokens.append('*' + token)
        return new_tokens

