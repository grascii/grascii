"""A collection of useful information about the Grascii grammar."""

from __future__ import annotations

_STROKES = "A AU A&' A&E B CH D DD DF DM DN DT DV E EU F G I J JND JNT K L LD \
    M MD MM MN MT N ND NG NK NT O OE P PND PNT R S SH SS T TD TH TM TN TV U V X XS Z"
_VOWELS = "A AU A&' A&E E EU I O OE U"

STROKES = set(_STROKES.split())
"""A set of all valid strokes."""
VOWELS = set(_VOWELS.split())
"""A set of all strokes that represent vowels."""
CONSONANTS = set(STROKES - VOWELS)
"""A set of all strokes that represent consonants."""

HARD_CHARACTERS = {c for c in "ABCDEFGIJKLMNOPRSTUVXZ"}
"""A set of all alphabetic characters that can appear as the first character in a stroke."""
ANNOTATION_CHARACTERS = {c for c in ",.|~_()"}
"""The set of all characters that are annotations."""
ASPIRATE = "'"
"""The character corresponding to the aspirate."""
MEDIUM_SOUND = "."
"""The character corresponding to the medium sound of a standard vowel."""
LONG_SOUND = ","
"""The character corresponding to the long sound of a standard vowel. """
LOOP = "|"
"""The character corresponding to the loop annotation."""
REVERSE = "~"
"""The character corresponding to the reversing annotation."""
WUNDERBAR = "_"
"""The character corresponding to the underbar (W) annotation."""
ING = "'"
"""The character corresponding to the -ing ending."""
LEFT = "("
"""A character corresponding to a direction annotation."""
RIGHT = ")"
"""A character corresponding to a direction annotation."""
OBLIQUE = ","
"""The character corresponding to the oblique annotation."""
DISJOINER = "^"
"""The character corresponding to a disjoiner."""
BOUNDARY = "-"
"""The character corresponding to a boundary."""
INTERSECTION = "\\"
"""The character corresponding to an intersection."""

ALPHABET = set("ABCDEFGIJKLMNOPRSTUVXZ'.,|~_()^-&\\")
"""The set of valid characters in the Grascii language."""

_CIRCLE_VOWEL_ANNOTATIONS: list[tuple[str, ...]] = [
    (REVERSE,),
    (LOOP,),
    (MEDIUM_SOUND, LONG_SOUND),
    (WUNDERBAR,),
]
_CIRCLE_DIPHTHONG_ANNOTATIONS: list[tuple[str, ...]] = [
    (REVERSE,),
    (WUNDERBAR,),
]
_HOOK_DIPHTHONG_ANNOTATIONS: list[tuple[str, ...]] = [(WUNDERBAR,)]
_DIRECTED_CONSONANT_ANNOTATIONS: list[tuple[str, ...]] = [(LEFT, RIGHT)]
_DIRECTED_CONSONANT_ANNOTATIONS_WITH_OBLIQUE: list[tuple[str, ...]] = [
    (LEFT, RIGHT),
    (OBLIQUE,),
]

ANNOTATIONS: dict[str, list[tuple[str, ...]]] = {
    "A": _CIRCLE_VOWEL_ANNOTATIONS,
    "E": _CIRCLE_VOWEL_ANNOTATIONS,
    "O": [(LEFT,), (MEDIUM_SOUND, LONG_SOUND), (WUNDERBAR,)],
    "U": [(RIGHT,), (MEDIUM_SOUND, LONG_SOUND), (WUNDERBAR,)],
    "I": [(REVERSE,), (LOOP,), (WUNDERBAR,)],
    "A&'": _CIRCLE_DIPHTHONG_ANNOTATIONS,
    "A&E": _CIRCLE_DIPHTHONG_ANNOTATIONS,
    "EU": _HOOK_DIPHTHONG_ANNOTATIONS,
    "AU": _HOOK_DIPHTHONG_ANNOTATIONS,
    "OE": _HOOK_DIPHTHONG_ANNOTATIONS,
    "S": _DIRECTED_CONSONANT_ANNOTATIONS_WITH_OBLIQUE,
    "Z": _DIRECTED_CONSONANT_ANNOTATIONS_WITH_OBLIQUE,
    "X": _DIRECTED_CONSONANT_ANNOTATIONS,
    "TH": _DIRECTED_CONSONANT_ANNOTATIONS_WITH_OBLIQUE,
    "SH": [(OBLIQUE,)],
    "SS": _DIRECTED_CONSONANT_ANNOTATIONS,
    "XS": _DIRECTED_CONSONANT_ANNOTATIONS,
}
"""
A dictionary of annotatable strokes to a sequence of acceptable annotations on
the corresponding stroke. The sequence contains tuples of annotations. The
tuples are ordered in the same order they must appear in a strict Grascii
string. The tuples contain mutually exclusive annotations. Ex: ``MEDIUM_SOUND``
and ``LONG_SOUND``
"""
