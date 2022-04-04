
from grascii import grammar
from grascii.parser import Interpretation

class Stroke:

    def __init__(self, stroke: str):
        self.stroke = stroke
        self.annotations: List[str] = []
        self.next: Optional[Stroke] = None
        self.prev: Optional[Stroke] = None
        self.next_consonant: Optional[Stroke] = None
        self.prev_consonant: Optional[Stroke] = None
        self.next_vowel: Optional[Stroke] = None
        self.prev_vowel = None

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
                stroke = Stroke(item)
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
