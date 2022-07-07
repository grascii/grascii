"""A collection of useful information about the grascii grammar.

:var STROKES: A set of all valid strokes.
:var HARD_CHARACTERS: A set of all alphabetic characters that can appear as
    the first character in a stroke.
:var ANNOTATION_CHARACTERS: The set of all characters that are annotations.
:var ASPIRATE: The character corresponding to the aspirate.
:var MEDIUM_SOUND: The character corresponding to the medium sound of a standard
    vowel.
:var LONG_SOUND: The character corresponding to the long sound of a standard
    vowel.
:var LOOP: The character corresponding to the loop annotation.
:var REVERSE: The character corresponding to the reversing annotation.
:var WUNDERBAR: The character corresponding to the underbar (W) annotation.
:var ING: The character corresponding to the -ing ending.
:var LEFT: A character corresponding to a direction annotation.
:var RIGHT: A character corresponding to a direction annotation.
:var OBLIQUE: The character corresponding to the oblique annotation.
:var DISJOINER: The character corresponding to a disjoiner.
:var BOUNDARY: The character corresponding to a boundary.
:var INTERSECTION: The character corresponding to an intersection.
:var ALPHABET: The set of valid characters in the grascii language.
:var ANNOTATIONS: A dictionary of annotatable strokes to a sequence of
    acceptable annotations on the corresponding stroke. The sequece contains
    tuples of annotations. The tuples are ordered in the same order they
    must appear in a strict grascii string. The tuples contain mutually
    exclusive annotations. Ex: MEDIUM_SOUND and LONG_SOUND
"""

from __future__ import annotations

from typing import Dict, List, Tuple

_STROKES = "A AU A&' A&E B CH D DD DF DM DN DT DV E EU F G I J JND JNT K L LD \
    M MD MM MN MT N ND NG NK NT O OE P PND PNT R S SH SS T TD TH TM TN TV U V X XS Z"
_VOWELS = "A AU A&' A&E E EU I O OE U"

STROKES = set(_STROKES.split())
VOWELS = set(_VOWELS.split())
CONSONANTS = set(STROKES - VOWELS)

HARD_CHARACTERS = {c for c in "ABCDEFGIJKLMNOPRSTUVXZ"}
ANNOTATION_CHARACTERS = {c for c in ",.|~_()"}
ASPIRATE = "'"
MEDIUM_SOUND = "."
LONG_SOUND = ","
LOOP = "|"
REVERSE = "~"
WUNDERBAR = "_"
ING = "'"
LEFT = "("
RIGHT = ")"
OBLIQUE = ","
DISJOINER = "^"
BOUNDARY = "-"
INTERSECTION = "\\"

ALPHABET = set("ABCDEFGIJKLMNOPRSTUVXZ'.,|~_()^-&\\")

_CIRCLE_VOWEL_ANNOTATIONS: List[Tuple[str, ...]] = [
    (REVERSE,),
    (LOOP,),
    (MEDIUM_SOUND, LONG_SOUND),
    (WUNDERBAR,),
]
_CIRCLE_DIPHTHONG_ANNOTATIONS: List[Tuple[str, ...]] = [
    (REVERSE,),
    (LOOP,),
    (WUNDERBAR,),
]
_HOOK_DIPHTHONG_ANNOTATIONS: List[Tuple[str, ...]] = [(WUNDERBAR,)]
_DIRECTED_CONSONANT_ANNOTATIONS: List[Tuple[str, ...]] = [(LEFT, RIGHT), (OBLIQUE,)]

ANNOTATIONS: Dict[str, List[Tuple[str, ...]]] = {
    "A": _CIRCLE_VOWEL_ANNOTATIONS,
    "E": _CIRCLE_VOWEL_ANNOTATIONS,
    "O": [(LEFT,), (MEDIUM_SOUND, LONG_SOUND), (WUNDERBAR,)],
    "U": [(RIGHT,), (MEDIUM_SOUND, LONG_SOUND), (WUNDERBAR,)],
    "I": _CIRCLE_DIPHTHONG_ANNOTATIONS,
    "A&'": _CIRCLE_DIPHTHONG_ANNOTATIONS,
    "A&E": _CIRCLE_DIPHTHONG_ANNOTATIONS,
    "EU": _HOOK_DIPHTHONG_ANNOTATIONS,
    "AU": _HOOK_DIPHTHONG_ANNOTATIONS,
    "OE": _HOOK_DIPHTHONG_ANNOTATIONS,
    "S": _DIRECTED_CONSONANT_ANNOTATIONS,
    "Z": _DIRECTED_CONSONANT_ANNOTATIONS,
    "TH": _DIRECTED_CONSONANT_ANNOTATIONS,
    "SH": [(OBLIQUE,)],
}
