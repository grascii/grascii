

alphabet = {'A',
            'B',
            'C',
            'D',
            'E',
            'F',
            'G',
            'H',
            'I',
            'J',
            'K',
            'L',
            'M',
            'N',
            'O',
            'P',
            'R',
            'S',
            'T',
            'U',
            'V',
            '~',
            '^',
            '(',
            ')',
            '-',
            '_',
            '|',
            '/',
            '\\',
            '\'',
            '\"',
            ',',
            '.',
            '?'}


tokens = {'A',
            'B',
            'CH',
            'D',
            'DD',
            'DF',
            'DM',
            'DN',
            'DT',
            'DV',
            'E',
            'F',
            'G',
            'I',
            'J',
            'JND',
            'JNT',
            'K',
            'L',
            'M',
            'MD',
            'MM',
            'MN',
            'MT',
            'N',
            'ND',
            'NT',
            'O',
            'P',
            'PND',
            'PNT',
            'R',
            'S',
            'SH',
            'SS',
            'T',
            'TD',
            'TH',
            'TN',
            'TM',
            'U',
            'V',
            '/G',
            '/K',
            '~',
            '^',
            '(',
            ')',
            '-',
            '_',
            '|',
            '\\',
            '\'',
            '\"',
            ',',
            '.',
            '?'}

def determine_pending_symbols(tokens = tokens):
    pending_symbols = set()
    for item in tokens:
        length = len(item)
        if length > 1:
            for i in range(length - 1):
                pending_symbols.add(item[i])
    return pending_symbols


 
def make_tokens(grascii, tokens = tokens, max_length = 3):

    def pop_stack():
        nonlocal stack
        nonlocal result
        nonlocal pending_symbols

        temp_token = ''.join(stack)
        if temp_token in tokens:
            result.append(temp_token)
            stack = []
        elif stack[-1] not in pending_symbols:
            char = stack.pop()
            pop_stack()
            result.append(char)


    result = []
    pending_symbols = determine_pending_symbols(tokens)
    stack = []
    for char in grascii:
        if char not in alphabet:
            raise Exception()
        if char in pending_symbols:
            stack.append(char)
        elif stack:
            stack.append(char)
            pop_stack()
        elif char in tokens:
            result.append(char)
    pop_stack()
    return result




