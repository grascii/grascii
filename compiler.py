#import transformer

annotations = {
        'A': '.,~|',
        'E': '.,~|',
        'I': '.,~',
        'O': '.,',
        'U': '.,',
        'S': '(),',
        'TH': '(),',
        'SH': ','
        }

equivalents = {
        'MD': 'MT',
        'MT': 'MD',
        'ND': 'NT',
        'NT': 'ND',
        'MM': 'MN',
        'MN': 'MM',
        'DF': 'DV',
        'DV': 'DF',
        'TD': 'DD|DT',
        'DD': 'TD|DT',
        'DT': 'TD|DD',
        'JND': 'JNT|PND|PNT',
        'JNT': 'JND|PND|PNT',
        'PND': 'JND|JNT|PNT',
        'PNT': 'JND|JNT|PND'
        }

def generate_regex(tokens, match_level):
    if match_level == 1:
        return '^' + ''.join(tokens) + '\\s'
    elif match_level == 2:
        builder = []
        builder.append('^')
        for token in tokens:
            if token == '**':
                prev_token = builder[-1]
                try:
                    builder.append('[{}]*'.format(annotations[prev_token]))
                except KeyError:
                    raise Exception
            else:
                equiv = equivalents.get(token)
                if equiv is not None:
                    builder.append('({}|{})'.format(token, equiv))
                else:
                    builder.append(token)
        builder.append('\\s')
        return ''.join(builder)

                
            


