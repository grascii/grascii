"""
Contains metrics for comparing search queries to regular expression matches.
"""

import string
from typing import List, Match, NamedTuple, Set

from grascii import grammar
from grascii.parser import Interpretation
from grascii.similarities import get_similar


class AnnotatedStroke(NamedTuple):
    stroke: str
    annotations: Set[str]


GrasciiSequence = List[AnnotatedStroke]


def convert_interpretation(interp: Interpretation) -> GrasciiSequence:
    """Convert an interpretation into a GrasciiSequence

    :param interp: The interpretation to convert.
    :returns: A GrasciiSequence.
    """

    sequence: GrasciiSequence = []
    i = 0
    while i < len(interp):
        item = interp[i]
        assert isinstance(item, str), item
        if i + 1 < len(interp) and isinstance(interp[i + 1], list):
            sequence.append(AnnotatedStroke(item, set(interp[i + 1])))
            i += 2
        else:
            sequence.append(AnnotatedStroke(item, set()))
            i += 1
    return sequence


def convert_match(match: Match) -> GrasciiSequence:
    """Convert an match into a GrasciiSequence

    :param match: The match to convert.
    :returns: A GrasciiSequence.
    """

    sequence: GrasciiSequence = []
    for group in match.groups():
        if group is None:
            continue
        i = 0
        while i < len(group) and group[i] in string.ascii_uppercase:
            i += 1
        if i > 0:
            sequence.append(AnnotatedStroke(group[:i], set(group[i:])))
        else:
            sequence.append(AnnotatedStroke(group, set()))
    return sequence


BASE_COST = 4

COSTS = {"~": 2, "|": 2, ".": 1, ",": 1, "(": 1, ")": 1, "_": 1}
ASP_COST = 1
DIS_COST = BASE_COST


def compute_ins_del_cost(stroke: AnnotatedStroke) -> int:
    """Compute the insertion and deletion cost of a stroke and its
    annotations.

    :param stroke: A stroke and its annotations for which to calculate its cost.
    :returns: A cost of insertion/deletion.
    """

    cost = 0
    if stroke.stroke in grammar.STROKES:
        cost += BASE_COST
    elif stroke.stroke == grammar.ASPIRATE:
        cost += ASP_COST
    elif stroke.stroke == grammar.DISJOINER:
        cost += BASE_COST

    assert cost > 0, stroke
    cost += sum(COSTS.get(annotation, 0) for annotation in stroke.annotations)
    return cost


def get_distance(stroke1: str, stroke2: str) -> int:
    """Calculate the distance between two strokes in a similarity graph.
    Restricted to 0-3.

    :param stroke1: A stroke
    :param stroke2: A second stroke to compute the distance between
    :returns: A distance.
    """

    def in_similarity_graph(distance) -> bool:
        similars = get_similar(stroke1, distance)
        similar_strokes = set()
        for tup in similars:
            similar_strokes |= set(tup)
        return stroke2 in similar_strokes

    for distance in range(3):
        if in_similarity_graph(distance):
            return distance
    return 3


def compute_sub_cost(stroke1: AnnotatedStroke, stroke2: AnnotatedStroke) -> int:
    """Compute the cost of substituting an annotated stroke with another one.

    :param stroke1: The stroke to replace.
    :param stroke2: The new stroke to add.
    :returns: A cost of substitution.
    """

    cost = 0
    if stroke1.stroke in grammar.STROKES and stroke2.stroke in grammar.STROKES:
        cost += get_distance(stroke1.stroke, stroke2.stroke) * BASE_COST
        diff = stroke1.annotations ^ stroke2.annotations
        cost += sum(COSTS.get(annotation, 0) for annotation in diff)
        return cost
    if stroke1.stroke == stroke2.stroke:
        return 0
    return max(compute_ins_del_cost(stroke1), compute_ins_del_cost(stroke2))


def match_distance(seq1: GrasciiSequence, seq2: GrasciiSequence) -> int:
    """Compute a weighed Levenshtein distance between two sequences of annotated
    strokes.

    :param seq1: A GrasciiSequence
    :param seq2: A second GrasciiSequence
    :returns: A distance between seq1 and seq2.
    """

    vec0 = [0]
    for stroke in seq2:
        vec0.append(vec0[-1] + compute_ins_del_cost(stroke))
    vec1 = [0 for i in range(len(seq2) + 1)]

    for stroke1 in seq1:
        vec1[0] = vec0[0] + compute_ins_del_cost(stroke1)

        for j, stroke2 in enumerate(seq2):
            del_cost = vec0[j + 1] + compute_ins_del_cost(stroke1)
            ins_cost = vec1[j] + compute_ins_del_cost(stroke2)
            sub_cost = vec0[j] + compute_sub_cost(stroke1, stroke2)
            vec1[j + 1] = min(del_cost, ins_cost, sub_cost)

        vec0, vec1 = vec1, vec0

    return vec0[len(seq2)]


def standard(interp: Interpretation, match: Match) -> int:
    """Compute the standard metric for a grascii search.

    :param interp: The interpretation to compare to the match
    :param match: The search match.
    :returns: A distance.
    """

    seq1 = convert_interpretation(interp)
    seq2 = convert_match(match)
    return match_distance(seq1, seq2)
