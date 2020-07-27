from typing import List, Union, Set, Match
import re

from grascii import grammar

def convert_interpretation(interp: List[Union[list, str]]) -> List[Union[Set[str], str]]:
    new_interp: List[Union[Set[str], str]] = list()
    i = 0
    while i < len(interp):
        item = interp[i]
        new_interp.append(item)
        if i + 1 < len(interp):
            if isinstance(interp[i + 1], list):
                new_interp.append(set(interp[i + 1]))
                i += 2
                continue
        new_interp.append(set())           
        i += 1
    return new_interp


def convert_match(match: Match):
    new_seq: List[Union[Set[str], str]] = list()
    regex = re.compile("(" + "|".join(grammar.STROKES) + ")?(.*)")
    for group in match.groups():
        if group is None:
            continue
        m = regex.match(group)
        assert m
        if m.group(1) in grammar.STROKES:
            new_seq.append(m.group(1))
            new_seq.append({c for c in m.group(2)})
        else:
            new_seq.append(group)
            new_seq.append(set())
    return new_seq

def check(match):
    print(convert_match(match))

def distance(s1, s2):
    m = len(s1)
    n = len(s2)

    v0 = [i for i in range(n + 1)]

    for i in range(m):
        print(v0)
        v1 = [0 for i in range(n + 1)]
        v1[0] = i + 1
        
        for j in range(n):
            del_cost = v0[j + 1] + 1
            ins_cost = v1[j] + 1
            if s1[i] == s2[j]:
                sub_cost = v0[j]
            else:
                sub_cost = v0[j] + 1

            v1[j + 1] = min(del_cost, ins_cost, sub_cost)

        v0 = v1
        
    print(v0)

    return v0[n]

distance("kitten", "sitting")
