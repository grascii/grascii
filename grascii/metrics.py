from typing import List, Union, Set, Match, Tuple
import re
import string

from grascii import grammar
from grascii.similarities import get_similar

def convert_interpretation(interp: List[Union[list, str]]) -> List[Tuple[str, Set[str]]]:
    new_interp: List[Tuple[str, Set[str]]] = list()
    i = 0
    while i < len(interp):
        item = interp[i]
        if i + 1 < len(interp):
            if isinstance(interp[i + 1], list):
                new_interp.append((item, set(interp[i + 1])))
                i += 2
                continue
        new_interp.append((item, set()))
        i += 1
    return new_interp


def convert_match(match: Match):
    new_seq: List[Tuple[str, Set[str]]] = list()
    regex = re.compile("(" + "|".join(grammar.STROKES) + ")?(.*)")
    for group in match.groups():
        if group is None:
            continue
        i = 0
        while i < len(group) and group[i] in string.ascii_uppercase:
            i += 1
        # m = regex.match(group)
        # assert m
        # if m.group(1) in grammar.STROKES:
        if i > 0:
            # new_seq.append((m.group(1), {c for c in m.group(2)}))
            new_seq.append((group[:i], {c for c in group[i:]}))
        else:
            new_seq.append((group, set()))
    return new_seq

def check(match):
    print(convert_match(match))

def distance(s1, s2):
    m = len(s1)
    n = len(s2)

    v0 = [i for i in range(n + 1)]
    v1 = [0 for i in range(n + 1)]

    for i in range(m):
        print(v0)
        v1[0] = i + 1
        
        for j in range(n):
            del_cost = v0[j + 1] + 1
            ins_cost = v1[j] + 1
            if s1[i] == s2[j]:
                sub_cost = v0[j]
            else:
                sub_cost = v0[j] + 1

            v1[j + 1] = min(del_cost, ins_cost, sub_cost)

        tmp = v0
        v0 = v1
        v1 = tmp
        
    print(v0)

    return v0[n]

BASE_COST = 4

COSTS = {
    "~": 2,
    "|": 2,
    ".": 1,
    ",": 1,
    "(": 1,
    ")": 1,
    "_": 1
}
ASP_COST = 1
DIS_COST = BASE_COST

def compute_ins_del_cost(tup):
    cost = 0
    if tup[0] in grammar.STROKES:
        cost += BASE_COST
    elif tup[0] == grammar.ASPIRATE:
        cost += ASP_COST
    elif tup[0] == grammar.DISJOINER:
        cost += BASE_COST

    # print(tup[1])
    assert isinstance(tup[1], set)
    cost += sum(COSTS.get(a, 0) for a in tup[1])
    return cost

def get_distance(s1, s2):
    def in_sim(dis):
        sim = get_similar(s1, dis)
        s = set()
        for t in sim:
            s |= {a for a in t}
        return s2 in s

    for i in range(3):
        if in_sim(i):
            return i
    return 3

def compute_sub_cost(t1, t2):
    cost = 0
    if t1[0] in grammar.STROKES and t2[0] in grammar.STROKES:
        cost += get_distance(t1[0], t2[0]) * BASE_COST
        diff = t1[1] ^ t2[1]
        cost += sum(COSTS.get(a, 0) for a in diff)
        return cost
    else:
        if t1[0] == t2[0]:
            return 0
        return max(compute_ins_del_cost(t1), compute_ins_del_cost(t2))

# print(compute_ins_del_cost(("A", {"~", ","})))

def match_distance(g1, g2):
    m = len(g1)
    n = len(g2)

    v0 = [0]
    for i in range(n):
        v0.append(v0[-1] + compute_ins_del_cost(g2[i]))
    # v0 = [i for i in range(n + 1)]
    v1 = [0 for i in range(n + 1)]

    for i in range(m):
        print(v0)
        # v1[0] = i + 1
        v1[0] = v0[0] + compute_ins_del_cost(g1[i])
        
        for j in range(n):
            del_cost = v0[j + 1] + compute_ins_del_cost(g2[j])
            # print(del_cost)
            ins_cost = v1[j] + compute_ins_del_cost(g1[i])
            # print(ins_cost)
            sub_cost = v0[j] + compute_sub_cost(g1[i], g2[j])
            # print(sub_cost)
            # if s1[i] == s2[j]:
                # sub_cost = v0[j]
            # else:
                # sub_cost = v0[j] + 1

            v1[j + 1] = min(del_cost, ins_cost, sub_cost)

        tmp = v0
        v0 = v1
        v1 = tmp
        
    print(v0)

    return v0[n]

# match_distance([("A", set())], [("A", {","})])

def standard(interp, match):
    g1 = convert_interpretation(interp)
    g2 = convert_match(match)
    print(g1)
    print(g2)
    return match_distance(g1, g2)
