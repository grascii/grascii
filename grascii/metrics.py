"""
Contains metrics for comparing search queries to regular expression matches.
"""

import re
import string
from typing import List, Union, Set, Match, Tuple, cast

from grascii import grammar
from grascii.similarities import get_similar
from grascii.types import Interpretation


def convert_interpretation(interp: Interpretation) -> List[Tuple[str, Set[str]]]:
    """Convert an interpretation into a form for comparison.
    
    :param interp: The interpretation to convert.
    :returns: A standard form.
    """

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


def convert_match(match: Match) -> List[Tuple[str, Set[str]]]:
    """Convert an match into a form for comparison.
    
    :param match: The interpretation to convert.
    :returns: A standard form.
    """

    new_seq: List[Tuple[str, Set[str]]] = list()
    regex = re.compile("(" + "|".join(grammar.STROKES) + ")?(.*)")
    for group in match.groups():
        if group is None:
            continue
        i = 0
        while i < len(group) and group[i] in string.ascii_uppercase:
            i += 1
        if i > 0:
            new_seq.append((group[:i], {c for c in group[i:]}))
        else:
            new_seq.append((group, set()))
    return new_seq

def distance(s1: str, s2: str) -> int:
    """An implementation of the W-.. algorithm to calculate Lev distance
    based on the 2-vector Wikipedia pseudocode
    """

    m = len(s1)
    n = len(s2)

    v0 = [i for i in range(n + 1)]
    v1 = [0 for i in range(n + 1)]

    for i in range(m):
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

def compute_ins_del_cost(tup: Tuple[str, Set[str]]) -> int:
    """Compute the insertion and deletion cost of a stroke and its 
    annotations.
    
    :param tup: A stroke and its annotations for which to calculate its cost.
    :returns: A cost of insertion/deletion.
    """

    cost = 0
    if tup[0] in grammar.STROKES:
        cost += BASE_COST
    elif tup[0] == grammar.ASPIRATE:
        cost += ASP_COST
    elif tup[0] == grammar.DISJOINER:
        cost += BASE_COST

    if cost == 0:
         print(tup)
    assert cost > 0
    cost += sum(COSTS.get(a, 0) for a in tup[1])
    return cost

def get_distance(s1: str, s2: str) -> int:
    """Calculate the distance between two strokes in a similarity graph.
    Restricted to 0-3.

    :param s1: A stroke
    :param s2: A second stroke to compute the distance between
    :returns: A distance.
    """

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

def compute_sub_cost(t1: Tuple[str, Set[str]], t2: Tuple[str, Set[str]]) -> int:
    """Compute the cost of substituting an annotated stroke with another one.
    
    :param t1: The stroke to replace.
    :param t2: The new stroke to add.
    :returns: A cost of substitution.
    """

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

def match_distance(g1: List[Tuple[str, Set[str]]], g2: List[Tuple[str, Set[str]]]) -> int:
    """Compute a weighed Lev distance between two sequences of annotated
    grascii tokens.
    
    :param g1: A grascii sequence.
    :param g2: A second grascii sequence.
    :returns: The edit distance between g1 and g2.
    """

    m = len(g1)
    n = len(g2)

    v0 = [0]
    for i in range(n):
        v0.append(v0[-1] + compute_ins_del_cost(g2[i]))
    v1 = [0 for i in range(n + 1)]

    for i in range(m):
        v1[0] = v0[0] + compute_ins_del_cost(g1[i])
        
        for j in range(n):
            del_cost = v0[j + 1] + compute_ins_del_cost(g1[i])
            ins_cost = v1[j] + compute_ins_del_cost(g2[j])
            sub_cost = v0[j] + compute_sub_cost(g1[i], g2[j])
            v1[j + 1] = min(del_cost, ins_cost, sub_cost)

        tmp = v0
        v0 = v1
        v1 = tmp
        
    return v0[n]

def standard(interp: Interpretation, match: Match) -> int:
    """Compute the standard metric for a grascii search.
    
    :param interp: The interpretation to compare to the match
    :param match: The search match.
    :returns: An edit distance.
    """

    g1 = convert_interpretation(interp)
    g2 = convert_match(match)
    return match_distance(g1, g2)
