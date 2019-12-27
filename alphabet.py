
import marisa_trie
from collections import deque

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

token_trie = marisa_trie.Trie(tokens)

def determine_pending_symbols(tokens = tokens):
    pending_symbols = set()
    for item in tokens:
        length = len(item)
        if length > 1:
            for i in range(length - 1):
                pending_symbols.add(item[i])
    return pending_symbols


 
def make_tokens(grascii, tokens = token_trie, max_length = 3):

    def process_deque(clear = False):
        nonlocal dq
        nonlocal result
        nonlocal pending_symbols

        temp_token = ''.join(dq)
        print(dq)
        if temp_token in tokens and (temp_token not in pending_symbols or clear):
            result.append(temp_token)
            dq = deque()
        elif dq[-1] not in pending_symbols:
            char = dq.pop()
            if dq:
                process_deque(clear = True)
            result.append(char)
        elif not tokens.keys(temp_token):
            char = dq.popleft()
            result.append(char)
            process_deque()

    result = []
    pending_symbols = determine_pending_symbols(tokens)
    dq = deque()
    for char in grascii:
        if char not in alphabet:
            raise Exception()
        if char in pending_symbols:
            dq.append(char)
            process_deque()
        elif dq:
            dq.append(char)
            process_deque()
        elif char in tokens:
            result.append(char)
    if dq:
        process_deque(clear = True)
    return result




