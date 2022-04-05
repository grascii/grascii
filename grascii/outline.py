
from enum import Enum
from typing import Optional

from grascii import grammar
from grascii.parser import Interpretation

class Direction(Enum):

    NORTH = "N"
    EAST = "E"
    SOUTH = "S"
    WEST = "W"
    NORTH_WEST = "NW"
    NORTH_EAST = "NE"
    SOUTH_EAST = "SE"
    SOUTH_WEST = "SW"

class Curve(Enum):

    LINE = 1
    CLOCKWISE = 2
    COUNTER_CLOCKWISE = 3

class Stroke:

    def __init__(self,
                 stroke: str,
                 head_direction: Optional[Direction]=None,
                 head_curve: Optional[Curve]=None,
                 tail_direction: Optional[Direction]=None,
                 tail_curve: Optional[Curve]=None) -> None:
        self.stroke = stroke
        self.head_direction = head_direction
        self.head_curve = head_curve
        self.tail_direction = tail_direction if tail_direction else head_direction
        self.tail_curve = tail_curve if tail_curve else head_curve
        self.annotations: List[str] = []
        self.next: Optional[Stroke] = None
        self.prev: Optional[Stroke] = None
        self.next_consonant: Optional[Stroke] = None
        self.prev_consonant: Optional[Stroke] = None
        self.next_vowel: Optional[Stroke] = None
        self.prev_vowel = None

    def has_annotation(self, annotation: str) -> bool:
        return annotation in self.annotations

    def has_direction_annotation(self) -> bool:
        return self.has_annotation(grammar.LEFT) or self.has_annotation(grammar.RIGHT)

    @classmethod
    def create(cls, stroke: str) -> 'Stroke':
        if stroke in {"K", "G"}:
            return cls(stroke, Direction.EAST, Curve.CLOCKWISE)
        if stroke in {"R", "L", "LD"}:
            return cls(stroke, Direction.EAST, Curve.COUNTER_CLOCKWISE)
        if stroke in {"N", "M", "MN", "MM"}:
            return cls(stroke, Direction.EAST, Curve.LINE)
        if stroke in {"T", "D", "TD", "DT", "DD"}:
            return cls(stroke, Direction.NORTH_EAST, Curve.LINE)
        if stroke in {"P", "B"}:
            return cls(stroke, Direction.SOUTH_WEST, Curve.COUNTER_CLOCKWISE)
        if stroke in {"F", "V"}:
            return cls(stroke, Direction.SOUTH_WEST, Curve.CLOCKWISE)
        if stroke in {"SH", "CH", "J"}:
            return cls(stroke, Direction.SOUTH_WEST, Curve.LINE)
        if stroke in {"NT", "ND", "MT", "MD"}:
            return cls(stroke, Direction.NORTH_EAST, Curve.COUNTER_CLOCKWISE)
        if stroke in {"TN", "DN", "TM", "DM"}:
            return cls(stroke, Direction.NORTH_EAST, Curve.CLOCKWISE)
        if stroke in {"NG", "NK"}:
            return cls(stroke, Direction.SOUTH_EAST, Curve.LINE)
        if stroke in {"DF", "DV", "TV"}:
            return cls(stroke, Direction.NORTH_EAST, Curve.CLOCKWISE, Direction.SOUTH_WEST, Curve.CLOCKWISE)
        if stroke in {"PNT", "PND", "JNT", "JND"}:
            return cls(stroke, Direction.SOUTH_EAST, Curve.COUNTER_CLOCKWISE, Direction.NORTH_EAST, Curve.COUNTER_CLOCKWISE)
        return cls(stroke)


class Outline:

    def __init__(self, interpretation: Interpretation):
        self.first = None
        self.last = None
        needs_next_consonant = []
        needs_next_vowel = []
        prev_stroke = None
        prev_vowel = None
        prev_consonant = None
        for item in interpretation:
            if not isinstance(item, list):
                stroke = Stroke.create(item)
                if prev_stroke:
                    prev_stroke.next = stroke
                else:
                    self.first = stroke
                stroke.prev = prev_stroke
                stroke.prev_consonant = prev_consonant
                stroke.prev_vowel = prev_vowel
                if item in grammar.CONSONANTS:
                    while needs_next_consonant:
                        needs_next_consonant.pop().next_consonant = stroke
                    prev_consonant = stroke
                elif item in grammar.VOWELS:
                    while needs_next_vowel:
                        needs_next_vowel.pop().next_vowel = stroke
                    prev_vowel = stroke
                elif item == grammar.DISJOINER:
                    needs_next_consonant.clear()
                    needs_next_vowel.clear()
                    prev_consonant = None
                    prev_vowel = None
                needs_next_consonant.append(stroke)
                needs_next_vowel.append(stroke)
                self.last = stroke
                prev_stroke = stroke
            else:
                prev_stroke.annotations = item.copy()
        self.infer_directions()

    def infer_directions(self) -> None:

        def set_S_direction_and_curve(stroke):
            assert stroke.has_direction_annotation()
            stroke.head_direction = Direction.SOUTH_WEST
            stroke.tail_direction = Direction.SOUTH_WEST
            if stroke.has_annotation(grammar.RIGHT):
                stroke.head_curve = Curve.CLOCKWISE
                stroke.tail_curve = Curve.CLOCKWISE
            elif stroke.has_annotation(grammar.LEFT):
                stroke.head_curve = Curve.COUNTER_CLOCKWISE
                stroke.tail_curve = Curve.COUNTER_CLOCKWISE

        def set_TH_direction_and_curve(stroke):
            assert stroke.has_direction_annotation()
            stroke.head_direction = Direction.NORTH_EAST
            stroke.tail_direction = Direction.NORTH_EAST
            if stroke.has_annotation(grammar.RIGHT):
                stroke.head_curve = Curve.COUNTER_CLOCKWISE
                stroke.tail_curve = Curve.COUNTER_CLOCKWISE
            elif stroke.has_annotation(grammar.LEFT):
                stroke.head_curve = Curve.CLOCKWISE
                stroke.tail_curve = Curve.CLOCKWISE

        # def check_adjacent_consonant(stroke, adjacent_consonant):
            # 30. When S is joined to a curve, S is written in the same
            # direction as the curve to which it is joined. A circle
            # vowel occuring at the joining does not affect the
            # application of this rule.
            # 31. When S is joined to T, D, N, M, the S is used which forms a
            # sharp angle. A circle vowel occuring at the joining does not
            # affect the application of this rule
            # 32. When S is joined to SH, CH, J the S is used which is written
            # with the clockwise movement
            # if :
                # if consonant.head_curve == Curve.CLOCKWISE:
                    # stroke.annotations.insert(0, grammar.RIGHT)
                # elif consonant.head_curve == Curve.CLOCKWISE

        current_stroke = self.first
        while current_stroke:
            if current_stroke.stroke in {"S", "Z"}:
                if not current_stroke.has_direction_annotation():
                    if current_stroke.next_consonant:
                        if current_stroke.next_consonant.head_curve == Curve.CLOCKWISE:
                            current_stroke.annotations.insert(0, grammar.RIGHT)
                        elif current_stroke.next_consonant.head_curve == Curve.COUNTER_CLOCKWISE:
                            current_stroke.annotations.insert(0, grammar.LEFT)
                        elif current_stroke.next_consonant.head_curve == Curve.LINE:
                            if current_stroke.next_consonant.head_direction == Direction.SOUTH_WEST:
                                current_stroke.annotations.insert(0, grammar.RIGHT)
                            else:
                                current_stroke.annotations.insert(0, grammar.RIGHT)
                        else:
                            current_stroke.annotations.insert(0, grammar.RIGHT)
                    elif current_stroke.prev_consonant:
                        if current_stroke.prev_consonant.tail_curve == Curve.CLOCKWISE:
                            current_stroke.annotations.insert(0, grammar.RIGHT)
                        elif current_stroke.prev_consonant.tail_curve == Curve.COUNTER_CLOCKWISE:
                            current_stroke.annotations.insert(0, grammar.LEFT)
                        elif current_stroke.prev_consonant.tail_curve == Curve.LINE:
                            if current_stroke.prev_consonant.tail_direction == Direction.SOUTH_WEST:
                                current_stroke.annotations.insert(0, grammar.RIGHT)
                            else:
                                current_stroke.annotations.insert(0, grammar.LEFT)
                        else:
                            current_stroke.annotations.insert(0, grammar.RIGHT)
                    else:
                        current_stroke.annotations.insert(0, grammar.RIGHT)
                set_S_direction_and_curve(current_stroke)
            elif current_stroke.stroke == "TH":
                if not current_stroke.has_direction_annotation():
                    current_stroke.annotations.insert(0, grammar.LEFT)
                set_TH_direction_and_curve(current_stroke)

            current_stroke = current_stroke.next

    def __str__(self) -> str:
        builder = []
        current_stroke = self.first
        while current_stroke:
            builder.append(current_stroke.stroke)
            builder += current_stroke.annotations
            current_stroke = current_stroke.next
        return "".join(builder)
