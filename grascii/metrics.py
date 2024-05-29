"""
Contains metrics for comparing search queries to regular expression matches.
"""

from __future__ import annotations

import string
import sys
from typing import (
    TYPE_CHECKING,
    Any,
    Callable,
    List,
    Match,
    NamedTuple,
    Optional,
    Set,
    Tuple,
    TypeVar,
)

from grascii import grammar
from grascii.parser import Interpretation
from grascii.similarities import get_similar

if TYPE_CHECKING:
    if sys.version_info >= (3, 8):
        from typing import Protocol
    else:
        from typing_extensions import Protocol
    from grascii.searchers import SearchResult

    class Comparable(Protocol):
        def __lt__(self, other: Any) -> bool:
            pass

    CT = TypeVar("CT", bound=Comparable)


class AnnotatedStroke(NamedTuple):
    stroke: str
    annotations: Set[str]


GrasciiSequence = List[AnnotatedStroke]


def interpretation_to_gsequence(interp: Interpretation) -> GrasciiSequence:
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


def match_to_gsequence(match: Match[str]) -> GrasciiSequence:
    """Convert a match into a ``GrasciiSequence``

    :param match: The match to convert.
    :returns: A ``GrasciiSequence``.
    """

    sequence: GrasciiSequence = []
    adjusted_matched_grascii_index = match.re.groupindex["matched_grascii"] - 1
    for index, group in enumerate(match.groups()):
        if index == adjusted_matched_grascii_index:
            # the matched_grascii group is not a leaf group
            continue
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


def gsequence_distance(seq1: GrasciiSequence, seq2: GrasciiSequence) -> int:
    """Compute a weighed Levenshtein distance between two sequences of annotated
    strokes.

    :param seq1: A ``GrasciiSequence``
    :param seq2: A second ``GrasciiSequence``
    :returns: A distance between seq1 and seq2.
    """

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
            cost += DIS_COST

        assert cost > 0, stroke
        cost += sum(COSTS.get(annotation, 0) for annotation in stroke.annotations)
        return cost

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

    def get_distance(stroke1: str, stroke2: str) -> int:
        """Calculate the distance between two strokes in a similarity graph.
        Restricted to 0-3.

        :param stroke1: A stroke
        :param stroke2: A second stroke to compute the distance between
        :returns: A distance.
        """

        def in_similarity_graph(distance: int) -> bool:
            similars = get_similar(stroke1, distance)
            similar_strokes = set()
            for tup in similars:
                similar_strokes |= set(tup)
            return stroke2 in similar_strokes

        for distance in range(3):
            if in_similarity_graph(distance):
                return distance
        return 3

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


IT = TypeVar("IT")


def determine_shortest_distance(
    matches: List[Tuple[IT, Match[str]]], func: Callable[[IT, Match[str]], CT]
) -> CT:
    """Determine the minimum value produced by a function on pairs of interpretations
    and matches. Utility for building metrics.
    """
    distance: Optional[CT] = None
    for interp, match in matches:
        new_distance = func(interp, match)
        if distance is None or new_distance < distance:
            distance = new_distance
    assert distance is not None
    return distance


def grascii_standard(result: SearchResult[Interpretation]) -> int:
    """Compute the standard metric for a grascii search.

    :param result: A ``SearchResult``
    :returns: A comparable key representing the distance between an ``Interpretation``
        and a ``Match``
    """

    def distance(interp: Interpretation, match: Match[str]) -> int:
        seq1 = interpretation_to_gsequence(interp)
        seq2 = match_to_gsequence(match)
        return gsequence_distance(seq1, seq2)

    min_start = min(r[1].start("matched_grascii") for r in result.matches)
    shortest_distance = determine_shortest_distance(result.matches, distance)

    # calculate an adjusted distance that will put "off-by-one" matches in the
    # same overall group as exact matches
    adjusted_distance = (
        shortest_distance if shortest_distance % 4 == 0 else shortest_distance - 1
    )

    return adjusted_distance, min_start, shortest_distance, len(result.entry.grascii)


def translation_standard(result: SearchResult[str]) -> Tuple[int, int]:
    """Compute the standard metric for a reverse search.

    :param result: A ``SearchResult``
    :returns: A comparable key representing the distance between a translation
        and a ``Match``
    """

    def distance(s: str, match: Match[str]) -> Tuple[int, int]:
        word_start = match.start("word") - match.end("grascii")
        return word_start, len(match.group("translation"))

    return determine_shortest_distance(result.matches, distance)


def trivial(result: SearchResult[IT]) -> int:
    """The trivial metric.

    :param result: A ``SearchResult``
    :returns: 0
    """
    return 0
