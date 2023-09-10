from __future__ import annotations

from enum import Enum
from typing import List, NamedTuple, Optional

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
    LOOP = 4


class StrokeType(NamedTuple):
    direction: Optional[Direction]
    curve: Optional[Curve]


class Stroke:
    """The building block of an ``Outline``"""

    def __init__(
        self,
        stroke: str,
        head_direction: Optional[Direction] = None,
        head_curve: Optional[Curve] = None,
        tail_direction: Optional[Direction] = None,
        tail_curve: Optional[Curve] = None,
    ) -> None:
        self.stroke = stroke
        self.head_type = StrokeType(head_direction, head_curve)
        td = tail_direction if tail_direction else head_direction
        tc = tail_curve if tail_curve else head_curve
        self.tail_type = StrokeType(td, tc)
        self.annotations: List[str] = []
        self.next: Optional[Stroke] = None
        self.prev: Optional[Stroke] = None
        self.next_consonant: Optional[Stroke] = None
        self.prev_consonant: Optional[Stroke] = None
        self.next_vowel: Optional[Stroke] = None
        self.prev_vowel: Optional[Stroke] = None
        self.next_char: Optional[Stroke] = None
        self.prev_char: Optional[Stroke] = None

    def has_annotation(self, annotation: str) -> bool:
        return annotation in self.annotations

    def has_direction_annotation(self) -> bool:
        return self.has_annotation(grammar.LEFT) or self.has_annotation(grammar.RIGHT)

    def add_annotation(self, annotation: str):
        self.annotations.insert(0, annotation)

    @classmethod
    def create(cls, stroke: str) -> "Stroke":
        if stroke in {"A", "E", "I", "A&'", "A&E"}:
            return cls(stroke, None, Curve.LOOP)
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
        if stroke in {"DF", "DV", "TV", "U"}:
            return cls(
                stroke,
                Direction.NORTH_EAST,
                Curve.CLOCKWISE,
                Direction.SOUTH_WEST,
                Curve.CLOCKWISE,
            )
        if stroke in {"PNT", "PND", "JNT", "JND", "O"}:
            return cls(
                stroke,
                Direction.SOUTH_EAST,
                Curve.COUNTER_CLOCKWISE,
                Direction.NORTH_EAST,
                Curve.COUNTER_CLOCKWISE,
            )
        return cls(stroke)


class Outline:

    """
    An alternative to ``Interpretation`` as a representation of a
    Grascii string. It is structured as a linked list and is better for
    contextual processing of strokes. Outlines infer the directions of
    directional characters and explicitly add direction annotations.
    """

    def __init__(self, interpretation: Interpretation) -> None:
        self.first = None
        self.last = None
        self._build(interpretation)
        self._infer_directions()

    def _build(self, interpretation: Interpretation) -> None:
        needs_next_consonant = []
        needs_next_vowel = []
        needs_next_char = []
        prev_stroke = None
        prev_vowel = None
        prev_consonant = None
        prev_char = None
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
                stroke.prev_char = prev_char
                if item in grammar.CONSONANTS:
                    while needs_next_consonant:
                        needs_next_consonant.pop().next_consonant = stroke
                    prev_consonant = stroke
                    while needs_next_char:
                        needs_next_char.pop().next_char = stroke
                    prev_char = stroke
                elif item in grammar.VOWELS:
                    while needs_next_vowel:
                        needs_next_vowel.pop().next_vowel = stroke
                    prev_vowel = stroke
                    while needs_next_char:
                        needs_next_char.pop().next_char = stroke
                    prev_char = stroke
                elif item == grammar.BOUNDARY or item == grammar.DISJOINER:
                    needs_next_consonant.clear()
                    needs_next_vowel.clear()
                    needs_next_char.clear()
                    prev_consonant = None
                    prev_vowel = None
                    prev_char = None
                needs_next_consonant.append(stroke)
                needs_next_vowel.append(stroke)
                needs_next_char.append(stroke)
                self.last = stroke
                prev_stroke = stroke
            else:
                prev_stroke.annotations = item.copy()

    def _infer_directions(self) -> None:
        """
        Add direction annotations to strokes without explicit directions. This
        method sets the directions of O, U, S/Z, and TH according to the
        following rules from the Preanniversary edition of Gregg Shorthand:

        20. The O-hook is placed on its side before N, M, R, L except when
        preceded by a downward character.

        22. The OO-hook is always placed on its side after N or M; it is also
        placed on its side after K or G when followed by R or L.

        30. When S is joined to a curve, S is written in the same direction as
        the curve to which it is joined. A circle vowel occurring at the joining
        does not affect the application of this rule.

        31. When S is joined to T, D, N, M, the S is used which forms a sharp
        angle. A circle vowel occurring at the joining does not affect the
        application of this rule.

        32. When S is joined to SH, CH, J the S is used which is written with
        the clockwise movement.

        33. In words consisting of S or TH, or both, and a circle vowel, S or TH
        should be written with the clockwise movement.

        34. The clockwise TH is given the preference, but when joined to O, R,
        L the other form is used.

        35. In words beginning with so, the comma S is used.

        Addendums
        =========

        The following addendums are used to address cases not covered by the
        above rules. These rules do not appear explicitly in the Gregg
        manual, but may be inferred, or simply chosen to ease the
        implementation.

        1. When S is between two consonants, its direction is based on the
        preceding character unless there is a syllable break forcing its
        direction to be based on the next character.

        2. When TH is joined to R or L, the under TH is used. A circle vowel
        occurring at the joining does not affect the application of this rule.

        3. In words beginning with IS, the left S is used.

        """

        def set_S_stroke_type(stroke: Stroke) -> None:
            assert stroke.has_direction_annotation()
            if stroke.has_annotation(grammar.RIGHT):
                stroke.head_type = StrokeType(Direction.SOUTH_WEST, Curve.CLOCKWISE)
                stroke.tail_type = StrokeType(Direction.SOUTH_WEST, Curve.CLOCKWISE)
            elif stroke.has_annotation(grammar.LEFT):
                stroke.head_type = StrokeType(
                    Direction.SOUTH_WEST, Curve.COUNTER_CLOCKWISE
                )
                stroke.tail_type = StrokeType(
                    Direction.SOUTH_WEST, Curve.COUNTER_CLOCKWISE
                )

        def set_TH_stroke_type(stroke: Stroke) -> None:
            assert stroke.has_direction_annotation()
            if stroke.has_annotation(grammar.RIGHT):
                stroke.head_type = StrokeType(
                    Direction.NORTH_EAST, Curve.COUNTER_CLOCKWISE
                )
                stroke.tail_type = StrokeType(
                    Direction.NORTH_EAST, Curve.COUNTER_CLOCKWISE
                )
            elif stroke.has_annotation(grammar.LEFT):
                stroke.head_type = StrokeType(Direction.NORTH_EAST, Curve.CLOCKWISE)
                stroke.tail_type = StrokeType(Direction.NORTH_EAST, Curve.CLOCKWISE)

        def set_S_direction(stroke: Stroke) -> None:
            assert stroke.stroke == "S" or stroke.stroke == "Z"
            if (
                not stroke.prev_char
                and stroke.next_char
                and stroke.next_char.stroke == "O"
            ):
                # Rule 35
                stroke.add_annotation(grammar.RIGHT)
                return
            # Addendum 1
            if stroke.prev_char:
                if stroke.prev_char.tail_type.curve == Curve.LOOP:
                    if stroke.prev_consonant:
                        # Rule 30 + 31
                        if set_S_direction_based_on_curves(
                            stroke, stroke.prev_consonant.tail_type, is_before=False
                        ):
                            return
                    elif (
                        stroke.prev_char.stroke == "I"
                        and not stroke.prev_char.prev_char
                    ):
                        # Addendum 3
                        stroke.add_annotation(grammar.LEFT)
                        return
                # Rule 31
                if set_S_direction_based_on_curves(
                    stroke, stroke.prev_char.tail_type, is_before=False
                ):
                    return
            if stroke.next_char:
                if stroke.next_char.head_type.curve == Curve.LOOP:
                    if stroke.next_consonant:
                        # Rule 30 + 31
                        if set_S_direction_based_on_curves(
                            stroke, stroke.next_consonant.head_type, is_before=True
                        ):
                            return
                # Rule 31
                if set_S_direction_based_on_curves(
                    stroke, stroke.next_char.head_type, is_before=True
                ):
                    return

            # Rule 33
            stroke.add_annotation(grammar.RIGHT)

        def set_S_direction_based_on_curves(
            stroke: Stroke, stroke_type: StrokeType, is_before: bool
        ) -> bool:
            if stroke_type.curve == Curve.CLOCKWISE:
                # Rule 30
                stroke.add_annotation(grammar.RIGHT)
                return True
            elif stroke_type.curve == Curve.COUNTER_CLOCKWISE:
                # Rule 30
                stroke.add_annotation(grammar.LEFT)
                return True
            elif stroke_type.curve == Curve.LINE:
                if stroke_type.direction == Direction.SOUTH_WEST:
                    # Rule 32
                    stroke.add_annotation(grammar.RIGHT)
                    return True
                else:
                    # Rule 31
                    if is_before:
                        stroke.add_annotation(grammar.RIGHT)
                    else:
                        stroke.add_annotation(grammar.LEFT)
                    return True
            return False

        def set_TH_direction(stroke: Stroke) -> None:
            assert stroke.stroke == "TH"
            if (stroke.next_char and stroke.next_char.stroke in {"O", "R", "L"}) or (
                stroke.prev_char and stroke.prev_char.stroke in {"O", "R", "L"}
            ):
                # Rule 34
                stroke.add_annotation(grammar.RIGHT)
            elif (
                stroke.next_char
                and stroke.next_char.stroke in {"A", "E", "I", "A&'", "A&E"}
                and stroke.next_consonant
                and stroke.next_consonant.stroke in {"R", "L"}
            ) or (
                stroke.prev_char
                and stroke.prev_char.stroke in {"A", "E", "I", "A&'", "A&E"}
                and stroke.prev_consonant
                and stroke.prev_consonant.stroke in {"R", "L"}
            ):
                # Addendum 2
                stroke.add_annotation(grammar.RIGHT)
            else:
                # Rule 33
                stroke.add_annotation(grammar.LEFT)

        def set_O_direction(stroke: Stroke) -> None:
            assert stroke.stroke == "O"
            if stroke.next_char and stroke.next_char.stroke in {
                "N",
                "M",
                "MN",
                "MM",
                "R",
                "L",
            }:
                if (not stroke.prev) or (
                    not stroke.prev_char
                    or stroke.prev_char.tail_type.direction != Direction.SOUTH_WEST
                ):
                    # Rule 20
                    stroke.add_annotation(grammar.LEFT)

        def set_U_direction(stroke: Stroke) -> None:
            assert stroke.stroke == "U"
            if stroke.prev_char:
                if stroke.prev_char.stroke in {"N", "M", "MN", "MM"}:
                    # Rule 22
                    stroke.add_annotation(grammar.RIGHT)
                elif stroke.prev_char.stroke in {"K", "G"}:
                    if stroke.next_char and stroke.next_char.stroke in {"R", "L"}:
                        # Rule 22
                        stroke.add_annotation(grammar.RIGHT)

        current_stroke = self.first
        while current_stroke:
            if current_stroke.stroke in {"S", "Z"}:
                if not current_stroke.has_direction_annotation():
                    set_S_direction(current_stroke)
                set_S_stroke_type(current_stroke)
            elif current_stroke.stroke == "TH":
                if not current_stroke.has_direction_annotation():
                    set_TH_direction(current_stroke)
                set_TH_stroke_type(current_stroke)
            elif current_stroke.stroke == "O":
                if not current_stroke.has_direction_annotation():
                    set_O_direction(current_stroke)
            elif current_stroke.stroke == "U":
                if not current_stroke.has_direction_annotation():
                    set_U_direction(current_stroke)
            current_stroke = current_stroke.next

    def __str__(self) -> str:
        builder = []
        current_stroke = self.first
        while current_stroke:
            builder.append(current_stroke.stroke)
            builder += current_stroke.annotations
            current_stroke = current_stroke.next
        return "".join(builder)

    def to_interpretation(self) -> Interpretation:
        """Convert this ``Outline`` to an ``Interpretation``"""
        interpretation: Interpretation = []
        current_stroke = self.first
        while current_stroke:
            interpretation.append(current_stroke.stroke)
            if current_stroke.annotations:
                interpretation.append(current_stroke.annotations)
            current_stroke = current_stroke.next
        return interpretation
